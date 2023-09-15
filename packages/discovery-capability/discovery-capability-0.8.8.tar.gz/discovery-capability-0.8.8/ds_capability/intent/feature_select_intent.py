import inspect
import pandas as pd
import pyarrow as pa
import pyarrow.compute as pc
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

from ds_capability.components.commons import Commons
from ds_capability.intent.common_intent import CommonsIntentModel
from ds_capability.intent.abstract_feature_select_intent import AbstractFeatureSelectIntentModel


class FeatureSelectIntent(AbstractFeatureSelectIntentModel, CommonsIntentModel):

    def auto_clean_header(self, canonical: pa.Table, case: str=None, rename_map: [dict, list, str]=None,
                          replace_spaces: str=None, save_intent: bool=None, intent_level: [int, str]=None,
                          intent_order: int=None, replace_intent: bool=None, remove_duplicates: bool=None):
        """ clean the headers of a Table replacing space with underscore. This also allows remapping and case selection

        :param canonical: the pandas.DataFrame to drop duplicates from
        :param rename_map: (optional) a dict of name value pairs, a fixed length list of column names or connector name
        :param case: (optional) changes the headers to lower, upper, title. if none of these then no change
        :param replace_spaces: (optional) character to replace spaces with. Default is '_' (underscore)
        :param save_intent: (optional) if the intent contract should be saved to the property manager
        :param intent_level: (optional) the level name that groups intent by a reference name
        :param intent_order: (optional) the order in which each intent should run.
                    - If None: default's to -1
                    - if -1: added to a level above any current instance of the intent section, level 0 if not found
                    - if int: added to the level specified, overwriting any that already exist

        :param replace_intent: (optional) if the intent method exists at the level, or default level
                    - True - replaces the current intent method with the new
                    - False - leaves it untouched, disregarding the new intent

        :param remove_duplicates: (optional) removes any duplicate intent in any level that is identical
        :return: pandas.DataFrame.
        """
        # resolve intent persist options
        self._set_intend_signature(self._intent_builder(method=inspect.currentframe().f_code.co_name, params=locals()),
                                   intent_level=intent_level, intent_order=intent_order, replace_intent=replace_intent,
                                   remove_duplicates=remove_duplicates, save_intent=save_intent)
        # Code block for intent
        # auto mapping
        if isinstance(rename_map, str):
            if self._pm.has_connector(rename_map):
                handler = self._pm.get_connector_handler(rename_map)
                mapper = handler.load_canonical()
                if mapper.shape[1] == 1:
                    rename_map = mapper.iloc[:, 0].values.tolist()
                else:
                    rename_map = dict(zip(mapper.iloc[:, 0].values, mapper.iloc[:, 1].values))
            else:
                mapper=None
        # get headers as pd Series and map
        if isinstance(rename_map, dict):
            headers = pd.Series(canonical.column_names).replace(rename_map).astype(str)
        elif isinstance(rename_map, list) and len(rename_map) == canonical.num_columns:
            headers = pd.Series(rename_map)
        else:
            headers = pd.Series(canonical.column_names).astype(str)
        # tidy
        replace_spaces = replace_spaces if isinstance(replace_spaces, str) else '_'
        headers = headers.str.replace(' ', replace_spaces, regex=False)
        headers = headers.str.strip()
        headers = headers.str.replace(r'[^\w\s]', '', regex=True)  # Remove special characters
        # convert case
        if isinstance(case, str):
            if case.lower() == 'lower':
                headers = headers.str.lower()
            elif case.lower() == 'upper':
                headers = headers.str.lower()
            elif case.lower() == 'title':
                headers = headers.str.lower()
        # return table with new headers
        return pa.table(canonical.columns, names=headers.to_list())

    def auto_cast_types(self, canonical: pa.Table, category_max: int=None, save_intent: bool=None,
                        intent_level: [int, str]=None, intent_order: int=None, replace_intent: bool=None,
                        remove_duplicates: bool=None):
        """ attempts to cast the columns of a table to its content type.

        :param canonical: the pandas.DataFrame to drop duplicates from
        :param category_max:  (optional)
        :param save_intent: (optional) if the intent contract should be saved to the property manager
        :param intent_level: (optional) the level name that groups intent by a reference name
        :param intent_order: (optional) the order in which each intent should run.
                    - If None: default's to -1
                    - if -1: added to a level above any current instance of the intent section, level 0 if not found
                    - if int: added to the level specified, overwriting any that already exist

        :param replace_intent: (optional) if the intent method exists at the level, or default level
                    - True - replaces the current intent method with the new
                    - False - leaves it untouched, disregarding the new intent

        :param remove_duplicates: (optional) removes any duplicate intent in any level that is identical
        :return: pandas.DataFrame.
        """
        # resolve intent persist options
        self._set_intend_signature(self._intent_builder(method=inspect.currentframe().f_code.co_name, params=locals()),
                                   intent_level=intent_level, intent_order=intent_order, replace_intent=replace_intent,
                                   remove_duplicates=remove_duplicates, save_intent=save_intent)
        # Code block for intent
        return Commons.table_cast(canonical, cat_max=category_max)

    def auto_reinstate_nulls(self, canonical: pa.Table, nulls_list=None, headers: [str, list]=None, drop: bool=None,
                             data_type: [str, list]=None, regex: [str, list]=None, save_intent: bool=None,
                             intent_level: [int, str]=None, intent_order: int=None, replace_intent: bool=None,
                             remove_duplicates: bool=None):
        """ automatically reinstates nulls that have been masked with alternate values such as space or question-mark.
        By default, the nulls list is ['',' ','NaN','nan','None','null','Null','NULL']

        :param canonical:
        :param nulls_list: (optional) potential null values to replace with a null.
        :param headers: a list of headers to drop or filter on type
        :param drop: to drop or not drop the headers
        :param data_type: the column types to include or exclude. Default None else int, float, bool, object, 'number'
        :param regex: a regular expression to search the headers
        :param save_intent: (optional) if the intent contract should be saved to the property manager
        :param intent_level: (optional) the level name that groups intent by a reference name
        :param intent_order: (optional) the order in which each intent should run.
                    - If None: default's to -1
                    - if -1: added to a level above any current instance of the intent section, level 0 if not found
                    - if int: added to the level specified, overwriting any that already exist

        :param replace_intent: (optional) if the intent method exists at the level, or default level
                    - True - replaces the current intent method with the new
                    - False - leaves it untouched, disregarding the new intent

        :param remove_duplicates: (optional) removes any duplicate intent in any level that is identical
        :return: pandas.DataFrame.
        """
        # resolve intent persist options
        self._set_intend_signature(self._intent_builder(method=inspect.currentframe().f_code.co_name, params=locals()),
                                   intent_level=intent_level, intent_order=intent_order, replace_intent=replace_intent,
                                   remove_duplicates=remove_duplicates, save_intent=save_intent)
        # Code block for intent
        drop = drop if isinstance(drop, bool) else False
        nulls_list = nulls_list if isinstance(nulls_list, list) else ['', ' ', 'NaN', 'nan', 'None', 'null', 'Null',
                                                                      'NULL']

        selected_headers = Commons.filter_headers(canonical, headers=headers, d_types=data_type, regex=regex, drop=drop)
        rtn_tbl = None
        for n in selected_headers:
            c = canonical.column(n).to_pandas()
            c = c.where(~c.isin(nulls_list))
            canonical = Commons.table_append(canonical, pa.table([c], names=[n]))
        return canonical

    def auto_drop_columns(self, canonical: pa.Table, nulls_threshold: float=None, nulls_list: [bool, list]=None,
                          drop_predominant: bool=None, drop_empty_row: bool=None, drop_unknown: bool=None,
                          save_intent: bool=None, intent_level: [int, str]=None, intent_order: int=None,
                          replace_intent: bool=None, remove_duplicates: bool=None):
        """ auto removes columns that are at least 0.998 percent np.NaN, a single value, std equal zero or have a
        predominant value greater than the default 0.998 percent.

        :param canonical:
        :param nulls_threshold: The threshold limit of a nulls value. Default 0.95
        :param nulls_list: can be boolean or a list:
                    if boolean and True then null_list equals ['NaN', 'nan', 'null', '', 'None', ' ']
                    if list then this is considered potential null values.
        :param drop_predominant: drop columns that have a predominant value of the given predominant max
        :param drop_empty_row: also drop any rows where all the values are empty
        :param drop_unknown:  (optional) drop objects that are not string types such as binary
        :param save_intent: (optional) if the intent contract should be saved to the property manager
        :param intent_level: (optional) the level name that groups intent by a reference name
        :param intent_order: (optional) the order in which each intent should run.
                    - If None: default's to -1
                    - if -1: added to a level above any current instance of the intent section, level 0 if not found
                    - if int: added to the level specified, overwriting any that already exist

        :param replace_intent: (optional) if the intent method exists at the level, or default level
                    - True - replaces the current intent method with the new
                    - False - leaves it untouched, disregarding the new intent

        :param remove_duplicates: (optional) removes any duplicate intent in any level that is identical
        :return: pandas.DataFrame.
        """
        # resolve intent persist options
        self._set_intend_signature(self._intent_builder(method=inspect.currentframe().f_code.co_name, params=locals()),
                                   intent_level=intent_level, intent_order=intent_order, replace_intent=replace_intent,
                                   remove_duplicates=remove_duplicates, save_intent=save_intent)
        # Code block for intent
        nulls_threshold = nulls_threshold if isinstance(nulls_threshold, float) and 0 <= nulls_threshold <= 1 else 0.95
        drop_unknown = drop_unknown if isinstance(drop_unknown, bool) else False
        # drop knowns
        to_drop = []
        for n in canonical.column_names:
            c = canonical.column(n).combine_chunks()
            if pa.types.is_dictionary(c.type):
                c = c.dictionary_decode()
            if pa.types.is_nested(c.type) or pa.types.is_list(c.type) or pa.types.is_struct(c.type):
                to_drop.append(n)
            elif c.null_count / canonical.num_rows > nulls_threshold:
                to_drop.append(n)
            elif pc.count(pc.unique(c)).as_py() <= 1:
                to_drop.append(n)
        return canonical.drop_columns(to_drop)

    def auto_drop_duplicates(self, canonical: pa.Table, save_intent: bool=None, intent_level: [int, str]=None, 
                             intent_order: int=None, replace_intent: bool=None, remove_duplicates: bool=None):
        """ Removes columns that are duplicates of each other

        :param canonical:
        :param save_intent: (optional) if the intent contract should be saved to the property manager
        :param intent_level: (optional) the level name that groups intent by a reference name
        :param intent_order: (optional) the order in which each intent should run.
                    - If None: default's to -1
                    - if -1: added to a level above any current instance of the intent section, level 0 if not found
                    - if int: added to the level specified, overwriting any that already exist

        :param replace_intent: (optional) if the intent method exists at the level, or default level
                    - True - replaces the current intent method with the new
                    - False - leaves it untouched, disregarding the new intent

        :param remove_duplicates: (optional) removes any duplicate intent in any level that is identical
        :return: Canonical,.
        """
        # resolve intent persist options
        self._set_intend_signature(self._intent_builder(method=inspect.currentframe().f_code.co_name, params=locals()),
                                   intent_level=intent_level, intent_order=intent_order, replace_intent=replace_intent,
                                   remove_duplicates=remove_duplicates, save_intent=save_intent)
        # Code block for intent
        to_drop = []
        for i in range(0, len(canonical.column_names)):
            col_1 = canonical.column_names[i]
            for col_2 in canonical.column_names[i + 1:]:
                if canonical.column(col_1).equals(canonical.column(col_2)):
                    to_drop.append(col_2)
        return canonical.drop_columns(to_drop)

    def auto_drop_correlated(self, canonical: pa.Table, threshold: float=None, save_intent: bool=None,
                             intent_level: [int, str]=None, intent_order: int=None, replace_intent: bool=None,
                             remove_duplicates: bool=None) -> [dict, pd.DataFrame]:
        """ uses 'brute force' techniques to remove's highly correlated numeric columns based on the threshold,
        set by default to 0.998.

        :param canonical:
        :param threshold: (optional) threshold correlation between columns. default 0.998
        :param save_intent: (optional) if the intent contract should be saved to the property manager
        :param intent_level: (optional) the level name that groups intent by a reference name
        :param intent_order: (optional) the order in which each intent should run.
                    - If None: default's to -1
                    - if -1: added to a level above any current instance of the intent section, level 0 if not found
                    - if int: added to the level specified, overwriting any that already exist

        :param replace_intent: (optional) if the intent method exists at the level, or default level
                    - True - replaces the current intent method with the new
                    - False - leaves it untouched, disregarding the new intent

        :param remove_duplicates: (optional) removes any duplicate intent in any level that is identical
        :return: Canonical,.
        """
        # resolve intent persist options
        self._set_intend_signature(self._intent_builder(method=inspect.currentframe().f_code.co_name, params=locals()),
                                   intent_level=intent_level, intent_order=intent_order, replace_intent=replace_intent,
                                   remove_duplicates=remove_duplicates, save_intent=save_intent)
        # Code block for intent
        threshold = threshold if isinstance(threshold, float) and 0 < threshold < 1 else 0.998
        # extract numeric columns
        tbl_filter = Commons.filter_columns(canonical, d_types=[pa.int64(), pa.int32(), pa.float64(), pa.float32()])
        df_filter = tbl_filter.to_pandas()
        to_drop = set()
        corr_matrix = df_filter.corr()
        for i in range(len(corr_matrix.columns)):
            for j in range(i):
                if abs(corr_matrix.iloc[i, j]) > threshold:  # we are interested in absolute coeff value
                    col_name = corr_matrix.columns[i]  # getting the name of column
                    to_drop.add(col_name)
        return canonical.drop_columns(to_drop)

    def auto_projection(self, canonical: pa.Table, headers: list=None, drop: bool=None, n_components: [int, float]=None,
                        seed: int=None, save_intent: bool=None, intent_level: [int, str]=None, intent_order: int=None,
                        replace_intent: bool=None, remove_duplicates: bool=None, **kwargs) -> pd.DataFrame:
        """Principal component analysis (PCA) is a linear dimensionality reduction using Singular Value Decomposition
        of the data to project it to a lower dimensional space.

        :param canonical:
        :param headers: (optional) a list of headers to select (default) or drop from the dataset
        :param drop: (optional) if True then srop the headers. False by default
        :param n_components: (optional) Number of components to keep.
        :param seed: (optional) placeholder
        :param save_intent: (optional) if the intent contract should be saved to the property manager
        :param intent_level: (optional) the level name that groups intent by a reference name
        :param intent_order: (optional) the order in which each intent should run.
                    - If None: default's to -1
                    - if -1: added to a level above any current instance of the intent section, level 0 if not found
                    - if int: added to the level specified, overwriting any that already exist

        :param replace_intent: (optional) if the intent method exists at the level, or default level
                    - True - replaces the current intent method with the new
                    - False - leaves it untouched, disregarding the new intent

        :param remove_duplicates: (optional) removes any duplicate intent in any level that is identical
        :param kwargs: additional parameters to pass the PCA model
        :return: a pd.DataFrame
        """
        # resolve intent persist options
        self._set_intend_signature(self._intent_builder(method=inspect.currentframe().f_code.co_name, params=locals()),
                                   intent_level=intent_level, intent_order=intent_order, replace_intent=replace_intent,
                                   remove_duplicates=remove_duplicates, save_intent=save_intent)
        # Code block for intent
        headers = Commons.list_formatter(headers)
        sample = Commons.filter_columns(canonical, headers=headers, drop=drop, d_types=[pa.float64(), pa.int64()])
        sample = self.auto_drop_columns(sample, nulls_threshold=0.3)
        sample = Commons.table_fill_null(sample)
        if not sample or len(sample) == 0:
            return canonical
        n_components = n_components if isinstance(n_components, (int, float)) \
                                       and 0 < n_components < sample.shape[1]  else sample.shape[1]
        sample = sample.to_pandas(split_blocks=True)
        # standardise
        scaler = StandardScaler()
        train = scaler.fit_transform(sample)
        # pca
        pca = PCA(n_components=n_components, **kwargs)
        train = pca.fit_transform(train)
        gen = Commons.label_gen(prefix='pca_')
        names = []
        for n in range(train.shape[1]):
            names.append(next(gen))
        tbl = pa.Table.from_arrays(train.T, names=names)
        canonical = canonical.drop_columns(sample.columns)
        return Commons.table_append(canonical, tbl)
