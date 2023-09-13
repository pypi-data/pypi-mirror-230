# -*- coding: utf-8 -*-
import pdb
import pandas as pd
import numpy as np
from seleya.utilities.kd_logger import kd_logger
from seleya import SurfaceDBAPI


class CO2(object):

    def co2_columns(self):
        """ Return the columns that contain CO2 emissions """
        return [
            'code', 'date', 'reduction_percent', 'target_type',
            'intensity_metric', 'base_year', 'target_year', 'base_year_value',
            'co2_emissions_scope1', 'co2_emissions_scope2',
            'co2_emissions_scope3'
        ]

    def company_score_columns(self):
        """ Return the columns that contain CO2 emissions """
        return [
            'code', 'time_frame', 'scope', 'target_type', 'intensity_metric',
            'reduction_ambition', 'base_year', 'end_year', 'sbti_validated',
            'annual_reduction_rate', 'param', 'intercept', 'temperature_score',
            'temperature_results'
        ]

    def emission_columns(self):
        """ Return the columns that contain CO2 emissions """
        return [
            'total_co2_emissions', 'co2_emissions_scope1',
            'co2_emissions_scope2', 'co2_emissions_scope3'
        ]

    def fetch_company_targets(self, codes, begin_date, end_date):
        target_data = SurfaceDBAPI.CO2EmissionTarget().fetch(
            codes=codes,
            begin_date=begin_date,
            end_date=end_date,
            columns=self.co2_columns())
        target_data['intensity_metric'] = target_data[
            'intensity_metric'].astype(str)
        return target_data

    def fetch_company_emissions(self, codes, begin_date, end_date):
        emission_data = SurfaceDBAPI.Metrics().fetch(
            codes=codes,
            begin_date=begin_date,
            end_date=end_date,
            columns=self.emission_columns())
        emission_data = emission_data.replace(to_replace=[None], value=np.nan)
        emission_data['FY'] = emission_data['date'].apply(
            lambda x: int(x.year))
        return emission_data

    def industry_scores(self, codes):
        industry_data = SurfaceDBAPI.Industry().extract(
            codes=codes, columns=['code', 'industry_id1'])
        industry_data.rename(columns={'industry_id1': 'industry'},
                             inplace=True)

        scores = SurfaceDBAPI.EmissionScoreAverage().fetch(
            industry=industry_data.industry.unique().tolist())
        scores['time_frame'] = scores['time_frame'].str.upper()
        scores = scores.rename(
            columns={'temperature_score': 'industry_average_score'})
        scores = scores.merge(industry_data, how='left', on='industry')
        target_scores = scores[scores['scope'] != 'S1+S2+S3']
        company_scores = scores[scores['scope'] == 'S1+S2+S3'].drop(
            columns=['scope'])
        return target_scores, company_scores

    def company_scores(self, codes):
        scores = SurfaceDBAPI.CompanyEmissionTemperature().fetch(
            codes=codes, columns=self.company_score_columns())
        scores = scores.replace(to_replace=[None], value=np.nan)
        scores['target_type'] = scores['target_type'].str.capitalize()
        scores['time_frame'] = scores['time_frame'].str.upper()
        scores = scores.rename(columns={
            'end_year': 'target_year',
            'sbti_validated': 'sbti_flag'
        })
        target_scores = scores[scores['scope'] != 'S1+S2+S3'].drop_duplicates(
            subset=[
                'code', 'time_frame', 'scope', 'target_type', 'base_year',
                'target_year'
            ],
            keep='last').drop(
                columns=['annual_reduction_rate', 'intensity_metric'])
        company_scores = scores[scores['scope'] == 'S1+S2+S3'].drop_duplicates(
            subset=['code', 'time_frame', 'scope'], keep='last')
        return target_scores, company_scores[[
            'code', 'time_frame', 'temperature_score', 'temperature_results'
        ]]

    def convert_scope(self, row):
        """ Convert the scope to a number """
        result = []
        if row['co2_emissions_scope1'] == 1:
            result.append('1')
        if row['co2_emissions_scope2'] == 1:
            result.append('2')
        if row['co2_emissions_scope3'] == 1:
            result.append('3')
        return 'CO2e Emissions Scope ' + ', '.join(result)

    def convert_scope_SBTi(self, row):
        """ Convert the scope to a number """
        result = ''
        if row['co2_emissions_scope1'] == 1:
            result += '+S1'
        if row['co2_emissions_scope2'] == 1:
            result += '+S2'
        if row['co2_emissions_scope3'] == 1:
            result += '+S3'
        return result[1:]

    def calc_year_values(self, row, emission_data):
        """" Calculate the year values for the given row """

        def calc_value(row, scope_mask):
            year_data = row.dropna().to_dict()
            if len([x for x in scope_mask.keys() if x not in year_data.keys()
                    ]) > 0:
                if set(scope_mask.keys()) == set([
                        'co2_emissions_scope1', 'co2_emissions_scope2'
                ]) and 'total_co2_emissions' in year_data:
                    return year_data['total_co2_emissions']
                if set(scope_mask.keys()) == set(
                    [
                        'co2_emissions_scope1', 'co2_emissions_scope2',
                        'co2_emissions_scope3'
                    ]
                ) and 'total_co2_emissions' in year_data and 'co2_emissions_scope3' in year_data:
                    return year_data['total_co2_emissions'] + year_data[
                        'co2_emissions_scope3']
                return np.nan
            result = 0
            for x in scope_mask.keys():
                result += year_data[x]
            return result

        scope_mask = row[[
            'co2_emissions_scope1', 'co2_emissions_scope2',
            'co2_emissions_scope3'
        ]]
        scope_mask = scope_mask[scope_mask == 1].to_dict()
        emission_data['emission_value_db'] = emission_data.apply(
            lambda x: calc_value(x, scope_mask), axis=1)
        return emission_data

    def type_unit_mapping(self, target_type, intensity_metric):
        if target_type == 'Absolute':
            return 'T', 'T = Tonnes'
        elif intensity_metric == 'Revenue':
            return 'T/USD mm', 'T/USD mm = Tonnes per USD million'
        elif intensity_metric == 'Product':
            return 'T/Product', 'T/Product = Tonnes per unit of product sales'
        elif intensity_metric == 'Cement':
            return 'T/Cement', 'T/Cement = Tonnes per unit of cement production'
        elif intensity_metric == 'Oil':
            return 'T/Oil', 'T/Oil = Tonnes per unit of oil production'
        elif intensity_metric == 'Steel':
            return 'T/Steel', 'T/Steel = Tonnes per unit of steel production'
        elif intensity_metric == 'Aluminum':
            return 'T/Aluminum', 'T/Aluminum = Tonnes per unit of aluminum production'
        elif intensity_metric == 'Power':
            return 'T/Power', 'T/Power = Tonnes per unit of power generated'
        else:
            return 'T/Other', 'T/Other = Tonnes per unit not recognized by SBTi'

    def update_target(self, idx, target, target_data, emission_history):
        """ Update the target with the calculated values """
        if len(emission_history) == 0 or target['target_type'] != 'Absolute':
            return

        base_year = target['base_year']
        target_year = target['target_year']
        base_year_value = target['base_year_value']
        reduction_percent = target['reduction_percent']\
            if pd.isna(target['reduction_ambition']) else target['reduction_ambition']

        # 如果数据库里有base year的数据， 用这个
        if base_year in emission_history['FY'].tolist():
            base_year_value = emission_history[
                emission_history['FY'] ==
                base_year].squeeze()['emission_value_db']
        target_data.at[idx, 'base_year_value'] = base_year_value

        base_year_value = 0 if base_year_value is None else base_year_value
        target_year_emission = base_year_value * (1 - reduction_percent)

        current_year = int(emission_history['FY'].iloc[-1])
        current_emission = emission_history['emission_value_db'].iloc[-1]
        total_changes = target_year_emission / current_emission - 1
        target_data.at[idx, 'target_year_emission'] = target_year_emission
        target_data.at[idx, 'total_changes'] = total_changes

        cagr = pow(target_year_emission / current_emission, 1.0 /
                   (target_year - current_year)
                   ) - 1 if target_year > current_year else np.nan
        target_data.at[idx, 'cagr'] = cagr
        target_data.at[idx, 'current_year'] = current_year
        reduction_amount = target_year_emission - base_year_value
        real_progress = (current_emission - base_year_value) / reduction_amount \
            if reduction_amount and not pd.isna(reduction_amount) else 0
        real_progress = real_progress if real_progress < 1 else 1
        target_data.at[idx,
                       'progress'] = real_progress if real_progress > 0 else 0
        target_data.at[idx, 'years_remaining'] = target_year - current_year
        target_data.at[idx, 'current_year_emission'] = current_emission


class Emission(object):

    def __init__(self, industry_code):
        self._transformer = CO2()
        self._industry_code = industry_code

    def prepare_data(self, codes, begin_date, end_date, category, method):
        kd_logger.info("""create {0} {1} transformer ... """.format(
            category, method))

        kd_logger.info("""{0} fetch target {1}~{2} data  """.format(
            codes[0], begin_date, end_date))
        target_data = self._transformer.fetch_company_targets(
            codes=codes, begin_date=begin_date, end_date=end_date)

        if target_data.empty:
            kd_logger.error("""{0} has no target data""".format(codes[0]))

        emission_data = self._transformer.fetch_company_emissions(
            codes=codes, begin_date=begin_date, end_date=end_date)

        if emission_data.empty:
            kd_logger.error("""{0} has no emission data""".format(codes[0]))

        target_scores, company_scores = self._transformer.company_scores(
            codes=codes)
        if target_scores.empty:
            kd_logger.error("""{0} has no target score data""".format(
                codes[0]))

        if company_scores.empty:
            kd_logger.error("""{0} has no company score data""".format(
                codes[0]))

        target_avg_scores, company_avg_scores = self._transformer.industry_scores(
            codes=codes)
        return target_data, emission_data.reset_index(drop=True), target_scores.reset_index(drop=True), company_scores.reset_index(drop=True), \
                    target_avg_scores.reset_index(drop=True), company_avg_scores.reset_index(drop=True)

    def _emissom_to_history(self, target_data, emission_data):
        index1 = target_data.set_index(['code']).index
        index2 = emission_data.set_index(['code']).index
        index3 = index2.difference(index1)
        ed = emission_data.set_index(['code']).loc[index3].reset_index()
        if ed.empty:
            return None, None
        history = ed[['FY', 'code', 'total_co2_emissions']].dropna().rename(
            columns={'total_co2_emissions': 'emission_value_db'})
        row_history = []
        group = history.groupby('code')
        for k, v in group:
            row = self._history_row('CO2e Emissions Scope 1, 2', v)
            row_history.append(row)
        row_history = pd.DataFrame(row_history)
        history['target_scope_str'] = 'CO2e Emissions Scope 1, 2'
        return history, row_history

    def _history_row(self, target_scope, history):
        start_year = int(history['FY'].iloc[0])
        end_year = int(history['FY'].iloc[-1])
        start_year_value = history['emission_value_db'].iloc[0]
        end_year_value = history['emission_value_db'].iloc[-1]
        total_changes = np.nan
        cagr = np.nan
        if start_year != end_year:
            total_changes = (end_year_value / start_year_value - 1) * 100
            cagr = (pow(end_year_value / start_year_value, 1 /
                        (end_year - start_year)) - 1) * 100
        return {
            'start_year': start_year,
            'end_year': end_year,
            'target_scope_str': target_scope,
            'total_changes': total_changes,
            'cagr': cagr,
            'code': history['code'].iloc[0]
        }

    def calculate_hisotry(self, target_data, emission_history_dfs):
        target_data['current_year'] = target_data['current_year'].apply(
            lambda x: int(x) if not pd.isna(x) else x)
        target_data['years_remaining'] = target_data['years_remaining'].apply(
            lambda x: int(x) if not pd.isna(x) else x)
        emission_history_list = []
        for k, rt in emission_history_dfs.items():
            rt = rt[rt.FY > 2013]
            rts = rt[['code', 'FY', 'emission_value_db']]
            rts['target_scope_str'] = k[-1]
            emission_history_list.append(rts)
        emission_history_list = pd.concat(emission_history_list, axis=0)

        emission_history = []
        row_history = []
        for target_scope in target_data['target_scope_str'].unique():
            emission_hist = emission_history_list[
                emission_history_list['target_scope_str'] == target_scope]
            emission_history.append(emission_hist)
            history = emission_hist.copy()
            if history.empty:
                continue
            group = history.groupby('code')
            for k, v in group:
                row = self._history_row(target_scope, v)
                row_history.append(row)
        emission_history = pd.concat(
            emission_history, axis=0) if len(emission_history) > 0 else None
        row_history = pd.DataFrame(row_history)
        return emission_history, row_history

    def calculate_results(self, codes, begin_date, end_date, target_data,
                          emission_data, target_scores, company_scores,
                          target_avg_scores, company_avg_scores):
        kd_logger.info("""calculate result ... """)
        if not target_data.empty:
            company_scores = company_scores.merge(company_avg_scores,
                                                  on=['code', 'time_frame'],
                                                  how='left')

            target_data['target_scope_str'] = target_data.apply(
                self._transformer.convert_scope, axis=1)

            target_data['scope'] = target_data.apply(
                self._transformer.convert_scope_SBTi, axis=1)

            target_data = target_data.merge(target_scores,
                                            how='left',
                                            on=[
                                                'code', 'scope', 'target_type',
                                                'base_year', 'target_year'
                                            ])
            target_data = target_data.dropna(subset=['time_frame'])
        else:
            emission_history, row_history = self._emissom_to_history(
                target_data=target_data, emission_data=emission_data)
            return None, None, emission_history, row_history

        target_data = target_data.merge(target_avg_scores,
                                        on=['code', 'scope', 'time_frame'],
                                        how='left')

        target_data['unit'], target_data['unit_desc'] = zip(
            *target_data.apply(lambda x: self._transformer.type_unit_mapping(
                x['target_type'], x['intensity_metric']),
                               axis=1))
        target_data['has_history'] = 1

        kd_logger.info("""{0} fetch metrics {1}~{2} data  """.format(
            codes[0], begin_date, end_date))

        target_data = target_data.sort_values(
            by=['code', 'target_scope_str', 'target_year'])

        emission_history_dfs = {}
        for idx, row in target_data.drop_duplicates(
                subset=['code', 'target_scope_str']).iterrows():
            emission_date = emission_data[emission_data['code'] == row['code']]
            emission_history = self._transformer.calc_year_values(
                row, emission_date.copy(deep=True))
            emission_history = emission_history.dropna(
                subset=['code', 'FY',
                        'emission_value_db'], how='any').drop(columns=['date'])
            if len(emission_history) == 0:
                target_data.loc[(
                    target_data['target_scope_str'] == row['target_scope_str'])
                                & (target_data['code'] == row['code']),
                                'has_history'] = 0
            emission_history_dfs[(row['code'],
                                  row['target_scope_str'])] = emission_history

        target_data['target_year_emission'] = np.nan
        target_data['current_year_emission'] = np.nan
        target_data['total_changes'] = np.nan
        target_data['cagr'] = np.nan
        target_data['current_year'] = np.nan
        target_data['progress'] = np.nan
        target_data['years_remaining'] = np.nan
        kd_logger.info("""{0} update target {1}~{2} data  """.format(
            codes[0], begin_date, end_date))

        for idx, target in target_data.iterrows():
            scope_str = target['target_scope_str']
            code = target['code']
            # if isinstance(target['base_year_value'], int) or isinstance(
            #         target['base_year_value'], str):
            self._transformer.update_target(
                idx, target, target_data,
                emission_history_dfs[(code, scope_str)])

        target_data['target_year_emission'] = np.nan
        target_data['current_year_emission'] = np.nan
        target_data['total_changes'] = np.nan
        target_data['cagr'] = np.nan
        target_data['current_year'] = np.nan
        target_data['progress'] = np.nan
        target_data['years_remaining'] = np.nan

        kd_logger.info("""{0} update target {1}~{2} data  """.format(
            codes[0], begin_date, end_date))

        for idx, target in target_data.iterrows():
            scope_str = target['target_scope_str']
            code = target['code']
            # if isinstance(target['base_year_value'], int) or isinstance(
            #         target['base_year_value'], str):
            self._transformer.update_target(
                idx, target, target_data,
                emission_history_dfs[(code, scope_str)])

        target_data[
            'reduction_ambition'] = target_data['reduction_ambition'] * 100
        target_data[
            'reduction_percent'] = target_data['reduction_percent'] * 100
        target_data['total_changes'] = target_data['total_changes'] * 100
        target_data['cagr'] = target_data['cagr'] * 100
        target_data['progress'] = target_data['progress'] * 100
        target_data['current_year'] = target_data['current_year'].apply(
            lambda x: int(x) if not pd.isna(x) else x)
        target_data['years_remaining'] = target_data['years_remaining'].apply(
            lambda x: int(x) if not pd.isna(x) else x)

        emission_history, row_history = self.calculate_hisotry(
            target_data, emission_history_dfs.copy())
        target_data = target_data.drop(columns=[
            'date', 'co2_emissions_scope1', 'co2_emissions_scope2',
            'co2_emissions_scope3'
        ])
        '''
        index1 = target_data.set_index(['code']).index
        index2 = emission_data.set_index(['code']).index
        index3 = index2.difference(index1)
        ed = emission_data.set_index(['code']).loc[index3].reset_index()
        
        if not ed.empty:  ## no target data 公司没有目标数据
            history = ed[[
                'FY', 'code', 'total_co2_emissions'
            ]].dropna().rename(
                columns={'total_co2_emissions': 'emission_value_db'})
            rh = []
            group = history.groupby('code')
            for k, v in group:
                row = self._history_row('CO2e Emissions Scope 1, 2', v)
                rh.append(row)
            rh = pd.DataFrame(rh)
            history['target_scope_str'] = 'CO2e Emissions Scope 1, 2'
            row_history = row_history.append(rh).reset_index(drop=True)
            emission_history = emission_history.append(history).reset_index(
                drop=True)
        '''
        sub_emission_history, sub_row_history = self._emissom_to_history(
            target_data=target_data, emission_data=emission_data)
        if sub_row_history is not None:
            row_history = row_history.append(sub_row_history).reset_index(
                drop=True)
        if sub_emission_history is not None:
            emission_history = emission_history.append(
                sub_emission_history).reset_index(drop=True)

        #scores_result = company_scores.to_dict(orient='records')
        #target_result = target_data.to_dict(orient='records')
        return company_scores, target_data, emission_history, row_history

    def run(self, begin_date, end_date, category, method):
        industry_data = SurfaceDBAPI.Industry().fetch(
            industry_code=self._industry_code,
            columns=['code', 'industry_id1'])
        if industry_data.empty:
            kd_logger.error('Industry data is empty')
            return None
        codes = industry_data['code'].unique().tolist()

        target_data, emission_data, target_scores, company_scores, target_avg_scores, company_avg_scores = self.prepare_data(
            codes=codes,
            begin_date=begin_date,
            end_date=end_date,
            category=category,
            method=method)
        if emission_data.empty:
            kd_logger.error('Target data is empty')
            return None, None, None, None
        company_scores, target_data, emission_history, row_history = self.calculate_results(
            codes=codes,
            begin_date=begin_date,
            end_date=end_date,
            target_data=target_data,
            emission_data=emission_data,
            target_scores=target_scores,
            company_scores=company_scores,
            target_avg_scores=target_avg_scores,
            company_avg_scores=company_avg_scores)
        return company_scores, target_data, emission_history, row_history
