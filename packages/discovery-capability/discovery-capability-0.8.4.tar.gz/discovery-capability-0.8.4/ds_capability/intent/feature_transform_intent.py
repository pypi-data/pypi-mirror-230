import inspect
import pandas as pd
import pyarrow as pa
import pyarrow.compute as pc
from ds_capability.components.commons import Commons
from ds_capability.intent.common_intent import CommonsIntentModel
from ds_capability.intent.abstract_feature_transform_intent import AbstractFeatureTransformIntentModel


class FeatureTransformIntent(AbstractFeatureTransformIntentModel, CommonsIntentModel):

    def model_encode_integer(self, canonical: pa.Table, headers: [str, list], ranking: list=None, prefix=None,
                             seed: int=None, save_intent: bool=None, intent_level: [int, str]=None,
                             intent_order: int=None, replace_intent: bool=None, remove_duplicates: bool=None):
        """ Integer encoding replaces the categories by digits from 1 to n, where n is the number of distinct
        categories of the variable. Integer encoding can be either nominal or orinal.

        Nominal data is categorical variables without any particular order between categories. This means that
        the categories cannot be sorted and there is no natural order between them.

        Ordinal data represents categories with a natural, ordered relationship between each category. This means
        that the categories can be sorted in either ascending or descending order. In order to encode integers as
        ordinal, a ranking must be provided.

        If ranking is given, the return will be ordinal values based on the ranking order of the list. If a
        categorical value is not found in the list it is grouped with other missing values and given the last
        ranking.

        :param canonical: a pd.DataFrame as the reference dataframe
        :param headers: the header(s) to apply the encoding
        :param ranking: (optional) if used, ranks the categorical values to the list given
        :param prefix: a str to prefix the column
        :param seed: seed: (optional) a seed value for the random function: default to None
        :param save_intent: (optional) if the intent contract should be saved to the property manager
        :param intent_level: (optional) the intent level that groups intent to create a column
        :param intent_order: (optional) the order in which each intent should run.
                    - If None: default's to -1
                    - if -1: added to a level above any current instance of the intent section, level 0 if not found
                    - if int: added to the level specified, overwriting any that already exist

        :param replace_intent: (optional) if the intent method exists at the level, or default level
                    - True - replaces the current intent method with the new
                    - False - leaves it untouched, disregarding the new intent

        :param remove_duplicates: (optional) removes any duplicate intent in any level that is identical
        :return: a pd.DataFrame
        """
        self._set_intend_signature(self._intent_builder(method=inspect.currentframe().f_code.co_name, params=locals()),
                                   intent_level=intent_level, intent_order=intent_order, replace_intent=replace_intent,
                                   remove_duplicates=remove_duplicates, save_intent=save_intent)
        # intend code block on the canonical
        canonical = self._get_canonical(canonical)
        prefix = prefix if isinstance(prefix, str) else ''
        headers = Commons.list_formatter(headers)
        _ = self._seed() if seed is None else seed
        tbl = None
        for header in headers:
            column = canonical.column(header).combine_chunks()
            if isinstance(ranking, list): # ordinal
                if pa.types.is_dictionary(column.type):
                    column = column.dictionary_decode()
                rank = Commons.list_formatter(ranking)
                unique = pc.unique(column).to_pylist()
                missing = Commons.list_diff(unique, rank, symmetric=False)
                full_rank = rank + missing
                values = list(range(len(rank)))
                values = values + ([len(rank)] * (len(full_rank) - len(rank)))
                mapper = dict(zip(full_rank, values))
                s_column = column.to_pandas()
                column =  pa.Array.from_pandas(s_column.replace(mapper))
            else: # nominal
                if not pa.types.is_dictionary(column.type):
                    column = column.dictionary_encode()
                column = pa.array(column.indicies, pa.int64())
            new_header = f"{prefix}{header}"
            tbl = Commons.table_append(tbl, pa.table([column], names=[new_header]))
        return Commons.table_append(canonical)

    def model_encode_one_hot(self, canonical: pa.Table, headers: [str, list], prefix=None, data_type: pa.Table=None,
                             prefix_sep: str=None, dummy_na: bool = False, drop_first: bool = False, seed: int=None,
                             save_intent: bool=None, intent_level: [int, str]=None, intent_order: int=None,
                             replace_intent: bool=None, remove_duplicates: bool=None) -> pd.DataFrame:
        """ encodes categorical data types, One hot encoding, consists in encoding each categorical variable with
        different boolean variables (also called dummy variables) which take values 0 or 1, indicating if a category
        is present in an observation.

        :param canonical:
        :param headers: the header(s) to apply multi-hot
        :param prefix: str, list of str, or dict of str, String to append DataFrame intent levels, with equal length.
        :param prefix_sep: str separator, default '_'
        :param dummy_na: Add a column to indicate null values, if False nullss are ignored.
        :param drop_first:  Whether to get k-1 dummies out of k categorical levels by removing the first level.
        :param data_type: Data type for new columns. Only a single dtype is allowed.
        :param seed: seed: (optional) a seed value for the random function: default to None
        :param save_intent: (optional) if the intent contract should be saved to the property manager
        :param intent_level: (optional) the intent level that groups intent to create a column
        :param intent_order: (optional) the order in which each intent should run.
                    - If None: default's to -1
                    - if -1: added to a level above any current instance of the intent section, level 0 if not found
                    - if int: added to the level specified, overwriting any that already exist

        :param replace_intent: (optional) if the intent method exists at the level, or default level
                    - True - replaces the current intent method with the new
                    - False - leaves it untouched, disregarding the new intent

        :param remove_duplicates: (optional) removes any duplicate intent in any level that is identical
        :return: a pd.DataFrame
        """
        self._set_intend_signature(self._intent_builder(method=inspect.currentframe().f_code.co_name, params=locals()),
                                   intent_level=intent_level, intent_order=intent_order, replace_intent=replace_intent,
                                   remove_duplicates=remove_duplicates, save_intent=save_intent)
        # intend code block on the canonical
        canonical = self._get_canonical(canonical)
        headers = Commons.list_formatter(headers)
        _ = self._seed() if seed is None else seed
        prefix_sep = prefix_sep if isinstance(prefix_sep, str) else "_"
        dummy_na = dummy_na if isinstance(dummy_na, bool) else False
        drop_first = drop_first if isinstance(drop_first, bool) else False
        d_type = data_type if data_type else pa.int64()
        dummies = pd.get_dummies(canonical.to_pandas(), columns=headers, prefix=prefix, prefix_sep=prefix_sep,
                              dummy_na=dummy_na, drop_first=drop_first, dtype=data_type)
        return pa.Table.from_pandas(dummies)
