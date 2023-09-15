import unittest
import os
from pathlib import Path
import shutil
import pandas as pd
import pyarrow as pa
import pyarrow.compute as pc
from ds_capability import FeatureBuild
from ds_capability.components.commons import Commons
from ds_capability.intent.feature_build_intent import FeatureBuildIntent
from ds_core.properties.property_manager import PropertyManager

# Pandas setup
pd.set_option('max_colwidth', 320)
pd.set_option('display.max_rows', 100)
pd.set_option('display.max_columns', 99)
pd.set_option('expand_frame_repr', True)


class FeatureBuilderTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        # clean out any old environments
        for key in os.environ.keys():
            if key.startswith('HADRON'):
                del os.environ[key]
        # Local Domain Contract
        os.environ['HADRON_PM_PATH'] = os.path.join('working', 'contracts')
        os.environ['HADRON_PM_TYPE'] = 'parquet'
        # Local Connectivity
        os.environ['HADRON_DEFAULT_PATH'] = Path('working/data').as_posix()
        # Specialist Component
        try:
            os.makedirs(os.environ['HADRON_PM_PATH'])
        except OSError:
            pass
        try:
            os.makedirs(os.environ['HADRON_DEFAULT_PATH'])
        except OSError:
            pass
        try:
            shutil.copytree('../_test_data', os.path.join(os.environ['PWD'], 'working/source'))
        except OSError:
            pass
        PropertyManager._remove_all()

    def tearDown(self):
        try:
            shutil.rmtree('working')
        except OSError:
            pass

    def test_for_smoke(self):
        fb = FeatureBuild.from_memory()
        tools: FeatureBuildIntent = fb.tools
        tbl = tools.get_synthetic_data_types(100)
        self.assertEqual((100, 6), tbl.shape)

    def test_correlate_discrete_intervals(self):
        fb = FeatureBuild.from_memory()
        tools: FeatureBuildIntent = fb.tools
        tbl = tools.get_synthetic_data_types(100)
        result = tools.correlate_discrete_intervals(tbl, header='num', to_header='num')
        self.assertEqual(5, pc.count(result.column('num').combine_chunks().dictionary).as_py())
        result = tools.correlate_discrete_intervals(tbl, header='num', categories=['low', 'mid', 'high'], to_header='num')
        self.assertCountEqual(['high', 'mid', 'low'], result.column('num').combine_chunks().dictionary.to_pylist())
        result = tools.correlate_discrete_intervals(tbl, header='num', granularity=[0.25,0.5,0.75],
                                                    categories=['0%->25%', '25%->50%', '50%->75%', '75%->100%'], to_header='num')
        self.assertCountEqual(['0%->25%', '25%->50%', '50%->75%', '75%->100%'], result.column('num').combine_chunks().dictionary.to_pylist())

    def test_correlate_on_condition(self):
        fb = FeatureBuild.from_memory()
        tools: FeatureBuildIntent = fb.tools
        tbl = tools.get_synthetic_data_types(1000, seed=101)
        # check no zeros
        self.assertEqual(0, pc.sum(pc.equal(tbl.column('num').combine_chunks(), 0)).as_py())
        # check three zeros
        result = tools.correlate_on_condition(tbl, header='num', other='num',
                                              condition=[(4, 'greater', 'or'), (-2, 'less', None)], value=0, to_header='num')
        self.assertEqual(383, pc.sum(pc.equal(result.column('num').combine_chunks(), pa.scalar(0.0))).as_py())
        # check string
        result = tools.correlate_on_condition(tbl, header='cat', other='cat',
                                              condition=[(pa.array(['INACTIVE', "SUSPENDED"]), 'is_in', None)], value='N/A', to_header='target')
        self.assertEqual(228, pc.count(pc.index_in(result.column('target').combine_chunks(), pa.array(['N/A'])).drop_null()).as_py())
        # check headers
        result = tools.correlate_on_condition(tbl, header='num', other='num',
                                              condition=[(4, 'greater', 'or'), (-2, 'less', None)],
                                              value=0, default=1, to_header='target')
        self.assertEqual(617, pc.sum(result.column('target')).as_py())
        result = tools.correlate_on_condition(tbl, header='num', other='num',
                                              condition=[(4, 'greater', 'or'), (-2, 'less', None)],
                                              value=0, default="@num", to_header='target')
        self.assertEqual(result.column('target').slice(2, 4), result.column('num').slice(2, 4))

    def test_correlate_column_join(self):
        fb = FeatureBuild.from_memory()
        tools: FeatureBuildIntent = fb.tools
        tbl = tools.get_synthetic_data_types(10, seed=101)
        result = tools.correlate_column_join(tbl, header='cat', others='string', sep=': ', to_header='compound')
        self.assertCountEqual(['cat', 'num', 'int', 'bool', 'date', 'compound'], result.column_names)
        self.assertEqual("PENDING: Smokeys Gate", result.column('compound').combine_chunks()[0].as_py())
        result = tools.correlate_column_join(tbl, header='cat', others='string', sep=': ', to_header='cat')
        self.assertCountEqual(['cat', 'num', 'int', 'bool', 'date'], result.column_names)
        self.assertEqual("PENDING: Smokeys Gate", result.column('cat').combine_chunks()[0].as_py())
        tbl = tools.get_synthetic_data_types(1000, inc_nulls=True, seed=101)
        result = tools.correlate_column_join(tbl, header='cat', others=['cat_null', 'string_null'], sep='-', to_header='compound')
        self.assertGreater(result.column('compound').combine_chunks().null_count, 0)

    def test_correlate_column_join_constant(self):
        fb = FeatureBuild.from_memory()
        tools: FeatureBuildIntent = fb.tools
        tbl = tools.get_synthetic_data_types(10, seed=101)
        result = tools.correlate_column_join(tbl, header='PI', others='int', to_header='compound')
        self.assertTrue(pc.all(pc.match_like(result.column('compound'),"PI__")).as_py())
        self.assertEqual(['cat', 'num', 'bool', 'date', 'string', 'compound'], result.column_names)
        result = tools.correlate_column_join(tbl, header='int', others=['-PI-', 'date'], to_header='int')
        self.assertTrue(pc.all(pc.match_like(result.column('int'),"__-PI-20%")).as_py())
        self.assertEqual(['cat', 'num', 'bool', 'string', 'int'], result.column_names)
        result = tools.correlate_column_join(tbl, header='int', others=['-PI-', 'date'], drop_others=False, to_header='compound')
        self.assertEqual(['cat', 'num', 'int', 'bool', 'date', 'string', 'compound'], result.column_names)

    def test_correlate_dates_jitter(self):
        fb = FeatureBuild.from_memory()
        tools: FeatureBuildIntent = fb.tools
        sample_size = 10
        tbl = tools.get_datetime(start=-30, until=-14, ordered=True, ignore_time=True, size=sample_size, to_header='creationDate')
        tbl = tools.correlate_dates(tbl, header="creationDate", ignore_time=True, offset={'days': 10}, jitter=1, jitter_units='D', to_header='processDate')
        tprint(tbl)

    # def test_correlate_dates_choice(self):
    #     fb = FeatureBuild.from_memory()
    #     tools: FeatureBuildIntent = fb.tools
    #     tbl = tools.get_synthetic_data_types(10)
    #     df['creationDate'] = tools.get_datetime(start=-30, until=-14, ordered=True, ignore_time=True, size=sample_size)
    #     df['processDate'] = tools.correlate_dates(df, header="creationDate", ignore_time=True, offset={'days': 10},
    #                                              choice=4, jitter=1, jitter_units='D')
    #
    #
    # def test_correlate_dates(self):
    #     fb = FeatureBuild.from_memory()
    #     tools: FeatureBuildIntent = fb.tools
    #     tbl = tools.get_synthetic_data_types(10)
    #     df = pd.DataFrame(columns=['dates'], data=['2019/01/30', '2019/02/12', '2019/03/07', '2019/03/07'])
    #     result = tools.correlate_dates(df, 'dates', date_format='%Y/%m/%d')
    #     self.assertEqual(df['dates'].to_list(), result)
    #     # offset
    #     result = tools.correlate_dates(df, 'dates', offset=2, date_format='%Y/%m/%d')
    #     self.assertEqual(['2019/02/01', '2019/02/14', '2019/03/09', '2019/03/09'], result)
    #     result = tools.correlate_dates(df, 'dates', offset=-2, date_format='%Y/%m/%d')
    #     self.assertEqual(['2019/01/28', '2019/02/10', '2019/03/05', '2019/03/05'], result)
    #     result = tools.correlate_dates(df, 'dates', offset={'years': 1, 'months': 2}, date_format='%Y/%m/%d')
    #     self.assertEqual(['2020/03/30', '2020/04/12', '2020/05/07', '2020/05/07'], result)
    #     result = tools.correlate_dates(df, 'dates', offset={'years': -1, 'months': 2}, date_format='%Y/%m/%d')
    #     self.assertEqual(['2018/03/30', '2018/04/12', '2018/05/07', '2018/05/07'], result)
    #     # jitter
    #     now = datetime.datetime.now()
    #     df = pd.DataFrame(columns=['dates'], data=tools._get_datetime(now, now + datetime.timedelta(days=1), size=1000, seed=31))
    #     df['result'] = tools.correlate_dates(df, 'dates', jitter=1, jitter_units='D', seed=31)
    #     loss = tools.correlate_dates(df, header='result', now_delta='D')
    #     self.assertEqual([579, 329, 83, 9], pd.Series(loss).value_counts().to_list())
    #     # nulls
    #     df = pd.DataFrame(columns=['dates'], data=['2019/01/30', np.nan, '2019/03/07', '2019/03/07'])
    #     result = tools.correlate_dates(df, 'dates')
    #     self.assertEqual('NaT', str(result[1]))
    #
    # def test_correlate_date_min_max(self):
    #     fb = FeatureBuild.from_memory()
    #     tools: FeatureBuildIntent = fb.tools
    #     tbl = tools.get_synthetic_data_types(10)
    #     # control
    #     df = pd.DataFrame(columns=['dates'], data=tools._get_datetime("2018/01/01", '2018/01/02', size=1000, seed=31))
    #     result = tools.correlate_dates(df, 'dates', jitter=5, jitter_units='D', date_format='%Y/%m/%d', seed=31)
    #     self.assertEqual("2017/12/14", pd.Series(result).min())
    #     self.assertEqual("2018/01/18", pd.Series(result).max())
    #     # min
    #     result = tools.correlate_dates(df, 'dates', jitter=5, jitter_units='D', min_date="2018/01/01", date_format='%Y/%m/%d', seed=31)
    #     self.assertEqual("2018/01/01", pd.Series(result).min())
    #     self.assertEqual("2018/01/18", pd.Series(result).max())
    #     # max
    #     result = tools.correlate_dates(df, 'dates', jitter=5, jitter_units='D', max_date="2018/01/01", date_format='%Y/%m/%d', seed=31)
    #     self.assertEqual("2017/12/14", pd.Series(result).min())
    #     self.assertEqual("2018/01/01", pd.Series(result).max())
    #
    # def test_correlate_date_as_delta(self):
    #     fb = FeatureBuild.from_memory()
    #     tools: FeatureBuildIntent = fb.tools
    #     tbl = tools.get_synthetic_data_types(10)
    #     # control
    #     now = pd.Timestamp.now()
    #     df = pd.DataFrame(columns=['dates'], data=[now - pd.DateOffset(years=52), now - pd.DateOffset(years=20)])
    #     result = tools.correlate_dates(df, 'dates', now_delta='Y')
    #     self.assertEqual([52, 20], result)


    def test_raise(self):
        with self.assertRaises(KeyError) as context:
            env = os.environ['NoEnvValueTest']
        self.assertTrue("'NoEnvValueTest'" in str(context.exception))

def tprint(t: pa.table, index_header: str=None):
    print(Commons.table_report(t, index_header=index_header).to_string())

if __name__ == '__main__':
    unittest.main()
