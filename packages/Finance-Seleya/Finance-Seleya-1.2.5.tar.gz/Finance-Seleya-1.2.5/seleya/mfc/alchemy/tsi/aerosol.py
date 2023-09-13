# -*- coding: utf-8 -*-
import pdb
import numpy as np
import pandas as pd
from seleya import SurfaceDBAPI
from seleya import SurfaceMGAPI
from seleya.utilities.kd_logger import kd_logger


class Aerosol(object):

    def __init__(self, sector_code, region='All'):
        self._sector_code = sector_code
        self._region = region

    def prepare_data(self, begin_date=None, end_date=None):
        sector_data = SurfaceDBAPI.Industry().fetch_sector(
            sector_code=self._sector_code,
            columns=['code', 'industry_id1', 'sector_id'])
        if sector_data.empty:
            kd_logger.error('sector data is empty')
            return None
        kd_logger.info('fetching {0} {1} feature data...'.format(
            self._region, self._sector_code))
        feature_data = SurfaceDBAPI.FeatureImportance().fetch_factor_range(
            region=self._region,
            sector_id=self._sector_code,
            columns=['factor', 'sector_id', 'importance', 'classification'])
        kd_logger.info('fetching  {0}  {1} qrank data...'.format(
            self._region, self._sector_code))

        gd_factors_name = feature_data[feature_data['classification'] ==
                                       'employee'].factor.unique().tolist()
        metrics_factors_name = feature_data[
            feature_data['classification'] != 'employee'].factor.unique(
            ).tolist()
        codes = sector_data['code'].unique().tolist()

        kd_logger.info('fetching {0}  {1}  company data...'.format(
            self._region, self._sector_code))
        company_data = SurfaceDBAPI.Company().fetch(
            codes=codes, columns=['code', 'region', 'mkt_cap'])

        kd_logger.info('fetching {0}  {1} glassdoor qrank...'.format(
            self._region, self._sector_code))

        gd_qrank_data = SurfaceMGAPI.GDQrankDist().fetch(
            codes=codes,
            begin_date=begin_date,
            end_date=end_date,
            name=gd_factors_name,
            columns=['code', 'date', 'name', 'value', 'industry'])

        kd_logger.info('merge {0}  {1}  qrank...'.format(
            self._region, self._sector_code))
        material_metrics_qrank_data = SurfaceMGAPI.GicDistLevel1().fetch(
            codes=codes,
            begin_date=begin_date,
            end_date=end_date,
            name=metrics_factors_name,
            columns=['code', 'date', 'name', 'value', 'industry'])

        non_metrics_qrank_data = SurfaceMGAPI.NonGicDistLevel1().fetch(
            codes=codes,
            begin_date=begin_date,
            end_date=end_date,
            name=metrics_factors_name,
            columns=['code', 'date', 'name', 'value', 'industry'])
        metrics_qrank_data = pd.concat(
            [material_metrics_qrank_data, non_metrics_qrank_data],
            ignore_index=True)

        metrics_qrank_data = metrics_qrank_data.pivot_table(
            values='value', index=['code', 'date', 'industry'],
            columns='name').reset_index().drop(columns=['industry'])

        gd_qrank_data = gd_qrank_data.pivot_table(
            values='value', index=['code', 'date', 'industry'],
            columns='name').reset_index().drop(columns=['industry'])

        qrank_data = metrics_qrank_data.merge(gd_qrank_data,
                                              on=['code', 'date'],
                                              how='outer')
        basic_infos = company_data.merge(sector_data, on=['code'], how='left')

        total_data = basic_infos.merge(qrank_data, on=['code'])

        total_data = total_data.drop_duplicates(
            subset=['code', 'date'], keep='first').reset_index(drop=True)
        return total_data, feature_data

    def filter_factors(self, total_data, columns, threshold=0.4):

        def _coverage_seq(factors_data, factor_name):
            coverage = factors_data.sort_values(
                by=['date', 'industry_id1']).groupby([
                    'date', 'industry_id1'
                ]).apply(lambda x: 1 - np.isnan(x[factor_name].values).mean())
            coverage.name = factor_name
            return coverage

        res = []
        for col in columns:
            rts = _coverage_seq(
                total_data.copy()[['date', 'industry_id1', col]], col)
            res.append(rts)
        coverage = pd.concat(res, axis=1).stack()
        coverage = coverage[coverage >= threshold]
        return coverage.reset_index().rename(columns={
            'level_2': 'column_name',
            0: 'coverage'
        })

    def calculate_result(self, total_data, feature_data, threshold, k=10):
        columns = [
            col for col in feature_data.factor.unique().tolist()
            if col in total_data.columns
        ]

        kd_logger.info('{0}  {1}  calc coverage ...'.format(
            self._region, self._sector_code))
        coverage_data = self.filter_factors(total_data, columns, threshold)
        coverage_data = coverage_data.merge(
            feature_data.rename(columns={'factor': 'column_name'}),
            on=['column_name'])
        index_columns = [
            'code', 'region', 'mkt_cap', 'industry_id1', 'sector_id', 'date'
        ]
        clean_data = total_data[index_columns +
                                coverage_data.column_name.unique().tolist()]
        ### 每个行业的 factor 权重
        kd_logger.info('{0}  {1}  calc weighted ...'.format(
            self._region, self._sector_code))
        weighted = coverage_data.sort_values(
            by=['date', 'importance'], ascending=False).set_index([
                'date', 'industry_id1'
            ])[['column_name',
                'importance']].groupby(level=['date', 'industry_id1']).apply(
                    lambda x: x[:k].set_index('column_name')['importance'] / x[
                        0:k].set_index('column_name')['importance'].sum())
        '''
        weighted = coverage_data.set_index(['date', 'industry_id1'])[[
            'column_name', 'importance'
        ]].groupby(level=['date', 'industry_id1']).apply(
            lambda x: x.set_index('column_name')['importance'] / x.set_index(
                'column_name')['importance'].sum())
        '''
        weighted = weighted.reset_index()
        ### 计算公司在每个行业的分数
        ### (facotr * 权重).sum()
        res = {}
        for industry in weighted.industry_id1.unique().tolist():
            kd_logger.info('{0} {1} {2} calc company score ...'.format(
                self._region, self._sector_code, industry))

            industry_weighted = weighted[weighted['industry_id1'] == industry]
            factor_columns = industry_weighted.column_name.unique().tolist()
            clean_dt = clean_data[clean_data['industry_id1'] == industry]
            industry_weighted = industry_weighted.set_index(
                ['date', 'column_name'])['importance'].unstack()
            industry_data = clean_dt[['date', 'code'] + factor_columns].merge(
                industry_weighted, on=['date'], suffixes=('', '_w'))
            w_list = [f + '_w' for f in factor_columns]
            industry_data[factor_columns] = (
                (2 * industry_data[factor_columns].values - 1) *
                industry_data[w_list].values * 5)

            industry_data['score'] = industry_data[factor_columns].fillna(
                0).sum(axis=1)
            industry_data['industry'] = industry

            res[industry] = industry_data.drop(w_list, axis=1)
        return res

    def run(self, begin_date, end_date, threshold=0.5):
        total_data, feature_data = self.prepare_data(begin_date=begin_date,
                                                     end_date=end_date)

        return self.calculate_result(total_data,
                                     feature_data,
                                     threshold=threshold)
