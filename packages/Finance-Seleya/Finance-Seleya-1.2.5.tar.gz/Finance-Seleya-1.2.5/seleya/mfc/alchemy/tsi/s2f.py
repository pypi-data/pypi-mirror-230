import warnings
import json
import os
import pdb
import numpy as np
import pandas as pd
from pandas import CategoricalDtype

from seleya import SurfaceDBAPI
from seleya import SurfaceMGAPI
from seleya import DBAPI
from seleya.Toolset import blob_service
from seleya.utilities.kd_logger import kd_logger
from joblib import load

# supress sklearn warnings
warnings.filterwarnings(action='ignore', category=UserWarning)


class S2F(object):

    def __init__(self, sector_code, target_original='revenue_total_employees'):
        self._local_dir = os.environ['local_dir']
        self._db_engine = DBAPI.FetchEngine.create_engine('sly')
        self._blob_svc = blob_service.BlobService()
        self._sector_code = sector_code
        self._probability_cols = [
            'ratingBusinessOutlook', 'ratingRecommendToFriend', 'ratingCeo'
        ]
        self._mean_cols = [
            'ratingWorkLifeBalance', 'ratingCultureAndValues',
            'ratingSeniorLeadership', 'ratingCareerOpportunities',
            'ratingOverall', 'ratingCompensationAndBenefits',
            'ratingDiversityAndInclusion'
        ]
        self._gd_cols = self._probability_cols + self._mean_cols
        self._iso_ems_score_map = {
            'No': 0,
            'ISO 14000': 1,
            'EMS': 1,
            'Both': 2
        }
        self._target_original_list = [
            'return_on_assets', 'return_on_equity', 'debt_to_equity',
            'revenue_total_employees', 'free_cash_flow_margin'
        ]
        self._target_original = target_original
        if target_original not in self._target_original_list:
            raise ValueError(
                f"target_original must be one of {self._target_original_list}")
        self._target_list = []
        for offset in range(1, 4):
            self._target_list.append(
                f"{self._target_original}_{offset}y_change")
        self._region_map = {
            'Europe': 0,
            'Americas': 1,
            'Oceania': 3,
            'Asia': 4,
            'Africa': 5
        }
        self._inverse_region_map = {v: k for k, v in self._region_map.items()}
        self._region_type = CategoricalDtype(
            categories=['Europe', 'Americas', 'Oceania', 'Asia', 'Africa'],
            ordered=True)

    def prepare_data(self, begin_date, end_date):
        kd_logger.info('Fetching sector data')
        sector_peers = SurfaceDBAPI.Sector().fetch(
            sector_code=self._sector_code, columns=['code', 'sector_id'])
        if sector_peers.empty:
            kd_logger.error('Sector data is empty')
            return None
        kd_logger.info(
            f"{self._sector_code} has {len(sector_peers)} companies")
        codes = sector_peers['code'].unique().tolist()

        sasb_sector = SurfaceDBAPI.SASBMapdom().fetch_sector(
            sector_code=self._sector_code, columns=['column_name', 'trcode'])
        sasb_sector = sasb_sector.dropna(subset=['trcode']).drop_duplicates(
            subset=['trcode'])
        sasb_sector = sasb_sector[~sasb_sector['trcode'].str.startswith('TR.F.'
                                                                        )]
        kd_logger.info(
            f"{self._sector_code} has {len(sasb_sector)} material metrics")

        names = DBAPI.ESGMetricsDetailFactory(self._db_engine).name()
        clause_list = [
            names.index_metric == 1,
            names.trcode.in_(sasb_sector['trcode'].tolist())
        ]
        esg_details_sector = DBAPI.ESGMetricsDetailFactory(
            self._db_engine).customize(
                clause_list=clause_list,
                columns=['trcode', 'category', 'column_name', 'polarity'])
        metrics_list = esg_details_sector['column_name'].unique().tolist()
        kd_logger.info(f"{self._sector_code} esg metrics detail pulled")

        metrics_data = DBAPI.SASBMetricsFactory(self._db_engine).result(
            codes=codes,
            column_name=esg_details_sector['column_name'].tolist(),
            begin_date=begin_date,
            end_date=end_date).drop(['quarter'], axis=1)

        company_data = DBAPI.CompanyFactory(self._db_engine).result(
            codes=codes,
            primary=[1],
            columns=['code', 'region', 'mkt_cap'],
            key='code')

        metrics_data['date'] = metrics_data['date'].apply(
            lambda x: x.strftime('%Y-%m-%d'))
        metrics_data = metrics_data.sort_values(by=['code', 'date'],
                                                ascending=[True, True])
        metrics_data.groupby(['code', 'date']).fillna(method='ffill',
                                                      limit=2,
                                                      inplace=True)

        # metrics_data = metrics_data.dropna(axis=1,
        #                                    thresh=(0.10 * len(metrics_data)))
        metrics_data = metrics_data.dropna(
            axis=0, thresh=2 + ((len(metrics_data.columns) - 2) * 0.2))
        metrics_list = [x for x in metrics_list if x in metrics_data.columns]
        kd_logger.info(f"{self._sector_code} metrics, company data pulled")

        gd_data = SurfaceMGAPI.GDQrankRaw().fetch(
            columns=['date', 'code', 'name', 'value'], codes=codes)
        kd_logger.info(f"{self._sector_code} GD data pulled")

        gd_data = gd_data.pivot_table(values='value',
                                      index=['code', 'date'],
                                      columns='name',
                                      aggfunc='first').reset_index()

        total_data = metrics_data.merge(gd_data,
                                        how='left',
                                        on=['code', 'date'])
        if 'iso_14000_or_ems' in total_data.columns.tolist():
            total_data['iso_14000_or_ems'] = total_data[
                'iso_14000_or_ems'].map(self._iso_ems_score_map)
        total_data = total_data.sort_values(by=['code', 'date'],
                                            ascending=[True, True])

        transform_list = metrics_list + self._gd_cols

        for factor in transform_list:
            for offset in range(1, 4):
                total_data[f"{factor}_{offset}y_change"] = total_data.groupby(
                    ['code'])[factor].pct_change(offset)
        kd_logger.info(f"{self._sector_code} transformed data shift")
        total_data = total_data.replace([np.inf, -np.inf, 'None'], np.nan)

        return total_data, company_data

    def calculate_result(self, total_data, company_data, prediction_from,
                         prediction_to, model_path):
        result_dict = {}
        for target in self._target_list:
            kd_logger.info(f"{self._sector_code} downloading {target} model")
            local_dir = f'{self._local_dir}/{self._sector_code}/{target}/'
            remote_dir = f'{model_path}/{self._sector_code}/{target}/'
            try:
                self._blob_svc.download_file(
                    container_name='model',
                    local_file_name=f"{local_dir}model.joblib",
                    remote_file_name=f"{remote_dir}model.joblib",
                    is_refresh=False)
                self._blob_svc.download_file(
                    container_name='model',
                    local_file_name=f"{local_dir}imputer.joblib",
                    remote_file_name=f"{remote_dir}imputer.joblib",
                    is_refresh=False)
            except Exception as e:
                kd_logger.error(
                    f"{self._sector_code} {target} model download failed")
                continue

            current_data = total_data.copy(deep=True)
            current_data = current_data.merge(company_data,
                                              how='left',
                                              on='code')
            current_data = current_data.dropna(subset=['region', 'mkt_cap'],
                                               axis=0)
            current_data['region'] = current_data['region'].map(
                self._region_map)
            current_data.columns = current_data.columns.astype(str)

            imputer = load(f"{local_dir}imputer.joblib")
            current_data = current_data.set_index(['code', 'date'])
            esg_imputer_cols = imputer.feature_names_in_
            current_data[esg_imputer_cols] = imputer.transform(
                current_data[esg_imputer_cols])
            current_data = current_data.reset_index()
            current_data['region'] = current_data['region'].map(
                self._inverse_region_map)
            current_data['region'] = current_data['region'].astype(
                self._region_type)

            # only calculate for the recent two years
            current_data = current_data[
                (current_data['date'] > prediction_from)
                & (current_data['date'] < prediction_to)]

            ebm = load(f"{local_dir}model.joblib")
            # get the prediction results and individual contributions
            predict_and_contrib = ebm.predict_and_contrib(current_data,
                                                          output='labels')
            # predictions = np.argmax(predict_and_contrib[0], axis=1)
            """
            to interpret the contribution, we can calculate the probability of each class following the formula:
            scores = contribution.sum(axis=1) + intercept
            from sklearn.utils.extmath import softmax
            softmax(np.c_[np.zeros(scores.shape), scores])

            alternatively, if we only want the label itself:
            scores = contribution.sum(axis=1) + intercept
            scores = np.c_[np.zeros(scores.shape), scores]
            np.argmax(scores, axis=1)
            """
            predictions = predict_and_contrib[0]
            intercept_ = ebm.intercept_[0]
            contribution = pd.DataFrame(predict_and_contrib[1],
                                        columns=ebm.feature_names_in_)
            contribution['prediction'] = predictions.tolist()
            contribution['intercept'] = intercept_
            contribution['code'] = current_data['code'].tolist()
            contribution['date'] = current_data['date'].tolist()
            contribution['sector'] = self._sector_code
            contribution['target'] = target

            result_dict[target] = contribution
            kd_logger.info(
                f"{self._sector_code} {target} model explaining done")
        return result_dict

    def run(self,
            begin_date='2014-01-01',
            end_date='2023-01-01',
            prediction_from='2021-01-01',
            prediction_to='2023-01-01',
            model_path='S2F/run03'):
        """
        Run the S2F model
        begin_date: the start date of the metrics and gd data fetching
        end_date: the end date of the metrics and gd data fetching
        prediction_from: the start date range for the prediction
        prediction_to: the end date range for the prediction
        """
        total_data, company_data = self.prepare_data(begin_date, end_date)
        result_dict = self.calculate_result(total_data,
                                            company_data,
                                            prediction_from,
                                            prediction_to,
                                            model_path=model_path)
        return result_dict
