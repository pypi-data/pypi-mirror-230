import inspect
from typing import Any
import string
import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.compute as pc

from scipy import stats

from ds_capability.components.commons import Commons
from ds_capability.intent.feature_build_correlate_intent import FeatureBuildCorrelateIntent
from ds_capability.sample.sample_data import Sample


# noinspection PyArgumentList,PyUnresolvedReferences
class FeatureBuildIntent(FeatureBuildCorrelateIntent):

    """Feature data is representative data that, depending on its application, holds statistical and
    distributive characteristics of its real world counterpart. This component provides a set of actions
    that focuses on building a synthetic data through knowledge and statistical analysis"""

    def get_number(self, start: [int, float, str]=None, stop: [int, float, str]=None, canonical: pa.Table=None,
                   relative_freq: list=None, precision: int=None, ordered: str=None, at_most: int=None, size: int=None,
                   quantity: float=None, to_header: str=None,  seed: int=None, save_intent: bool=None, intent_order: int=None,
                   intent_level: [int, str]=None, replace_intent: bool=None, remove_duplicates: bool=None) -> pa.Table:
        """ returns a number in the range from_value to to_value. if only to_value given from_value is zero

        :param start: optional (signed) integer or float to start from. See below for str
        :param stop: (signed) integer or float the number sequence goes to but not include. See below
        :param canonical: (optional) a pa.Table to append the result table to
        :param relative_freq: (optional) a weighting pattern or probability that does not have to add to 1
        :param precision: (optional) the precision of the returned number. if None then assumes int value else float
        :param ordered: (optional) order the data ascending 'asc' or descending 'dec', values accepted 'asc' or 'des'
        :param at_most:  (optional)the most times a selection should be chosen
        :param to_header: (optional) an optional name to call the column
        :param size: (optional) the size of the sample
        :param quantity: (optional) a number between 0 and 1 representing data that isn't null
        :param seed: (optional) a seed value for the random function: default to None
        :param save_intent: (optional) if the intent contract should be saved to the property manager
        :param intent_level: (optional) the column name that groups intent to create a column
        :param intent_order: (optional) the order in which each intent should run.
                    - If None: default's to -1
                    - if -1: added to a level above any current instance of the intent section, level 0 if not found
                    - if int: added to the level specified, overwriting any that already exist
                    
        :param replace_intent: (optional) if the intent method exists at the level, or default level
                    - True - replaces the current intent method with the new
                    - False - leaves it untouched, disregarding the new intent
                    
        :param remove_duplicates: (optional) removes any duplicate intent in any level that is identical
        :return: a random number

        The values can be represented by an environment variable with the format '${NAME}' where NAME is the
        environment variable name
        """
        # intent persist options
        self._set_intend_signature(self._intent_builder(method=inspect.currentframe().f_code.co_name, params=locals()),
                                   intent_level=intent_level, intent_order=intent_order, replace_intent=replace_intent,
                                   remove_duplicates=remove_duplicates, save_intent=save_intent)
        # remove intent params
        canonical = self._get_canonical(canonical)
        if not isinstance(size, int):
            raise ValueError("size not set. Size must be an int greater than zero")
        start = self._extract_value(start)
        stop = self._extract_value(stop)
        if not isinstance(size, int):
            raise ValueError("size not set. Size must be an int greater than zero")
        if not isinstance(start, (int, float)) and not isinstance(stop, (int, float)):
            raise ValueError(f"either a 'from_value' or a 'from_value' and 'to_value' must be provided")
        if not isinstance(start, (float, int)):
            start = 0
        if not isinstance(stop, (float, int)):
            (start, stop) = (0, start)
        if stop <= start:
            raise ValueError("The number range must be a positive difference, where to_value <= from_value")
        at_most = 0 if not isinstance(at_most, int) else at_most
        #        size = size if isinstance(size, int) else 1
        seed = self._seed() if seed is None else seed
        precision = 3 if not isinstance(precision, int) else precision
        if precision == 0:
            start = int(round(start, 0))
            stop = int(round(stop, 0))
        is_int = True if (isinstance(stop, int) and isinstance(start, int)) else False
        if is_int:
            precision = 0
        # build the distribution sizes
        if isinstance(relative_freq, list) and len(relative_freq) > 1 and sum(relative_freq) > 1:
            freq_dist_size = self._freq_dist_size(relative_freq=relative_freq, size=size, seed=seed)
        else:
            freq_dist_size = [size]
        # generate the numbers
        rtn_list = []
        generator = np.random.default_rng(seed=seed)
        d_type = int if is_int else float
        bins = np.linspace(start, stop, len(freq_dist_size) + 1, dtype=d_type)
        for idx in np.arange(1, len(bins)):
            low = bins[idx - 1]
            high = bins[idx]
            if low >= high:
                continue
            elif at_most > 0:
                sample = []
                for _ in np.arange(at_most, dtype=d_type):
                    count_size = freq_dist_size[idx - 1] * generator.integers(2, 4, size=1)[0]
                    sample += list(set(np.linspace(bins[idx - 1], bins[idx], num=count_size, dtype=d_type,
                                                   endpoint=False)))
                if len(sample) < freq_dist_size[idx - 1]:
                    raise ValueError(f"The value range has insufficient samples to choose from when using at_most."
                                     f"Try increasing the range of values to sample.")
                rtn_list += list(generator.choice(sample, size=freq_dist_size[idx - 1], replace=False))
            else:
                if d_type == int:
                    rtn_list += generator.integers(low=low, high=high, size=freq_dist_size[idx - 1]).tolist()
                else:
                    choice = generator.random(size=freq_dist_size[idx - 1], dtype=float)
                    choice = np.round(choice * (high - low) + low, precision).tolist()
                    # make sure the precision
                    choice = [high - 10 ** (-precision) if x >= high else x for x in choice]
                    rtn_list += choice
        # order or shuffle the return list
        if isinstance(ordered, str) and ordered.lower() in ['asc', 'des']:
            rtn_list.sort(reverse=True if ordered.lower() == 'asc' else False)
        else:
            generator.shuffle(rtn_list)
        rtn_list = self._set_quantity(rtn_list, quantity=self._quantity(quantity), seed=seed)
        rtn_arr = pa.NumericArray.from_pandas(rtn_list)
        if rtn_arr.type.equals('double'):
            try:
                rtn_arr = pa.array(rtn_arr, pa.int64())
            except pa.lib.ArrowInvalid:
                pass
        to_header = to_header if isinstance(to_header, str) else next(self.label_gen)
        return Commons.table_append(canonical, pa.table([rtn_arr], names=[to_header]))

    def get_category(self, selection: list, size: int, canonical: pa.Table=None, relative_freq: list=None, encode: bool=None,
                     quantity: float=None, to_header: str=None,  seed: int=None, save_intent: bool=None, intent_level: [int, str]=None,
                     intent_order: int=None, replace_intent: bool=None, remove_duplicates: bool=None) -> pa.Table:
        """ returns a categorical as a string.

        :param selection: a list of items to select from
        :param size: size of the return
        :param canonical: (optional) a pa.Table to append the result table to
        :param relative_freq: a weighting pattern that does not have to add to 1
        :param encode: if the categorical should be returned encoded as a dictionary type or string type (default)
        :param quantity: a number between 0 and 1 representing the percentage quantity of the data
        :param to_header: (optional) an optional name to call the column
        :param seed: a seed value for the random function: default to None
        :param save_intent: (optional) if the intent contract should be saved to the property manager
        :param intent_level: (optional) the column name that groups intent to create a column
        :param intent_order: (optional) the order in which each intent should run.
                    - If None: default's to -1
                    - if -1: added to a level above any current instance of the intent section, level 0 if not found
                    - if int: added to the level specified, overwriting any that already exist

        :param replace_intent: (optional) if the intent method exists at the level, or default level
                    - True - replaces the current intent method with the new
                    - False - leaves it untouched, disregarding the new intent

        :param remove_duplicates: (optional) removes any duplicate intent in any level that is identical
        :return: an item or list of items chosen from the list
        """
        # intent persist options
        self._set_intend_signature(self._intent_builder(method=inspect.currentframe().f_code.co_name, params=locals()),
                                   intent_level=intent_level, intent_order=intent_order, replace_intent=replace_intent,
                                   remove_duplicates=remove_duplicates, save_intent=save_intent)
        # remove intent params
        canonical = self._get_canonical(canonical)
        if not isinstance(size, int):
            raise ValueError("size not set. Size must be an int greater than zero")
        if len(selection) < 1:
            return [None] * size
        encode = encode if isinstance(encode, bool) else False
        seed = self._seed() if seed is None else seed
        relative_freq = relative_freq if isinstance(relative_freq, list) else [1]*len(selection)
        select_index = self._freq_dist_size(relative_freq=relative_freq, size=size, dist_length=len(selection),
                                                  dist_on='right', seed=seed)
        rtn_list = []
        for idx in range(len(select_index)):
            rtn_list += [selection[idx]]*select_index[idx]
        gen = np.random.default_rng(seed)
        gen.shuffle(rtn_list)
        rtn_list = self._set_quantity(rtn_list, quantity=self._quantity(quantity), seed=seed)
        to_header = to_header if isinstance(to_header, str) else next(self.label_gen)
        if encode:
            return Commons.table_append(canonical, pa.table([pa.DictionaryArray.from_pandas(rtn_list).dictionary_encode()], names=[to_header]))
        return Commons.table_append(canonical, pa.table([pa.DictionaryArray.from_pandas(rtn_list)], names=[to_header]))

    def get_boolean(self, size: int, canonical: pa.Table=None, probability: float=None, quantity: float=None,
                    to_header: str=None,  seed: int=None, save_intent: bool=None, intent_level: [int, str]=None, intent_order: int=None,
                    replace_intent: bool=None, remove_duplicates: bool=None) -> pa.Table:
        """A boolean discrete random distribution

        :param size: the size of the sample
        :param canonical: (optional) a pa.Table to append the result table to
        :param probability: a float between 0 and 1 of the probability of success. Default = 0.5
        :param quantity: a number between 0 and 1 representing data that isn't null
        :param to_header: (optional) an optional name to call the column
        :param seed: a seed value for the random function: default to None
        :param save_intent: (optional) if the intent contract should be saved to the property manager
        :param intent_level: (optional) the column name that groups intent to create a column
        :param intent_order: (optional) the order in which each intent should run.
                    - If None: default's to -1
                    - if -1: added to a level above any current instance of the intent section, level 0 if not found
                    - if int: added to the level specified, overwriting any that already exist

        :param replace_intent: (optional) if the intent method exists at the level, or default level
                    - True - replaces the current intent method with the new
                    - False - leaves it untouched, disregarding the new intent

        :param remove_duplicates: (optional) removes any duplicate intent in any level that is identical
        :return: a random number
        """
        # intent persist options
        self._set_intend_signature(self._intent_builder(method=inspect.currentframe().f_code.co_name, params=locals()),
                                   intent_level=intent_level, intent_order=intent_order, replace_intent=replace_intent,
                                   remove_duplicates=remove_duplicates, save_intent=save_intent)
        # remove intent params
        canonical = self._get_canonical(canonical)
        if not isinstance(size, int):
            raise ValueError("size not set. Size must be an int greater than zero")
        prob = probability if isinstance(probability, int) and 0 < probability < 1 else 0.5
        seed = self._seed(seed=seed)
        rtn_list = list(stats.bernoulli.rvs(p=probability, size=size, random_state=seed))
        rtn_list = list(map(bool, rtn_list))
        rtn_list = self._set_quantity(rtn_list, quantity=self._quantity(quantity), seed=seed)
        to_header = to_header if isinstance(to_header, str) else next(self.label_gen)
        return Commons.table_append(canonical, pa.table([pa.NumericArray.from_pandas(rtn_list)], names=[to_header]))

    def get_datetime(self, start: Any, until: Any, canonical: pa.Table=None, relative_freq: list=None,
                     at_most: int=None, ordered: str=None, date_format: str=None,  as_num: bool=None,
                     ignore_time: bool=None, ignore_seconds: bool=None, size: int=None, quantity: float=None,
                     to_header: str=None,  seed: int=None, day_first: bool=None, year_first: bool=None, save_intent: bool=None,
                     intent_level: [int, str]=None, intent_order: int=None, replace_intent: bool=None,
                     remove_duplicates: bool=None) -> pa.Table:
        """ returns a random date between two date and/or times. weighted patterns can be applied to the overall date
        range. if a signed 'int' type is passed to the start and/or until dates, the inferred date will be the current
        date time with the integer being the offset from the current date time in 'days'.

        Note: If no patterns are set this will return a linearly random number between the range boundaries.

        :param start: the start boundary of the date range can be str, datetime, pd.datetime, pd.Timestamp or int
        :param until: up until boundary of the date range can be str, datetime, pd.datetime, pd.Timestamp or int
        :param canonical: (optional) a pa.Table to append the result table to
        :param quantity: the quantity of values that are not null. Number between 0 and 1
        :param relative_freq: (optional) A pattern across the whole date range.
        :param at_most: the most times a selection should be chosen
        :param ordered: order the data ascending 'asc' or descending 'dec', values accepted 'asc' or 'des'
        :param ignore_time: ignore time elements and only select from Year, Month, Day elements. Default is False
        :param ignore_seconds: ignore second elements and only select from Year to minute elements. Default is False
        :param date_format: the string format of the date to be returned. if not set then pd.Timestamp returned
        :param as_num: returns a list of Matplotlib date values as a float. Default is False
        :param size: the size of the sample to return. Default to 1
        :param to_header: (optional) an optional name to call the column
        :param seed: a seed value for the random function: default to None
        :param year_first: specifies if to parse with the year first
                    - If True parses dates with the year first, e.g. 10/11/12 is parsed as 2010-11-12.
                    - If both dayfirst and yearfirst are True, yearfirst is preceded (same as dateutil).

        :param day_first: specifies if to parse with the day first
                    - If True, parses dates with the day first, eg %d-%m-%Y.
                    - If False default to a preferred preference, normally %m-%d-%Y (but not strict)

        :param save_intent: (optional) if the intent contract should be saved to the property manager
        :param intent_level: (optional) the column name that groups intent to create a column
        :param intent_order: (optional) the order in which each intent should run.
                    - If None: default's to -1
                    - if -1: added to a level above any current instance of the intent section, level 0 if not found
                    - if int: added to the level specified, overwriting any that already exist

        :param replace_intent: (optional) if the intent method exists at the level, or default level
                    - True - replaces the current intent method with the new
                    - False - leaves it untouched, disregarding the new intent

        :param remove_duplicates: (optional) removes any duplicate intent in any level that is identical
        :return: a date or size of dates in the format given.
         """
        # intent persist options
        self._set_intend_signature(self._intent_builder(method=inspect.currentframe().f_code.co_name, params=locals()),
                                   intent_level=intent_level, intent_order=intent_order, replace_intent=replace_intent,
                                   remove_duplicates=remove_duplicates, save_intent=save_intent)
        # remove intent params
        canonical = self._get_canonical(canonical)
        if not isinstance(size, int):
            raise ValueError("size not set. Size must be an int greater than zero")
        if start is None or until is None:
            raise ValueError("The start or until parameters cannot be of NoneType")
        # Code block for intent
        as_num = as_num if isinstance(as_num, bool) else False
        ignore_seconds = ignore_seconds if isinstance(ignore_seconds, bool) else False
        ignore_time = ignore_time if isinstance(ignore_time, bool) else False
        seed = self._seed() if seed is None else seed
        # start = start.to_pydatetime() if isinstance(start, pd.Timestamp) else start
        # until = until.to_pydatetime() if isinstance(until, pd.Timestamp) else until
        if isinstance(start, int):
            start = (pd.Timestamp.now() + pd.Timedelta(days=start))
        start = pd.to_datetime(start, errors='coerce', dayfirst=day_first,
                               yearfirst=year_first)
        if isinstance(until, int):
            until = (pd.Timestamp.now() + pd.Timedelta(days=until))
        elif isinstance(until, dict):
            until = (start + pd.Timedelta(**until))
        until = pd.to_datetime(until, errors='coerce', dayfirst=day_first,
                               yearfirst=year_first)
        if start == until:
            rtn_list = pd.Series([start] * size)
        else:
            dt_tz = pd.Series(start).dt.tz
            _dt_start = Commons.date2value(start, day_first=day_first, year_first=year_first)[0]
            _dt_until = Commons.date2value(until, day_first=day_first, year_first=year_first)[0]
            precision = 15
            rtn_tbl = self.get_number(start=_dt_start, stop=_dt_until, relative_freq=relative_freq, at_most=at_most,
                                       ordered=ordered, precision=precision, size=size, seed=seed, save_intent=False)
            rtn_list = rtn_tbl.columns.pop(0).to_pylist()
            rtn_list = pd.Series(Commons.value2date(rtn_list, dt_tz=dt_tz))
        if ignore_time:
            rtn_list = pd.Series(pd.DatetimeIndex(rtn_list).normalize())
        if ignore_seconds:
            rtn_list = rtn_list.apply(lambda t: t.replace(second=0, microsecond=0, nanosecond=0))
        if as_num:
            return Commons.date2value(rtn_list)
        if isinstance(date_format, str) and len(rtn_list) > 0:
            rtn_list = rtn_list.dt.strftime(date_format)
        rtn_list = self._set_quantity(rtn_list, quantity=self._quantity(quantity), seed=seed)
        to_header = to_header if isinstance(to_header, str) else next(self.label_gen)
        return Commons.table_append(canonical, pa.table([pa.TimestampArray.from_pandas(rtn_list)], names=[to_header]))

    def get_intervals(self, intervals: list, canonical: pa.Table=None, relative_freq: list=None, precision: int=None,
                      size: int=None, quantity: float=None, to_header: str=None,  seed: int=None, save_intent: bool=None,
                      intent_level: [int, str]=None, intent_order: int=None, replace_intent: bool=None,
                      remove_duplicates: bool=None) -> pa.Table:
        """ returns a number based on a list selection of tuple(lower, upper) interval

        :param intervals: a list of unique tuple pairs representing the interval lower and upper boundaries
        :param canonical: (optional) a pa.Table to append the result table to
        :param relative_freq: a weighting pattern or probability that does not have to add to 1
        :param precision: the precision of the returned number. if None then assumes int value else float
        :param size: the size of the sample
        :param quantity: a number between 0 and 1 representing data that isn't null
        :param to_header: (optional) an optional name to call the column
        :param seed: a seed value for the random function: default to None
        :param save_intent: (optional) if the intent contract should be saved to the property manager
        :param intent_level: (optional) the column name that groups intent to create a column
        :param intent_order: (optional) the order in which each intent should run.
                    - If None: default's to -1
                    - if -1: added to a level above any current instance of the intent section, level 0 if not found
                    - if int: added to the level specified, overwriting any that already exist

        :param replace_intent: (optional) if the intent method exists at the level, or default level
                    - True - replaces the current intent method with the new
                    - False - leaves it untouched, disregarding the new intent

        :param remove_duplicates: (optional) removes any duplicate intent in any level that is identical
        :return: a random number
        """
        # intent persist options
        self._set_intend_signature(self._intent_builder(method=inspect.currentframe().f_code.co_name, params=locals()),
                                   intent_level=intent_level, intent_order=intent_order, replace_intent=replace_intent,
                                   remove_duplicates=remove_duplicates, save_intent=save_intent)
        # remove intent params
        canonical = self._get_canonical(canonical)
        if not isinstance(size, int):
            raise ValueError("size not set. Size must be an int greater than zero")
        precision = precision if isinstance(precision, (float, int)) else 3
        seed = self._seed() if seed is None else seed
        if not all(isinstance(value, tuple) for value in intervals):
            raise ValueError("The intervals list must be a list of tuples")
        interval_tbl = self.get_category(selection=intervals, relative_freq=relative_freq, size=size, seed=seed,
                                          save_intent=False)
        interval_list = interval_tbl.columns.pop(0).to_pylist()
        interval_counts = pd.Series(interval_list, dtype='object').value_counts()
        rtn_list = []
        for index in interval_counts.index:
            size = interval_counts[index]
            if size == 0:
                continue
            if len(index) == 2:
                (lower, upper) = index
                if index == 0:
                    closed = 'both'
                else:
                    closed = 'right'
            else:
                (lower, upper, closed) = index
            if lower == upper:
                rtn_list += [round(lower, precision)] * size
                continue
            if precision == 0:
                margin = 1
            else:
                margin = 10 ** (((-1) * precision) - 1)
            if str.lower(closed) == 'neither':
                lower += margin
                upper -= margin
            elif str.lower(closed) == 'right':
                lower += margin
            elif str.lower(closed) == 'both':
                upper += margin
            # correct adjustments
            if lower >= upper:
                upper = lower + margin
            rtn_tbl = self.get_number(lower, upper, precision=precision, size=size, seed=seed, save_intent=False)
            rtn_list += rtn_tbl.columns.pop(0).to_pylist()
        np.random.default_rng(seed=seed).shuffle(rtn_list)
        rtn_list = self._set_quantity(rtn_list, quantity=self._quantity(quantity), seed=seed)
        to_header = to_header if isinstance(to_header, str) else next(self.label_gen)
        return Commons.table_append(canonical, pa.table([pa.StringArray.from_pandas(rtn_list)], names=[to_header]))

    def get_dist_normal(self, mean: float, std: float, canonical: pa.Table=None, precision: int=None, size: int=None,
                        quantity: float=None, to_header: str=None,  seed: int=None, save_intent: bool=None, intent_level: [int, str]=None,
                        intent_order: int=None, replace_intent: bool=None, remove_duplicates: bool=None) -> pa.Table:
        """A normal (Gaussian) continuous random distribution.

        :param mean: The mean (“centre”) of the distribution.
        :param std: The standard deviation (jitter or “width”) of the distribution. Must be >= 0
        :param canonical: (optional) a pa.Table to append the result table to
        :param precision: The number of decimal points. The default is 3
        :param size: the size of the sample. if a tuple of intervals, size must match the tuple
        :param quantity: a number between 0 and 1 representing data that isn't null
        :param to_header: (optional) an optional name to call the column
        :param seed: a seed value for the random function: default to None
        :param save_intent: (optional) if the intent contract should be saved to the property manager
        :param intent_level: (optional) the column name that groups intent to create a column
        :param intent_order: (optional) the order in which each intent should run.
                    - If None: default's to -1
                    - if -1: added to a level above any current instance of the intent section, level 0 if not found
                    - if int: added to the level specified, overwriting any that already exist

        :param replace_intent: (optional) if the intent method exists at the level, or default level
                    - True - replaces the current intent method with the new
                    - False - leaves it untouched, disregarding the new intent

        :param remove_duplicates: (optional) removes any duplicate intent in any level that is identical
        :return: a random number
        """
        # intent persist options
        self._set_intend_signature(self._intent_builder(method=inspect.currentframe().f_code.co_name, params=locals()),
                                   intent_level=intent_level, intent_order=intent_order, replace_intent=replace_intent,
                                   remove_duplicates=remove_duplicates, save_intent=save_intent)
        # remove intent params
        canonical = self._get_canonical(canonical)
        if not isinstance(size, int):
            raise ValueError("size not set. Size must be an int greater than zero")
        seed = self._seed() if seed is None else seed
        precision = precision if isinstance(precision, int) else 3
        generator = np.random.default_rng(seed=seed)
        rtn_list = list(generator.normal(loc=mean, scale=std, size=size))
        rtn_list = list(np.around(rtn_list, precision))
        rtn_list = self._set_quantity(rtn_list, quantity=self._quantity(quantity), seed=seed)
        to_header = to_header if isinstance(to_header, str) else next(self.label_gen)
        return Commons.table_append(canonical, pa.table([pa.NumericArray.from_pandas(rtn_list)], names=[to_header]))

    def get_dist_choice(self, number: [int, str, float], canonical: pa.Table=None, size: int=None, quantity: float=None,
                        to_header: str=None,  seed: int=None, save_intent: bool=None, intent_level: [int, str]=None, intent_order: int=None,
                        replace_intent: bool=None, remove_duplicates: bool=None) -> pa.Table:
        """Creates a list of latent values of 0 or 1 where 1 is randomly selected both upon the number given. The
        ``number`` parameter can be a direct reference to the canonical column header or to an environment variable.
        If the environment variable is used ``number`` should be set to ``"${<<YOUR_ENVIRON>>}"`` where
        <<YOUR_ENVIRON>> is the environment variable name

        :param number: The number of true (1) values to randomly chose from the canonical. see below
        :param canonical: (optional) a pa.Table to append the result table to
        :param size: the size of the sample. if a tuple of intervals, size must match the tuple
        :param quantity: a number between 0 and 1 representing data that isn't null
        :param to_header: (optional) an optional name to call the column
        :param seed: a seed value for the random function: default to None
        :param save_intent: (optional) if the intent contract should be saved to the property manager
        :param intent_level: (optional) the column name that groups intent to create a column
        :param intent_order: (optional) the order in which each intent should run.
                       If None: default's to -1
                       if -1: added to a level above any current instance of the intent section, level 0 if not found
                       if int: added to the level specified, overwriting any that already exist
        :param replace_intent: (optional) if the intent method exists at the level, or default level
                       True - replaces the current intent method with the new
                       False - leaves it untouched, disregarding the new intent
        :param remove_duplicates: (optional) removes any duplicate intent in any level that is identical
        :return: a list of 1 or 0

        as choice is a fixed value, number can be represented by an environment variable with the format '${NAME}'
        where NAME is the environment variable name
       """
        # intent persist options
        self._set_intend_signature(self._intent_builder(method=inspect.currentframe().f_code.co_name, params=locals()),
                                   intent_level=intent_level, intent_order=intent_order, replace_intent=replace_intent,
                                   remove_duplicates=remove_duplicates, save_intent=save_intent)
        # remove intent params
        canonical = self._get_canonical(canonical)
        if not isinstance(size, int):
            raise ValueError("size not set. Size must be an int greater than zero")
        seed = self._seed() if seed is None else seed
        number = self._extract_value(number)
        number = int(number * size) if isinstance(number, float) and 0 <= number <= 1 else int(number)
        number = number if 0 <= number < size else size
        if isinstance(number, int) and 0 <= number <= size:
            rtn_list = pd.Series(data=[0] * size)
            choice_tbl = self.get_number(stop=size, size=number, at_most=1, precision=0, ordered='asc', seed=seed,
                                         save_intent=False)
            choice_idx = choice_tbl.columns.pop(0).to_pylist()
            rtn_list.iloc[choice_idx] = [1] * number
            return rtn_list.reset_index(drop=True).to_list()
        rtn_list = pd.Series(data=[0] * size).to_list()
        rtn_list = self._set_quantity(rtn_list, quantity=self._quantity(quantity), seed=seed)
        to_header = to_header if isinstance(to_header, str) else next(self.label_gen)
        return Commons.table_append(canonical, pa.table([pa.NumericArray.from_pandas(rtn_list)], names=[to_header]))

    def get_dist_bernoulli(self, probability: float, canonical: pa.Table=None, size: int=None, quantity: float=None,
                           to_header: str=None,  seed: int=None, save_intent: bool=None, intent_level: [int, str]=None, intent_order: int=None,
                           replace_intent: bool=None, remove_duplicates: bool=None) -> pa.Table:
        """A Bernoulli discrete random distribution using scipy

        :param probability: the probability occurrence
        :param canonical: (optional) a pa.Table to append the result table to
        :param size: the size of the sample
        :param quantity: a number between 0 and 1 representing data that isn't null
        :param to_header: (optional) an optional name to call the column
        :param seed: a seed value for the random function: default to None
        :param save_intent: (optional) if the intent contract should be saved to the property manager
        :param intent_level: (optional) the column name that groups intent to create a column
        :param intent_order: (optional) the order in which each intent should run.
                    - If None: default's to -1
                    - if -1: added to a level above any current instance of the intent section, level 0 if not found
                    - if int: added to the level specified, overwriting any that already exist

        :param replace_intent: (optional) if the intent method exists at the level, or default level
                    - True - replaces the current intent method with the new
                    - False - leaves it untouched, disregarding the new intent

        :param remove_duplicates: (optional) removes any duplicate intent in any level that is identical
        :return: a random number
        """
        # intent persist options
        self._set_intend_signature(self._intent_builder(method=inspect.currentframe().f_code.co_name, params=locals()),
                                   intent_level=intent_level, intent_order=intent_order, replace_intent=replace_intent,
                                   remove_duplicates=remove_duplicates, save_intent=save_intent)
        # remove intent params
        canonical = self._get_canonical(canonical)
        if not isinstance(size, int):
            raise ValueError("size not set. Size must be an int greater than zero")
        seed = self._seed() if seed is None else seed
        probability = self._extract_value(probability)
        rtn_list = list(stats.bernoulli.rvs(p=probability, size=size, random_state=seed))
        rtn_list = self._set_quantity(rtn_list, quantity=self._quantity(quantity), seed=seed)
        to_header = to_header if isinstance(to_header, str) else next(self.label_gen)
        return Commons.table_append(canonical, pa.table([pa.NumericArray.from_pandas(rtn_list)], names=[to_header]))

    def get_dist_bounded_normal(self, mean: float, std: float, lower: float, upper: float, canonical: pa.Table=None,
                                precision: int=None, size: int=None, quantity: float=None, to_header: str=None,  seed: int=None,
                                save_intent: bool=None, intent_level: [int, str]=None, intent_order: int=None,
                                replace_intent: bool=None, remove_duplicates: bool=None) -> pa.Table:
        """A bounded normal continuous random distribution.

        :param mean: the mean of the distribution
        :param std: the standard deviation
        :param lower: the lower limit of the distribution
        :param upper: the upper limit of the distribution
        :param canonical: (optional) a pa.Table to append the result table to
        :param precision: the precision of the returned number. if None then assumes int value else float
        :param size: the size of the sample
        :param quantity: a number between 0 and 1 representing data that isn't null
        :param to_header: (optional) an optional name to call the column
        :param seed: a seed value for the random function: default to None
        :param save_intent: (optional) if the intent contract should be saved to the property manager
        :param intent_level: (optional) the column name that groups intent to create a column
        :param intent_order: (optional) the order in which each intent should run.
                    - If None: default's to -1
                    - if -1: added to a level above any current instance of the intent section, level 0 if not found
                    - if int: added to the level specified, overwriting any that already exist

        :param replace_intent: (optional) if the intent method exists at the level, or default level
                    - True - replaces the current intent method with the new
                    - False - leaves it untouched, disregarding the new intent

        :param remove_duplicates: (optional) removes any duplicate intent in any level that is identical
        :return: a random number
        """
        # intent persist options
        self._set_intend_signature(self._intent_builder(method=inspect.currentframe().f_code.co_name, params=locals()),
                                   intent_level=intent_level, intent_order=intent_order, replace_intent=replace_intent,
                                   remove_duplicates=remove_duplicates, save_intent=save_intent)
        # remove intent params
        canonical = self._get_canonical(canonical)
        if not isinstance(size, int):
            raise ValueError("size not set. Size must be an int greater than zero")
        precision = precision if isinstance(precision, int) else 3
        seed = self._seed() if seed is None else seed
        rtn_list = stats.truncnorm((lower - mean) / std, (upper - mean) / std, loc=mean, scale=std)
        rtn_list = rtn_list.rvs(size, random_state=seed).round(precision)
        rtn_list = self._set_quantity(rtn_list, quantity=self._quantity(quantity), seed=seed)
        to_header = to_header if isinstance(to_header, str) else next(self.label_gen)
        return Commons.table_append(canonical, pa.table([pa.NumericArray.from_pandas(rtn_list)], names=[to_header]))

    def get_distribution(self, distribution: str, canonical: pa.Table=None, is_stats: bool=None, precision: int=None,
                         size: int=None, quantity: float=None, to_header: str=None,  seed: int=None, save_intent: bool=None,
                         intent_level: [int, str]=None, intent_order: int=None, replace_intent: bool=None,
                         remove_duplicates: bool=None, **kwargs) -> pa.Table:
        """returns a number based the distribution type.

        :param distribution: The string name of the distribution function from numpy random Generator class
        :param is_stats: (optional) if the generator is from the stats package and not numpy
        :param canonical: (optional) a pa.Table to append the result table to
        :param precision: (optional) the precision of the returned number
        :param size: (optional) the size of the sample
        :param quantity: (optional) a number between 0 and 1 representing data that isn't null
        :param to_header: (optional) an optional name to call the column
        :param seed: (optional) a seed value for the random function: default to None
        :param save_intent: (optional) if the intent contract should be saved to the property manager
        :param intent_level: (optional) the column name that groups intent to create a column
        :param intent_order: (optional) the order in which each intent should run.
                    - If None: default's to -1
                    - if -1: added to a level above any current instance of the intent section, level 0 if not found
                    - if int: added to the level specified, overwriting any that already exist

        :param replace_intent: (optional) if the intent method exists at the level, or default level
                    - True - replaces the current intent method with the new
                    - False - leaves it untouched, disregarding the new intent

        :param remove_duplicates: (optional) removes any duplicate intent in any level that is identical
        :param kwargs: the parameters of the method
        :return: a random number
        """
        # intent persist options
        self._set_intend_signature(self._intent_builder(method=inspect.currentframe().f_code.co_name, params=locals()),
                                   intent_level=intent_level, intent_order=intent_order, replace_intent=replace_intent,
                                   remove_duplicates=remove_duplicates, save_intent=save_intent)
        # remove intent params
        canonical = self._get_canonical(canonical)
        if not isinstance(size, int):
            raise ValueError("size not set. Size must be an int greater than zero")
        seed = self._seed() if seed is None else seed
        precision = 3 if precision is None else precision
        is_stats = is_stats if isinstance(is_stats, bool) else False
        if is_stats:
            rtn_list = eval(f"stats.{distribution}.rvs(size=size, random_state=_seed, **kwargs)", globals(), locals())
        else:
            generator = np.random.default_rng(seed=seed)
            rtn_list = eval(f"generator.{distribution}(size=size, **kwargs)", globals(), locals())
        rtn_list = list(np.around(rtn_list, precision))
        rtn_list = self._set_quantity(rtn_list, quantity=self._quantity(quantity), seed=seed)
        to_header = to_header if isinstance(to_header, str) else next(self.label_gen)
        return Commons.table_append(canonical, pa.table([pa.NumericArray.from_pandas(rtn_list)], names=[to_header]))

    def get_string_pattern(self, pattern: str, canonical: pa.Table=None, choices: dict=None, as_binary: bool=None,
                           quantity: [float, int]=None, size: int=None, choice_only: bool=None, to_header: str=None,  seed: int=None,
                           save_intent: bool=None, intent_level: [int, str]=None, intent_order: int=None,
                           replace_intent: bool=None, remove_duplicates: bool=None) -> pa.Table:
        """ Returns a random string based on the pattern given. The pattern is made up from the choices passed but
        by default is as follows:
                - c = random char [a-z][A-Z]
                - d = digit [0-9]
                - l = lower case char [a-z]
                - U = upper case char [A-Z]
                - p = all punctuation
                - s = space

        you can also use punctuation in the pattern that will be retained
        A pattern example might be

        .. code:: text

                uuddsduu => BA12 2NE or dl-{uu} => 4g-{FY}

        to create your own choices pass a dictionary with a reference char key with a list of choices as a value

        :param pattern: the pattern to create the string from
        :param canonical: (optional) a pa.Table to append the result table to
        :param choices: (optional) an optional dictionary of list of choices to replace the default.
        :param as_binary: (optional) if the return string is prefixed with a b
        :param quantity: (optional) a number between 0 and 1 representing the percentage quantity of the data
        :param size: (optional) the size of the return list. if None returns a single value
        :param choice_only: (optional) if to only use the choices given or to take not found characters as is
        :param to_header: (optional) an optional name to call the column
        :param seed: (optional) a seed value for the random function: default to None
        :param save_intent: (optional) if the intent contract should be saved to the property manager
        :param intent_level: (optional) the column name that groups intent to create a column
        :param intent_order: (optional) the order in which each intent should run.
                    - If None: default's to -1
                    - if -1: added to a level above any current instance of the intent section, level 0 if not found
                    - if int: added to the level specified, overwriting any that already exist

        :param replace_intent: (optional) if the intent method exists at the level, or default level
                    - True - replaces the current intent method with the new
                    - False - leaves it untouched, disregarding the new intent

        :param remove_duplicates: (optional) removes any duplicate intent in any level that is identical
        :return: a string based on the pattern
        """
        # intent persist options
        self._set_intend_signature(self._intent_builder(method=inspect.currentframe().f_code.co_name, params=locals()),
                                   intent_level=intent_level, intent_order=intent_order, replace_intent=replace_intent,
                                   remove_duplicates=remove_duplicates, save_intent=save_intent)
        # Code block for intent
        canonical = self._get_canonical(canonical)
        if not isinstance(size, int):
            raise ValueError("size not set. Size must be an int greater than zero")
        choice_only = False if choice_only is None or not isinstance(choice_only, bool) else choice_only
        as_binary = as_binary if isinstance(as_binary, bool) else False
        quantity = self._quantity(quantity)
        seed = self._seed(seed=seed)
        if choices is None or not isinstance(choices, dict):
            choices = {'c': list(string.ascii_letters),
                       'd': list(string.digits),
                       'l': list(string.ascii_lowercase),
                       'U': list(string.ascii_uppercase),
                       'p': list(string.punctuation),
                       's': [' '],
                       }
            choices.update({p: [p] for p in list(string.punctuation)})
        else:
            for k, v in choices.items():
                if not isinstance(v, list):
                    raise ValueError(
                        "The key '{}' must contain a 'list' of replacements options. '{}' found".format(k, type(v)))

        generator = np.random.default_rng(seed=seed)
        rtn_list = pd.Series(dtype=str)
        for c in list(pattern):
            if c in choices.keys():
                result = generator.choice(choices[c], size=size)
            elif not choice_only:
                result = [c]*size
            else:
                continue
            s_result = pd.Series(result)
            if rtn_list.empty:
                rtn_list = s_result
            else:
                rtn_list += s_result
        if as_binary:
            rtn_list = rtn_list.str.encode(encoding='raw_unicode_escape')
        rtn_list = self._set_quantity(rtn_list.to_list(), quantity=self._quantity(quantity), seed=seed)
        to_header = to_header if isinstance(to_header, str) else next(self.label_gen)
        return Commons.table_append(canonical, pa.table([pa.StringArray.from_pandas(rtn_list)], names=[to_header]))

    def get_sample(self, sample_name: str, canonical: pa.Table=None, sample_size: int=None, shuffle: bool=None,
                   size: int=None, quantity: float=None, to_header: str=None,  seed: int=None, save_intent: bool=None,
                   intent_level: [int, str]=None, intent_order: int=None, replace_intent: bool=None,
                   remove_duplicates: bool=None) -> pa.Table:
        """ returns a sample set based on sector and name
        To see the sample sets available use the Sample class __dir__() method:

            > from ds_capability.sample.sample_data import Sample
            > Sample().__dir__()

        :param sample_name: The name of the Sample method to be used.
        :param canonical: (optional) a pa.Table to append the result table to
        :param sample_size: (optional) the size of the sample to take from the reference file
        :param shuffle: (optional) if the selection should be shuffled before selection. Default is true
        :param quantity: (optional) a number between 0 and 1 representing the percentage quantity of the data
        :param size: (optional) size of the return. default to 1
        :param to_header: (optional) an optional name to call the column
        :param seed: (optional) a seed value for the random function: default to None
        :param save_intent: (optional) if the intent contract should be saved to the property manager
        :param intent_level: (optional) the column name that groups intent to create a column
        :param intent_order: (optional) the order in which each intent should run.
                    - If None: default's to -1
                    - if -1: added to a level above any current instance of the intent section, level 0 if not found
                    - if int: added to the level specified, overwriting any that already exist

        :param replace_intent: (optional) if the intent method exists at the level, or default level
                    - True - replaces the current intent method with the new
                    - False - leaves it untouched, disregarding the new intent

        :param remove_duplicates: (optional) removes any duplicate intent in any level that is identical
        :return: a sample list
        """
        self._set_intend_signature(self._intent_builder(method=inspect.currentframe().f_code.co_name, params=locals()),
                                   intent_level=intent_level, intent_order=intent_order, replace_intent=replace_intent,
                                   remove_duplicates=remove_duplicates, save_intent=save_intent)
        # Code block for intent
        canonical = self._get_canonical(canonical)
        if not isinstance(size, int):
            raise ValueError("size not set. Size must be an int greater than zero")
        sample_size = sample_name if isinstance(sample_size, int) else size
        quantity = self._quantity(quantity)
        seed = self._seed(seed=seed)
        shuffle = shuffle if isinstance(shuffle, bool) else True
        selection = eval(f"Sample.{sample_name}(size={size}, shuffle={shuffle}, seed={seed})")
        rtn_list = self._set_quantity(selection, quantity=quantity, seed=seed)
        to_header = to_header if isinstance(to_header, str) else next(self.label_gen)
        return Commons.table_append(canonical, pa.table([pa.Array.from_pandas(rtn_list)], names=[to_header]))

    def get_analysis(self, size: int, other: [str, pa.Table], canonical: pa.Table=None, category_limit: int=None,
                     date_jitter: int=None, date_units: str=None, date_ordered: bool=None, seed: int=None,
                     save_intent: bool=None, intent_level: [int, str]=None, intent_order: int=None,
                     replace_intent: bool=None, remove_duplicates: bool=None) -> pa.Table:
        """ builds a set of columns based on another (see analyse_association)
        if a reference DataFrame is passed then as the analysis is run if the column already exists the row
        value will be taken as the reference to the sub category and not the random value. This allows already
        constructed association to be used as reference for a sub category.

        :param size: The number of rows
        :param other: a direct or generated pd.DataFrame. see context notes below
        :param canonical: (optional) a pa.Table to append the result table to
        :param category_limit: (optional) a global cap on categories captured. zero value returns no limits
        :param date_jitter: (optional) The size of the jitter. Default to 2
        :param date_units: (optional) The date units. Options ['W', 'D', 'h', 'm', 's', 'milli', 'micro']. Default 'D'
        :param date_ordered: (optional) if the dates are shuffled or in order
        :param seed: (optional) a seed value for the random function: default to None
        :param save_intent: (optional) if the intent contract should be saved to the property manager
        :param intent_level: (optional) the column name that groups intent to create a column
        :param intent_order: (optional) the order in which each intent should run. In
                    - If None: default's to -1
                    - if -1: added to a level above any current instance of the intent section, level 0 if not found
                    - if int: added to the level specified, overwriting any that already exist

        :param replace_intent: (optional) if the intent method exists at the level, or default level
                    - True - replaces the current intent method with the new
                    - False - leaves it untouched, disregarding the new intent

        :param remove_duplicates: (optional) removes any duplicate intent in any level that is identical
        :return: a pa.Table
        """
        # intent persist options
        self._set_intend_signature(self._intent_builder(method=inspect.currentframe().f_code.co_name, params=locals()),
                                   intent_level=intent_level, intent_order=intent_order, replace_intent=replace_intent,
                                   remove_duplicates=remove_duplicates, save_intent=save_intent)
        # Code block for intent
        canonical = self._get_canonical(canonical)
        other = self._get_canonical(other)
        if other is None or other.num_rows == 0:
            return None
        if not isinstance(size, int):
            raise ValueError("size not set. Size must be an int greater than zero")
        date_jitter = date_jitter if isinstance(date_jitter, int) else 2
        units_allowed = ['W', 'D', 'h', 'm', 's', 'milli', 'micro']
        date_units = date_units if isinstance(date_units, str) and date_units in units_allowed else 'D'
        date_ordered = date_ordered if isinstance(date_ordered, bool) else False
        seed = self._seed(seed=seed)
        rtn_tbl = None
        gen = np.random.default_rng(seed)
        for c in other.column_names:
            column = other.column(c)
            if (pa.types.is_boolean(column.type) and pc.all(column).as_py() == False) or len(column.drop_null()) == 0:
                result = pa.table([pa.nulls(size)], names=[c])
                rtn_tbl = Commons.table_append(rtn_tbl, result)
                continue
            nulls = round(column.null_count / other.num_rows, 5)
            column = column.combine_chunks().drop_null()
            if pa.types.is_dictionary(column.type):
                selection = column.dictionary.to_pylist()
                frequency = column.value_counts().field(1).to_pylist()
                result = self.get_category(selection=selection, relative_freq=frequency, size=size, to_header=c,
                                           quantity=1-nulls, save_intent=False)
            elif pa.types.is_integer(column.type) or pa.types.is_floating(column.type):
                s_values = column.to_pandas()
                precision = 0 if pa.types.is_integer(column.type) else 5
                jitter = pc.round(pc.multiply(pc.stddev(column), 0.1), 5).as_py()
                result = s_values.add(gen.normal(loc=0, scale=jitter, size=s_values.size))
                while result.size < size:
                    _ = s_values.add(gen.normal(loc=0, scale=jitter, size=s_values.size))
                    result = pd.concat([result, _], axis=0)
                result = result.sample(frac=1).iloc[:size].astype(column.type.to_pandas_dtype()).reset_index(drop=True)
                result = self._set_quantity(result, quantity=self._quantity(1-nulls), seed=seed)
                result = pa.table([pa.Array.from_pandas(result)], names=[c])
            elif pa.types.is_boolean(column.type):
                frequency = dict(zip(column.value_counts().field(0).to_pylist(),
                                     column.value_counts().field(1).to_pylist())).get(True)
                if frequency is None:
                    frequency = 0
                prob = frequency/size
                prob = prob if 0 < prob < 1 else 0.5
                _ = gen.choice([True, False,], size=size, p=[prob, 1 - prob])
                result = self._set_quantity(_, quantity=self._quantity(1 - nulls), seed=seed)
                result = pa.table([pa.BinaryArray.from_pandas(result)], names=[c])
            elif pa.types.is_string(column.type):
                # for the moment do nothing with strings
                result = column.to_pandas()
                while result.size < size:
                    result = pd.concat([result, result], axis=0)
                result = result.sample(frac=1).iloc[:size].reset_index(drop=True)
                result = pd.Series(self._set_quantity(result, quantity=self._quantity(1-nulls), seed=seed))
                arr = pa.StringArray.from_pandas(result)
                result = pa.table([arr], names=[c])
            elif pa.types.is_date(column.type) or pa.types.is_timestamp(column.type):
                s_values = column.to_pandas()
                # set jitters to time deltas
                jitter = pd.Timedelta(value=date_jitter, unit=date_units) if isinstance(date_jitter, int) else pd.Timedelta(value=0)
                jitter = int(jitter.to_timedelta64().astype(int) / 10 ** 3)
                _ = gen.normal(loc=0, scale=jitter, size=s_values.size)
                _ = pd.Series(pd.to_timedelta(_, unit='micro'), index=s_values.index)
                result = s_values.add(_)
                while result.size < size:
                    _ = gen.normal(loc=0, scale=jitter, size=s_values.size)
                    _ = pd.Series(pd.to_timedelta(_, unit='micro'), index=s_values.index)
                    result = pd.concat([result, s_values.add(_)], axis=0)
                result = result.iloc[:size].astype(column.type.to_pandas_dtype())
                if date_ordered:
                    result = result.sample(frac=1).reset_index(drop=True)
                else:
                    result = result.sort_values(ascending=False).reset_index(drop=True)
                result = pd.Series(self._set_quantity(result, quantity=self._quantity(1-nulls), seed=seed))
                result = pa.table([pa.TimestampArray.from_pandas(result)], names=[c])
            else:
                # return nulls for other types
                result = pa.table([pa.nulls(size)], names=[c])
            rtn_tbl = Commons.table_append(rtn_tbl, result)
        return Commons.table_append(canonical, rtn_tbl)

    def get_synthetic_data_types(self, size: int, canonical: pa.Table=None, inc_nulls: bool=None,
                                 prob_nulls: float=None, seed: int=None, category_encode: bool=None,
                                 save_intent: bool=None, intent_level: [int, str]=None,intent_order: int=None,
                                 replace_intent: bool=None, remove_duplicates: bool=None) -> pa.Table:
        """ A dataset with example data types

        :param size: The size of the sample
        :param inc_nulls: include values with nulls
        :param canonical: (optional) a pa.Table to append the result table to
        :param prob_nulls: (optional) a value between 0 an 1 of the percentage of nulls. Default 0.02
        :param category_encode: (optional) if the categorical should be encoded to DictionaryArray
        :param seed: (optional) a seed value for the random function: default to None
        :param save_intent: (optional) if the intent contract should be saved to the property manager
        :param intent_level: (optional) the column name that groups intent to create a column
        :param intent_order: (optional) the order in which each intent should run.
                    - If None: default's to -1
                    - if -1: added to a level above any current instance of the intent section, level 0 if not found
                    - if int: added to the level specified, overwriting any that already exist

        :param replace_intent: (optional) if the intent method exists at the level, or default level
                    - True - replaces the current intent method with the new
                    - False - leaves it untouched, disregarding the new intent

        :param remove_duplicates: (optional) removes any duplicate intent in any level that is identical
        :return: pandas DataSet
        """
        # intent persist options
        self._set_intend_signature(self._intent_builder(method=inspect.currentframe().f_code.co_name, params=locals()),
                                   intent_level=intent_level, intent_order=intent_order, replace_intent=replace_intent,
                                   remove_duplicates=remove_duplicates, save_intent=save_intent)
        # remove intent params
        canonical = self._get_canonical(canonical)
        if not isinstance(size, int):
            raise ValueError("size not set. Size must be an int greater than zero")
        seed = self._seed(seed=seed)
        prob_nulls = prob_nulls if isinstance(prob_nulls, float) and 0 < prob_nulls < 1 else 0.1
        category_encode = category_encode if isinstance(category_encode, bool) else True
        # cat
        canonical = self.get_category(selection=['SUSPENDED', 'ACTIVE', 'PENDING', 'INACTIVE', 'ARCHIVE'],
                                      canonical=canonical, size=size, seed=seed, relative_freq=[1, 70, 20, 30, 10],
                                      encode=category_encode, to_header='cat', save_intent=False)
        # num
        canonical = self.get_dist_normal(mean=0, std=1, canonical=canonical, size=size, seed=seed, to_header='num',
                                         save_intent=False)
        canonical = self.correlate_number(canonical, 'num', precision=5, jitter=2, seed=seed, to_header='num',
                                          save_intent=False)
        # int
        canonical = self.get_number(start=size, stop=size * 10, at_most=1, ordered=True, canonical=canonical, size=size,
                                    seed=seed, to_header='int', save_intent=False)
        # bool
        canonical = self.get_boolean(size=size, probability=0.7, canonical=canonical, seed=seed, to_header='bool',
                                     save_intent=False)
        # date
        canonical = self.get_datetime(start='2022-12-01', until='2023-03-31', ordered=True, canonical=canonical,
                                      size=size, seed=seed, to_header='date', save_intent=False)
        # string
        canonical = self.get_sample(sample_name='us_street_names', canonical=canonical, size=size, seed=seed,
                                    to_header='string',  save_intent=False)

        if isinstance(inc_nulls, bool) and inc_nulls:
            gen = np.random.default_rng()
            # cat_null
            prob_nulls = (gen.integers(1, 10, 1) * 0.001)[0] + prob_nulls
            canonical = self.get_category(selection=['High', 'Med', 'Low'], canonical=canonical, relative_freq=[9,8,4],
                                          quantity=1 - prob_nulls, to_header='cat_null', size=size,
                                          encode=category_encode, seed=seed, save_intent=False)
            # num_null
            prob_nulls = (gen.integers(1, 10, 1) * 0.001)[0] + prob_nulls
            canonical = self.get_number(start=-1.0, stop=1.0, canonical=canonical, size=size,
                                        relative_freq=[1, 1, 2, 3, 5, 8, 13, 21], quantity=1 - prob_nulls,
                                        to_header='num_null', seed=seed, save_intent=False)
            # date_null
            prob_nulls = (gen.integers(1, 10, 1) * 0.001)[0] + prob_nulls
            canonical = self.get_datetime(start='2022-12-01', until='2023-03-31', canonical=canonical, ordered=True,
                                          size=size, quantity=1 - prob_nulls, to_header='date_null', seed=seed,
                                          save_intent=False)
            # string_null
            prob_nulls = (gen.integers(1, 10, 1) * 0.001)[0] + prob_nulls
            canonical = self.get_sample(sample_name='us_cities', canonical=canonical, size=size, quantity=1-prob_nulls,
                                        to_header='string_null', seed=seed, save_intent=False)
            #sparse
            canonical = self.get_number(start=-50, stop=8.0, canonical=canonical, size=size, quantity=0.3,
                                        to_header='sparse', seed=seed, save_intent=False)
            # one string
            _ = pa.table([pa.array(['one']*size)], names=['one_string'])
            canonical = Commons.table_append(canonical, _)
            # duplicate num
            _ = pa.table([canonical.column('num')], names=['dup_num'])
            canonical = Commons.table_append(canonical, _)
            # nulls_int
            _ = pa.table([pa.array(pa.nulls(size), pa.int64())], names=['nulls_int'])
            canonical = Commons.table_append(canonical, _)
            # nulls_date
            _ = pa.table([pa.array(pa.nulls(size), pa.timestamp('ns'))], names=['nulls_date'])
            canonical = Commons.table_append(canonical, _)
            # nulls_str
            _ = pa.table([pa.array(pa.nulls(size), pa.string())], names=['nulls_str'])
            canonical = Commons.table_append(canonical, _)
            # nulls
            _ = pa.table([pa.nulls(size)], names=['nulls'])
            canonical = Commons.table_append(canonical, _)
            # binary
            canonical = self.get_string_pattern(pattern='cccccccc', canonical=canonical, as_binary=True, size=size,
                                                seed=seed, to_header='binary', save_intent=False)
            # list array
            _ = pa.array(list(zip(canonical.column('num').to_pylist(), canonical.column('num_null').to_pylist())))
            _ = pa.table([_], names=['nest_list'])
            canonical = Commons.table_append(canonical, _)

        return canonical

    def get_noise(self, size: int, num_columns: int, canonical: pa.Table=None, seed: int=None, name_prefix: str=None,
                  save_intent: bool=None, intent_level: [int, str]=None, intent_order: int=None,
                  replace_intent: bool=None, remove_duplicates: bool=None) -> pd.DataFrame:
        """ Generates multiple columns of noise in your dataset

        :param size: The number of rows
        :param num_columns: the number of columns of noise
        :param canonical: (optional) a pa.Table to append the result table to
        :param name_prefix: a name the prefix the column names
        :param seed: seed: (optional) a seed value for the random function: default to None
        :param save_intent: (optional) if the intent contract should be saved to the property manager
        :param intent_level: (optional) the column name that groups intent to create a column
        :param intent_order: (optional) the order in which each intent should run.
                    - If None: default's to -1
                    - if -1: added to a level above any current instance of the intent section, level 0 if not found
                    - if int: added to the level specified, overwriting any that already exist

        :param replace_intent: (optional) if the intent method exists at the level, or default level
                    - True - replaces the current intent method with the new
                    - False - leaves it untouched, disregarding the new intent

        :param remove_duplicates: (optional) removes any duplicate intent in any level that is identical
        :return: a DataFrame
        """
        # intent persist options
        self._set_intend_signature(self._intent_builder(method=inspect.currentframe().f_code.co_name, params=locals()),
                                   intent_level=intent_level, intent_order=intent_order, replace_intent=replace_intent,
                                   remove_duplicates=remove_duplicates, save_intent=save_intent)
        # Code block for intent
        canonical = self._get_canonical(canonical)
        if not isinstance(size, int):
            raise ValueError("size not set. Size must be an int greater than zero")
        seed = self._seed(seed=seed)
        num_columns = num_columns if isinstance(num_columns, int) else 1
        name_prefix = name_prefix if isinstance(name_prefix, str) else ''
        label_gen = Commons.label_gen()
        rtn_tbl = None
        generator = np.random.default_rng(seed=seed)
        for _ in range(num_columns):
            seed = self._seed(seed=seed, increment=True)
            a = generator.choice(range(1, 6))
            b = generator.choice(range(1, 6))
            _ = self.get_distribution(distribution='beta', a=a, b=b, precision=6, size=size, seed=seed,
                                      to_header=f"{name_prefix}{next(label_gen)}", save_intent=False)
            rtn_tbl = Commons.table_append(rtn_tbl, _)
        return Commons.table_append(canonical, rtn_tbl)

    @property
    def sample_lists(self) -> list:
        """A list of sample options"""
        return Sample().__dir__()

