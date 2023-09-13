# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
import scipy.stats as stats
from ultron.sentry.api import *
from seleya import SurfaceDBAPI
from seleya.utilities.kd_logger import kd_logger
import pdb


class Glassdoor(object):

    def __init__(self, industry_code):
        self._industry_code = industry_code
        self._mapping_dict = {
            'NO_OPINION': 0,
            'NEGATIVE': -1,
            'POSITIVE': 1,
            'NEUTRAL': 0,
            'APPROVE': 1,
            'DISAPPROVE': -1
        }
        self._probability_cols = [
            'ratingBusinessOutlook', 'ratingRecommendToFriend', 'ratingCeo'
        ]
        self._mean_cols = [
            'ratingWorkLifeBalance', 'ratingCultureAndValues',
            'ratingSeniorLeadership', 'ratingCareerOpportunities',
            'ratingOverall', 'ratingCompensationAndBenefits',
            'ratingDiversityAndInclusion'
        ]
        self._factors_sets = self._probability_cols + self._mean_cols

    def _fetch_overview(self, codes):
        kd_logger.info('Fetching glassdoor overview data...')
        gd_overview_data = SurfaceDBAPI.GDOveriew().fetch(
            codes=codes, columns=['code', 'cid'])
        gd_overview_data = gd_overview_data[['cid', 'code'
                                             ]].drop_duplicates(subset=['cid'])
        return gd_overview_data

    def _fetch_reviews(self, begin_date, end_date, cids):
        kd_logger.info('Fetching glassdoor reviews data...')
        columns = ['id', 'cid', 'reviewId', 'reviewDateTime'
                   ] + self._factors_sets
        gd_reviews_data = SurfaceDBAPI.GDReviewsBase().fetch(
            begin_date=begin_date,
            end_date=end_date,
            cids=cids,
            columns=columns)
        if gd_reviews_data.empty:
            return None

        for col in self._probability_cols:
            gd_reviews_data[col] = gd_reviews_data[col].apply(
                lambda x: np.nan if x is None else self._mapping_dict[x])
        gd_reviews_data['reviewDateTime'] = pd.to_datetime(
            gd_reviews_data['reviewDateTime'])
        gd_reviews_data['date'] = pd.to_datetime(
            gd_reviews_data['reviewDateTime']).dt.strftime('%Y-12-31')
        return gd_reviews_data

    def prepare_data(self, begin_date=None, end_date=None):
        kd_logger.info('Fetching industry data...')
        industry_data = SurfaceDBAPI.Industry().fetch(
            industry_code=self._industry_code,
            columns=['code', 'industry_id1'])
        if industry_data.empty:
            kd_logger.error('Industry data is empty')
            return None

        codes = industry_data['code'].unique().tolist()
        gd_overview_data = self._fetch_overview(codes)
        if gd_overview_data.empty:
            kd_logger.error('Glassdoor overview data is empty')
            return None

        cids = gd_overview_data['cid'].unique().tolist()
        gd_reviews_data = self._fetch_reviews(begin_date=begin_date,
                                              end_date=end_date,
                                              cids=cids)
        if gd_reviews_data.empty:
            kd_logger.error('Glassdoor reviews data is empty')
            return None

        kd_logger.info('merging glassdoor data...')
        total_data = gd_reviews_data.merge(gd_overview_data,
                                           on=['cid'],
                                           how='left')
        return total_data

    def _transform_raw(self, mean_data):
        # save the raw average scores for UI use
        raw_data = mean_data.reset_index().set_index([
            'date',
            'code',
        ]).stack().reset_index().rename(columns={
            'level_2': 'name',
            0: 'value'
        })
        raw_data['date'] = pd.to_datetime(
            raw_data['date']).dt.strftime('%Y-%m-%d')
        raw_data['industry'] = self._industry_code
        return raw_data

    def _blom_score(self, values_series, threshold=0.9):
        idx = values_series.index.droplevel(level=0)
        coverage = values_series.isna().sum() / len(values_series)
        if coverage > threshold:
            scores = [np.nan for _ in range(len(values_series))]
        else:
            ranks = stats.mstats.rankdata(np.ma.masked_invalid(values_series))
            ranks[ranks == 0] = np.nan
            n = ranks.size - np.count_nonzero(np.isnan(ranks))
            scores = stats.norm.ppf((ranks - 3. / 8) / (n + 0.25))
        scores = pd.Series(data=scores, index=idx)
        return scores

    def _distribute(self, mean_data):
        dt = mean_data.set_index(['date', 'code', 'name'])['value']
        res = []
        _ = dt.unstack().apply(lambda x: self._percentile(x, res), axis=0)
        dt = pd.concat(res, axis=1)
        dt['industry'] = self._industry_code
        return dt

    def _percentile(self, x, res):
        name = str(x.name)
        x = x.dropna()
        rt = CSQuantiles(name).transform(x.reset_index().set_index('date'),
                                         name=name,
                                         category_field='code')
        res.append(rt.reset_index().set_index(['date', 'code']))

    def _calculate_distribute(self, mean_data):
        kd_logger.info('calculating distribute...')
        mean_data['date'] = pd.to_datetime(mean_data['date'])
        dist_data = self._distribute(mean_data=mean_data)
        if dist_data is None or dist_data.empty:
            kd_logger.error('distribute data is empty')
            return None
        dist_data = dist_data.reset_index().set_index(
            ['date', 'code', 'industry']).stack().reset_index()
        dist_data = dist_data.rename(columns={'level_3': 'name', 0: 'value'})
        dist_data['date'] = dist_data['date'].dt.strftime('%Y-%m-%d')
        return dist_data

    def _format_mean(self, mean_data):
        mean_data['industry'] = self._industry_code
        mean_data['date'] = mean_data['date'].dt.strftime('%Y-%m-%d')
        return mean_data

    def calculate_result(self, total_data, threshold=0.9):
        # aggregate means by year and cid
        mean_data = total_data.groupby(['date', 'code']).mean()
        raw_data = self._transform_raw(mean_data=mean_data)
        if raw_data is None or raw_data.empty:
            kd_logger.error('raw data is empty')
            return None

        kd_logger.info('calculating blom score...')
        for col_name in self._factors_sets:
            col_score = mean_data.sort_values(by=['date', 'code']).groupby(
                by=['date']).apply(lambda x: self._blom_score(
                    x[col_name], threshold=threshold))
            if isinstance(col_score, pd.DataFrame):
                col_score = col_score.stack()
            col_score.name = col_name
            mean_data[col_name] = col_score
        mean_data = mean_data.stack().reset_index().rename(columns={
            'level_2': 'name',
            0: 'value'
        })

        dist_data = self._calculate_distribute(mean_data=mean_data)
        if dist_data is None or dist_data.empty:
            kd_logger.error('distribute data is empty')
            return None

        kd_logger.info('calculating success...')
        return raw_data, self._format_mean(mean_data), dist_data

    def run(self, begin_date, end_date, threshold=0.9):
        total_data = self.prepare_data(begin_date, end_date)
        if total_data is None or total_data.empty:
            kd_logger.error('Glassdoor data is empty')
            return None
        return self.calculate_result(total_data=total_data,
                                     threshold=threshold)
