#
# --- LIBRARIES ---------------------------------------------------------------
import pandas as pd
import numpy as np
import math
import json
import re
import inspect

# --- BASE WITH SOME UTILITY FUNCTIONS ---------------------------------------

class BaseMetadataWorker():

    """
    A base class for metadata processing classes. Contains method to: \n
    * debug by printing function name \n
    * unpack a json dictionary containing metadata information \n
    * copy all instance input parameters to json \n
    * combine the *setup* and *process* functions for the specific subclass.

    """

    # Class variables ---------------------------------------------------------

    #: bool: Debug flag - function name will be printed at each function call
    # if this is True
    debug = False
    #: float: Small number used to make sure bins include boundary values
    eps = 1.E-6
    #:  str: Separator for collapsing vectors into strings
    separator = '|'
    #: str: prefix for json schema parms description
    worker_parms_description_prefix = 'init parameters for class '
    #: str: prefix for json schema df description
    processed_df_description_prefix = 'processed data for class '
    # These needed to be superseded for each class
    column_signature=['variable','level','count']
    column_place_holder_values=['NA','NA',0.0]

    # Class utility functions -------------------------------------------------

    @classmethod
    def place_holder_result(cls):
        '''
        Class method. Creates a dummy data frame with a single line of data.
        Used when it is important to return something even if there is
        nothing to return (for example, in a Spotfire data function)

        Returns
        -------
        Pandas dataframe
            The dataframe with one line of columns. Column names and content
            are class variables column_place_holder_values and
            column_signature.

        '''
        return pd.DataFrame(data=[cls.column_place_holder_values],
                            columns=cls.column_signature)

    @classmethod
    def set_debug(cls, debug):
        '''
        Class method. Set value of class variable debug to True or False
        '''
        cls.debug = debug

    @classmethod
    def get_current_function_name(cls):
        '''
        Class method.
        Print current function name if class variable debug is True
        '''
        if cls.debug:
            print(cls, '.', inspect.stack()[1].function)

    @classmethod
    def pack_json(cls, worker_parms, X, worker_parms_name, processed_df_name):
        '''
        Class method. Take all information from this class, and turn it into a
        JSON object.

        Parameters
        ----------
        worker_parms : dictionary
            The input parameters of the current Worker.
        X : Pandas dataframe
            The input data frame.
        worker_parms_name : string
            The label for these parameters.
        processed_df_name : string
            The label for the processed dataframe.

        Returns
        -------
        json_schema : dictionary
            A description of the content in this JSON string.
        json_body : dictionary
            The JSON object containing the parameters to re-create this Worker.
        json_df : string
            The serialized processed dataframe.

        '''

        # Create a new worker object of the type of the current class
        my_worker = cls.__new__(cls)
        # Initialize its attributes with the parameters from json
        my_worker.__init__(**worker_parms)
        # Set it up with input data frame, and return processed data frame
        processed_df = my_worker.setup_and_process(X)

        # Create json bits
        json_parms = my_worker.init_attributes_to_json()
        json_df = processed_df.to_json()
        # Assemble json
        # Find class name (remove whatever comes before last dot)
        my_class_name = cls.__name__.split('.')[-1]
        # Create labels and mini schema
        worker_parms_description = cls.worker_parms_description_prefix + my_class_name
        processed_df_description = cls.processed_df_description_prefix + my_class_name
        json_schema = {worker_parms_description: worker_parms_name,
                       processed_df_description: processed_df_name}
        # Create body of json
        json_body = {worker_parms_name: json_parms,
                     processed_df_name: json_df}

        return (json_schema, json_body, json_df)

    @classmethod
    def unpack_json(cls, received_json, return_df=False):
        '''
        Class method. Unpack a JSON object into its original Worker object
        and optionally metadata dataframe.

        Parameters
        ----------
        received_json : dictionary or string.
            The JSON object to unpack. If the object is in string format,
            it will be automatically loaded into a dictionary.
        return_df : boolean, optional
            If True, we also return the dataframe representation of the metadata
            object packed in the JSON object. The default is False.

        Raises
        ------
        KeyError
            If the schema, the parameters or the metadata for this Worker were not
            found in the JSON object.

        Returns
        -------
        Tuple of Worker object and metadata dataframe, or only Worker object.
            A tuple containing the unpacked worker and optionally the unpacked
            metadata.

        '''
        cls.get_current_function_name()

        #If the json is not in dictionary form, turn it into one
        if type(received_json)== str:
            received_json = json.loads(received_json)

        # The json dictionary must contain a descriptive schema
        try:
            schema = json.loads(received_json['schema'])
        except KeyError:
            raise KeyError(
                str(cls)+'.unpack_json: The schema key was not in json dictionary')

        # Find class name (remove whatever comes before last dot)
        my_class_name = cls.__name__.split('.')[-1]

        # Construct description strings (same as in function pack_json)
        key_parms_search = cls.worker_parms_description_prefix + my_class_name
        key_df_search = cls.processed_df_description_prefix + my_class_name
        # Find them in the schema dictionary
        parms_key = list(filter(lambda x: key_parms_search in x, schema))
        df_key = list(filter(lambda x: key_df_search in x, schema))

        if len(parms_key) > 0:
            parms = schema[parms_key[0]]
            received_attributes = json.loads(received_json[parms])
            # Create a new worker object of the type of the current class
            received_worker = cls.__new__(cls)
            # Initialize its attributes with the parameters from json
            received_worker.__init__(**received_attributes)
        else:
            raise KeyError(
                str(cls)+'.unpack_json: The parms parameter was not in json dictionary: '+key_parms_search)

        if len(df_key) > 0:
            df = schema[df_key[0]]
            # Extract the processed dataframe from json
            received_df = pd.DataFrame(json.loads(received_json[df]))
            # Setup the worker with it
            received_worker.setup_from_object(received_df)
        else:
            raise KeyError(
                str(cls)+'.: The dataframe parameter was not in json dictionary: '+key_df_search)

        # Do we return the dataframe as well, or only the worker?
        if return_df:
            return (received_worker, received_df)
        else:
            return received_worker

    @classmethod
    def detect_and_cast_date_types(cls, X):
        '''
        When data comes from external sources, it is possible that columns
        appearing to be of type 'object' do actually contain dates.
        This function converts them explicitly to dates by using
        pandas.to_datetime()

        Parameters
        ----------
        X : data frame
            The input data frame.

        Returns
        -------
        data frame
            The input data frame with explicit date types.

        '''
        import datetime
        objects=X.select_dtypes(include='object').columns.tolist()
        if len(objects)>0:
            # The test is performed on the first and last elements,
            # ...using dtype on the whole series does not detect dates
            N=X.shape[0]-1
            actual_dates1=X[objects].apply(lambda x: isinstance(x[0],datetime.date))
            actual_dates2=X[objects].apply(lambda x: isinstance(x[N],datetime.date))
            actual_dates = [a and b  for a, b in zip(actual_dates1,actual_dates2)]
            actual_date_vars = [v for (v, i) in zip(objects, actual_dates) if i]
            if len(actual_date_vars)>0:
                X[actual_date_vars] = X[actual_date_vars].apply(lambda x:pd.to_datetime(x))
        return X


    # Object methods ----------------------------------------------------------

    def init_attributes_to_json(self):
        '''
        Collect the instance attributes defined at construction,
        and turn them into a json string.
        Used within a constructor method.

        Returns
        -------
        string
            JSON string containing instance attributes needed to
            configure worker.

        '''

        self.__class__.get_current_function_name()
        return json.dumps(self.__init_attributes__)

    def setup_and_process(self, X):
        '''
        Perform the current object setup method, followed by the process
        method.

        Parameters
        ----------
        X : Pandas dataframe
            The input dataframe to process.

        Returns
        -------
        Pandas dataframe
            The processed dataframe, i.e. the metadata.

        '''

        self.__class__.get_current_function_name()
        self.setup(X)
        return self.process(X)

    def setup_from_object_and_process(self, Y, X=None):
        '''
        Perform the current object setup_from_object method, followed by the
        process method. If the metadata to reverse-engineer is not specified,
        this method reverts to setup_and_process.


        Parameters
        ----------
        Y : Pandas dataframe
            The new dataframe to process.
        X : Pandas dataframe, optional
            The blueprint processed dataframe. The default is None.

        Returns
        -------
        Pandas dataframe
            The processed new dataframe.

        '''

        self.__class__.get_current_function_name()
        if X is not None:
            self.setup_from_object(X)
        else:
            self.setup(Y)
        return self.process(Y)

#
# --- CATEGORICAL COUNTING AND GROUPING ---------------------------------------


class CategoricalFrequenciesWorker(BaseMetadataWorker):
    """
    A class for generating metadata from categorical variables.
    Contains methods for setting up a list of categories from a dataframe
    (*setup*)
    and calculating the count of levels for potentially a different dataframe
    (*process*).

    Returns a data frame with columns:\n
    * variable: the name of the original variable, e.g. City.\n
    * level: the value of the variable, e.g. 'London'.\n
    * count: the number of rows in the input dataframe that have City =
    'London'.

    :param bool auto_detect_categories: if True, class will use *cat_dtypes*
    to decide which variables are categorical; otherwise *categories* is used.
    (Default: True).
    :param bool include_nulls: if True, include null values as a separate
    level; otherwise ignore null values. (Default: True).
    :param bool empty_as_null: if True, treat empty strings as nulls; otherwise
    treat empty strings as separate levels. (Default: True).
    :param str name_of_null_level: name to give to level containing null
    values.(Default: 'missing').
    :param list[str] categories: list of variables to treat as categorical,
    if *auto_detect_categories* is False - otherwise ignored. (Default:[]).

    """

    # Class variables ----------------------------------------------------------

    #: list[str]: data types recognized as categories -
    # if *auto_detect_categories* is False  (class variable)
    cat_dtypes = ['bool', 'object']

    column_signature=['variable','level','count']
    column_place_holder_values=['NA','NA',0.0]

    # Class utility functions --------------------------------------------------

    # Object methods -----------------------------------------------------------

    def __init__(self, auto_detect_categories=True, include_nulls=True,
                 empty_as_null=True, name_of_null_level='missing',
                 categories=[]):
        '''
        Initialize object by storing the relevant information.
        Save instance attributes passed in into special
        instance variable __init_attributes__.

        Parameters
        ----------
        auto_detect_categories : bool, optional
            if True, class will use class variable cat_dtypes
            to decide which variables are categorical; otherwise categories
            is used. The default is True.
        include_nulls : bool, optional
            If True, include null values as a separate
            level; otherwise ignore null values. The default is True.
        empty_as_null : bool, optional
            If True, treat empty strings as nulls; otherwise
            treat empty strings as separate levels. The default is True.
        name_of_null_level : str, optional
            Name to give to level containing null
            values. The default is 'missing'.
        categories : list of str, optional
            List of variables to treat as categorical,
            if auto_detect_categories is False; otherwise ignored.
            The default is [].

        Returns
        -------
        None.

        '''
        self.__class__.get_current_function_name()
        self.auto_detect_categories = auto_detect_categories
        self.include_nulls = include_nulls
        self.empty_as_null = empty_as_null
        self.name_of_null_level = name_of_null_level
        self.categories = categories

        # Save a copy of the instance attributes defined during construction
        self.__init_attributes__ = self.__dict__.copy()

        return None

    def setup_from_object(self, XP):
        """
        Reverse engineer levels from existing processed dataframe.
        Used when levels generated for a dataframe are applied to a new dataframe.\n
        Fills instance variable *categories* with the variables found in the processed dataframe.

        :param pandas.DataFrame XP: the processed dataframe to use as a blueprint.
        :raise KeyError: if the 'variable' column does not exist in the input dataframe.

        """
        self.__class__.get_current_function_name()
        if 'variable' not in XP.columns:
            raise KeyError(str(
                self.__class__)+'.setup_from_object: Column: variable not found in input dataframe')
        # Generate the bins
        self.categories = list(dict.fromkeys(XP['variable']))

        return self

    def setup(self, X):
        """
        Set up list of categorical variables from input dataframe. \n
        Fills instance variable *categories* with the categorical variables.

        :param pandas.DataFrame X: the input dataframe for setup.
        :raise KeyError: if the input parameter *categories* contains columns that do not exist in the input dataframe.

        """
        self.__class__.get_current_function_name()
        # Detect and cast dates
        X = self.__class__.detect_and_cast_date_types(X)
        # Types recognized as categorical columns are stored in class variable cat_dtypes
        if self.auto_detect_categories:
            self.categories = X.select_dtypes(
                include=self.__class__.cat_dtypes).columns.tolist()
        else:
            # Check columns listed in categories exist in the data frame
            if not set(self.categories).issubset(set(X.columns)):
                bad_categories = []
                for bc in self.categories:
                    if bc not in X.columns:
                        bad_categories.append(bc)

                raise KeyError(str(
                    self.__class__)+'.setup: Categories not in data frame: '+', '.join(bad_categories))

        return self

    def process_column(self, X_cc, cc):
        """
        Fills dataframe with the counts for each level of the selected column.\n
        Empty values are optionally treated as nulls, and null values are optionally included in the count.

        :param pandas.Series X_cc: column of categorical data.
        :param str cc: name of the categorical column.
        :return: a data structure with columns ['level', 'count', 'variable']
        :rtype: pandas.DataFrame.

        """
        self.__class__.get_current_function_name()
        # Replace empty strings with nan if we want to treat empty strings as nulls
        if self.empty_as_null:
            X_cc.replace(r'^\s*$', None, regex=True, inplace=True)
        # Count occurrencies, including nulls if we want to include them in the counts
        XP_cc = X_cc.value_counts(
            dropna=not self.include_nulls).to_frame().reset_index()
        XP_cc.columns = ["level", "count"]
        XP_cc["variable"] = cc
        return XP_cc

    def process(self, X):
        """
        Fills dataframe with the counts for each level of categorical columns.\n

        :param pandas.DataFrame X: the input dataframe.
        :return: a data structure with columns ['level', 'count', 'variable']
        :rtype: pandas.DataFrame.

        """
        self.__class__.get_current_function_name()
        XP = pd.DataFrame(data={"level": [], "count": [], "variable": []})
        for cc in self.categories:
            # Use pipe to apply process_column to each column cc
            XP_cc = X[cc].pipe(self.process_column, cc)
            XP = pd.concat([XP, XP_cc], ignore_index=True)

        # Reorder columns
        XP = XP[['variable', 'level', 'count']]
        # Replace null bin with the chosen value
        XP.loc[XP['level'].isna(), 'level'] = self.name_of_null_level
        return XP


# -----------------------------------------------------------------------------
# Class to regroup high-cardinality categorical features into fewer categories

# variable: the categorical variable
# level: the level frequency bin after count encoding
# count: the number of rows for this level
# startbin: the value of the start count-encoded bin
# endbin: the value of the end count-encoded bin
# levels: the actual categorical levels in this bin (if allowed by cutoff on frequency)
# n_levels: the number of actual categorical levels in this bin

class CategoricalFrequenciesGrouper(BaseMetadataWorker):
    """
    NOTE: This class is currently by-passed and is likely to be largely re-engineered
    in the future.
    A class to generate a binned representation of high-cardinality categorical features."""

    # Class variables ----------------------------------------------------------

    #: str: encoding suffix (class variable)
    enc_suffix = '_SFDSML_enc'
    #: str: bin suffix  (class variable)
    bin_suffix = '_SFDSML_bin'

    column_signature=['variable','level','count','startbin','endbin','levels','n_levels']
    column_place_holder_values=['NA','NA',0.0,0.0,0.0,'NA',0.0]

    # Class utility functions --------------------------------------------------
    @classmethod
    def count_encode(cls, X):
        '''
        Class method.
        Count encode the high-cardinality categorical columns
        Return a data frame with both original and encoded columns

        Parameters
        ----------
        X : data frame
            The input data frame with high-cardinality categorical columns.

        Returns
        -------
        X_enc : data frame
            The encoded data frame, with encoded columns named with
            the enc_suffix class variable. Default for this is "_SFDSML_enc".

        '''
        cls.get_current_function_name()
        X_enc = X.copy()
        for cc in X.columns:
            cc_enc = cc+cls.enc_suffix
            X_enc[cc_enc] = X[cc].astype('object').map(X[cc].value_counts())
            X_enc[cc_enc] = X_enc[cc_enc] / np.max(X_enc[cc_enc])
            X_enc[cc_enc] = X_enc[cc_enc].astype(np.float32)
        return X_enc

    @classmethod
    def assign_column_to_bins(cls, x, bins):
        '''
        Class method. Assign column values to bins.
        Uses numpy.digitize.

        Parameters
        ----------
        x : series
            The input column.
        bins : list of real
            The start values of the bins.

        Returns
        -------
        y : series
            Assigned numeric bins.

        '''
        cls.get_current_function_name()
        x = x.dropna()
        x[x <= bins[0]] = bins[0] * \
            (1+np.sign(bins[0])*cls.eps) if bins[0] != 0 else bins[0]+cls.eps
        y = np.digitize(x, bins, right=True)
        return y

    # Object methods -----------------------------------------------------------

    def __init__(self,  cutoff_major_levels=0.3, name_of_null_level='missing'):
        '''
        Initialize object by storing the relevant information.
        Save instance attributes passed in into special
        instance variable __init_attributes__.

        Parameters
        ----------
        cutoff_major_levels : real, optional
            The fraction of levels to keep as major (unchanged) levels.
            The default is 0.3.
        name_of_null_level : str, optional
            Name to give to level containing null
            values. The default is 'missing'.

        Returns
        -------
        None.

        '''
        self.__class__.get_current_function_name()
        self.cutoff_major_levels = cutoff_major_levels
        self.name_of_null_level = name_of_null_level

        # Save a copy of the instance attributes defined during construction
        self.__init_attributes__ = self.__dict__.copy()

        return None

    def encode(self, X):
        '''
        Impute null values in high-cardinality categorical columns
        and then invoke count_encode.

        Parameters
        ----------
        X : data frame
            The input data frame with high-cardinality categorical columns.

        Returns
        -------
        X_enc : data frame
            The encoded data frame, with encoded columns named with
            the enc_suffix class variable. Default for this is "_SFDSML_enc".

        '''
        # Impute missing data NOW as it will be treated as a category
        X.fillna(value=self.name_of_null_level, inplace=True)
        X_enc = self.__class__.count_encode(X)
        return X_enc

    # Create a binned representation from the encoded dataset

    def encode_and_compute_bins(self, X):
        '''
        Count-encode the input dataframe and then bin the resulting
        encoded columns. Use 10 quantiles for binning.

        Parameters
        ----------
        X : data frame
            The input data frame with categorical variables.

        Returns
        -------
        X_bins : data frame
            DESCRIPTION.
        data frame
            A data frame with the bin limits for each numeric variable.

        '''
        self.__class__.get_current_function_name()
        X_enc = self.encode(X)
        # Bin the encoded version
        num_worker = NumericBinsWorker(
            True, True, 'quantile', 10, 'missing', 'outlier', [])
        X_bins = num_worker.setup_and_process(X_enc)
        return (X_bins, num_worker.B_ref)

    # Create a binned representation from the encoded dataset

    def encode_and_apply_bins(self, X, B_ref):
        '''
        For technical reasons, the categorical variables need to be
        encoded again. Then the calculated bins are applied.

        Parameters
        ----------
        X : data frame
            The input data frame with categorical variables.
        B_ref : data frame
            A data frame with the bin limits for each numeric variable.

        Returns
        -------
        X_enc : data frame
            The encoded data frame, with encoded columns named with
            the enc_suffix class variable. Default for this is "_SFDSML_enc".

        '''
        self.__class__.get_current_function_name()
        X_enc = self.encode(X)

        variables = B_ref['variable'].unique()
        # Now assign data to bins
        for cc in variables:
            cc0 = cc.replace(self.__class__.enc_suffix, '')
            cc_bin = cc0 + self.__class__.bin_suffix
            bins = np.array(B_ref.loc[B_ref['variable'] == cc, 'bin'].values[0].split(
                self.__class__.separator), dtype=float)
            X_enc[cc_bin] = self.__class__.assign_column_to_bins(
                X_enc[cc], bins)

        return (X_enc)

    def setup_from_object(self, XP):
        """
        Reverse engineer bins from existing processed dataframe.
        Fills instance variable *variables* with the variables found in the
        input dataframe (with names including the encoding suffix);
        fills dataframe *C_ref* with the bins for each variable and the cutoff
        for storing major levels.

        :param pandas.DataFrame XP: the processed dataframe to use as a
        blueprint.
        :raise KeyError: if the ['variable', 'startbin', 'endbin', 'levels']
        columns do not exist in the input dataframe.

        """

        self.__class__.get_current_function_name()
        sep = self.__class__.separator
        if 'variable' not in XP.columns:
            raise KeyError(str(
                self.__class__)+'.setup_from_object: Column: variable not found in input dataframe')
        if 'startbin' not in XP.columns:
            raise KeyError(str(
                self.__class__)+'.setup_from_object: Column: startbin not found in input dataframe')
        if 'endbin' not in XP.columns:
            raise KeyError(str(
                self.__class__)+'.setup_from_object: Column: endbin not found in input dataframe')
        if 'levels' not in XP.columns:
            raise KeyError(str(
                self.__class__)+'.setup_from_object: Column: levels not found in input dataframe')

        # Generate the bins: variables0 are the column names without encoding suffix
        variables0 = list(dict.fromkeys(XP['variable']))
        C_ref = pd.DataFrame(data={"variable": variables0,
                                   'bin':  pd.Series(data=[None]*len(variables0), dtype='str')})
        for nn in variables0:
            bins = XP.loc[XP['variable'] == nn, 'endbin'].dropna().tolist()
            bin0 = XP.loc[XP['variable'] == nn, 'startbin'].dropna().tolist()
            bins.insert(0, bin0[0])
            # Pack bins array and store
            C_ref.loc[C_ref.variable == nn, 'bin'] = sep.join(
                str(b) for b in bins)

        # Identify the first row with non-empty levels, count starting from 1
        tmp_df = XP.copy()
        tmp_df['major_levels_cutoff'] = tmp_df.groupby('variable').cumcount()+1
        tmp_df = tmp_df.loc[XP['levels'] != '']
        major_levels_cutoff = tmp_df.groupby(
            'variable')['major_levels_cutoff'].agg(min)
        C_ref = pd.merge(C_ref, major_levels_cutoff, on='variable')
        # Rename variable to add encoding suffix
        if C_ref.shape[0] > 0:
            C_ref['variable'] = C_ref['variable']+self.__class__.enc_suffix

        self.variables = list(dict.fromkeys(C_ref['variable']))
        self.C_ref = C_ref

        return self

    # Perform setup for each categorical column cc
    # Determine which bins will have explicit categorical levels

    def setup_column(self, X_cc, cc):
        '''
        Calculate the cutoff between untouched and binned levels for
        this column.

        Parameters
        ----------
        X_cc : series
            The input column.
        cc : str
            The name of the input column.

        Returns
        -------
        major_levels_cutoff : real
            The cutoff between untouched and binned levels for this column.

        '''
        self.__class__.get_current_function_name()

        # Sort values with max frequency bin on top and do cumulative count
        yyy = X_cc.sort_values('startbin', ascending=False).cumsum()['count']
        # Count relative to the total cumsum,
        # So we can compare to cutoff_major_levels e.g. 0.3
        yyy = yyy/max(yyy)
        n_bins = len(yyy)

        # Bins are numbered 0, 1, 2, ...
        filtered = [i for i, v in enumerate(
            yyy) if v is not None and v >= self.cutoff_major_levels]
        # Filtered_value =  [v for i, v in enumerate(yyy) if v is not None and v>=  self.cutoff_major_levels ]
        try:
            # Reverse count, so if filtered = 2 and there are 10 levels,
            # the cutoff is 10-2 = 8
            major_levels_cutoff = n_bins - min(filtered)
        except:
            major_levels_cutoff = n_bins
        return major_levels_cutoff

    def setup(self, X):
        """
        Set up bins and major levels from input dataframe.
        Fills instance variable *variables* with the variables found in the
        input dataframe (with names including the encoding suffix);
        Fills dataframe *C_ref* with the bins for each variable and the
        cutoff for storing major levels.

        :param pandas.DataFrame X: the input dataframe to use for setup.

        """

        self.__class__.get_current_function_name()
        X_bins, B_ref = self.encode_and_compute_bins(X)
        self.variables = X_bins['variable'].unique()
        C_ref = B_ref.copy()
        C_ref['major_levels_cutoff'] = np.nan

        # Input now is the frequency table
        for cc in self.variables:
            X_cc = X_bins.loc[X_bins['variable'] == cc]
            # Use pipe to apply setup
            bcutoff = X_cc.pipe(self.setup_column, cc)
            # Store cutoff for each variable
            C_ref.loc[C_ref.variable == cc, 'major_levels_cutoff'] = bcutoff
        self.C_ref = C_ref

        return self

    def process_column(self, cc, cc0, cc_bin, X_bins, X_enc):
        '''
        For each categorical column, add a column representing the actual levels
        and another representing the number of actual levels.
        The actual levels ('levels') are only persisted if the bin's rank is
        not lower than the cutoff

        Parameters
        ----------
        cc : str
            DESCRIPTION.
        cc0 : str
            DESCRIPTION.
        cc_bin : TYPE
            DESCRIPTION.
        X_bins : TYPE
            DESCRIPTION.
        X_enc : TYPE
            DESCRIPTION.

        Returns
        -------
        X_bins : TYPE
            DESCRIPTION.

        '''
        self.__class__.get_current_function_name()
        sep = self.__class__.separator
        # add an index column 1 to  max bin
        # cure index skipping value
        X_bins.reset_index(drop=True, inplace=True)
        X_bins.index += 1
        X_bins.reset_index(inplace=True)
        X_bins.rename(columns={'index': 'bin'}, inplace=True)

        X_enc.sort_values(by=cc, inplace=True)

        C_ref_cc = self.C_ref.loc[self.C_ref['variable'] == cc]
        cutoff = C_ref_cc['major_levels_cutoff'].values[0]

        tmp = X_enc.groupby([cc_bin])[cc0].apply(
            lambda x: sep.join(sorted(list(set(x)))[0:10])).reset_index()
        tmp2 = X_enc.groupby([cc_bin])[cc0].apply(
            lambda x: len(set(x))).reset_index()
        tmp.columns = ['bin', 'levels']
        # Empty levels where bin rank is less than the cutoff
        tmp.loc[tmp['bin'] < cutoff, 'levels'] = ''
        tmp2.columns = ['bin', 'n_levels']

        X_bins = X_bins.merge(tmp, how='outer', left_on='bin', right_on='bin')
        X_bins = X_bins.merge(tmp2, how='outer', left_on='bin', right_on='bin')
        # Correct cutoff if too many levels
        # Empty levels where bin rank is less than the cutoff
        X_bins.loc[X_bins['n_levels'] > 10, 'levels'] = ''
        X_bins = X_bins.apply(lambda x: x.fillna(
            0) if x.dtype != 'object' else x.fillna(''))

        return X_bins

    # Process entire data frame

    def process(self, X):
        '''
        Process the entire data frame.

        Parameters
        ----------
        X : data frame
            The input data frame with high-cardinality categorical variables.

        Returns
        -------
        R : data frame
            The resulting data frame with some levels kept intact and some
            binned by count (frequency).

        '''

        self.__class__.get_current_function_name()
        X_enc = self.encode_and_apply_bins(X, self.C_ref)
        # Bin the encoded version
        num_worker = NumericBinsWorker(
            True, True, 'quantile', 10, 'missing', 'outlier', [])
        num_worker.B_ref = self.C_ref
        num_worker.numeric = list(num_worker.B_ref['variable'])
        X_bins = num_worker.process(X_enc)

        R = pd.DataFrame(data={"variable": [], 'level': [], 'count': [], 'startbin': [], 'endbin': [],
                               "levels": [], 'n_levels': []})

        for cc in self.variables:
            cc0 = cc.replace(self.__class__.enc_suffix, '')
            cc_bin = cc0 + self.__class__.bin_suffix
            X_cc = X_bins.loc[X_bins['variable'] == cc]
            X_enc_cc = X_enc[[cc, cc0, cc_bin]]
            # Add info on levels for each bin
            R_cc = self.process_column(cc, cc0, cc_bin, X_cc, X_enc_cc)
            if R_cc is not None:
                R_cc = R_cc[R.columns]
                R = pd.concat([R, R_cc], ignore_index=True)
        # Remove the encoding suffix from the variable names
        if R.shape[0] > 0:
            R['variable'] = R['variable'].str.replace(
                self.__class__.enc_suffix, '')
        return R


#
# --- NUMERIC BINNING ---------------------------------------------------------

class NumericBinsWorker(BaseMetadataWorker):
    """
    A class for binning numerical variables.
    Contains methods for setting up a list of numeric variables from a dataframe (*setup*)
    and calculating the bin assignment for potentially a different dataframe (*process*).

    Returns a data frame with columns:\n
    * variable: the name of the original variable, e.g. Mileage.\n
    * level: a label for the numeric bin, in the form (a, b], e.g. (0.0, 10.0].\n
    * count: the number of rows in the input dataframe that fall into that bin.\n
    * startbin: the lower limit of the bin.\n
    * endbin: the upper limit of the bin.

    :param bool auto_detect_numeric:  if True, class will use *numeric_dtypes* to decide which variables are numeric;
     otherwise *numeric* is used. (Default: True).
    :param bool include_nulls: if True, include null values as a separate level; otherwise ignore null values. (Default: True).
    :param str binning_type: '[quantile', 'fixed_width', '01']. (Default: 'quantile').
    :param int n_bins_max: the maximum number of bins to generate. Should be a positive integer. (Default: 20).
    :param str name_of_null_level: name to give to level containing null values.(Default: 'missing').
    :param str name_of_outlier_level: name to give to level containing outliers. (Default: 'outlier').
    :param list[str] numeric: list of variables to treat as numeric (if *auto_detect_numeric* is False, otherwise ignored). (Default: []).

    """

    # Class variables ----------------------------------------------------------

    #: list[str] data types recognized as numeric  (class variable)
    numeric_dtypes = [np.number]
    #: list[str] data types recognized as integer  (class variable)
    integer_dtypes = [np.integer]

    column_signature=['variable','level','count','startbin','endbin']
    column_place_holder_values=['NA','NA',0.0,0.0,0.0]

    # Class utility functions --------------------------------------------------

    @classmethod
    def calculate_bin_edges(cls, v, n_bins_max):
        """
        Class method. Calculate fixed width bins.
        Used when input parameter *binning_type* is equal to 'fixed_width'.\n
        Expand the min and max bin by a small number so that we don't fall off the edges
        because of rounding errors.

        :param pandas.Series v: column of numeric data. Null values are removed.
        :param int n_bins_max: maximum number of bins to generate.
        :return: The generated bin edges.
        :rtype: list[float]

        """
        cls.get_current_function_name()
        v = v.dropna()
        v_min = min(v)
        v_max = max(v)
        # Add or remove small number; cater for negative or zero values
        v_min = v_min*(1-np.sign(v_min) *
                       cls.eps) if min(v) != 0 else min(v)-cls.eps
        v_max = v_max*(1+np.sign(v_max) *
                       cls.eps) if max(v) != 0 else max(v)+cls.eps

        # Simple method to calculate optimal n_bins (number of bins) and delta (width of a bin)
        n = v.nunique()
        n_bins = min(n_bins_max, math.floor(math.sqrt(n)))
        delta = (v_max-v_min)/n_bins
        # Round to 3 significant figures
        delta = float(('%.' + str(2) + 'e') % delta)
        # Alternative: Freedman Diaconis rule (results in more bins)
        # q3, q1 = np.percentile(v, [75 , 25])
        # delta = 2*(q3-q1)/v.size**(1/3)
        # n_bins = min(n_bins_max, round((v_max-v_min)/delta))

        bins = [np.nan]*(n_bins+1)

        bins[0] = b = v_min
        for i in range(1, n_bins+1):
            b = b+delta
            bins[i] = b
        bins[-1] = v_max
        # Just in case there is another bin that is larger than the last...
        return list(filter(lambda b: b >= v_min and b <= v_max, bins))

    @classmethod
    def calculate_quantile_bin_edges(cls, v, n_bins_max):
        """
        Class method. Calculate quantile bins.
        Used when input parameter *binning_type* is equal to 'quantile'.\n
        Expand the min and max bin by a small number so that we don't fall off the edges
        because of rounding errors.

        :param pandas.Series v: column of numeric data. Null values are removed.
        :param int n_bins_max: maximum number of bins to generate.
        :return: The generated bin edges.
        :rtype: list[float]

        """
        cls.get_current_function_name()
        v = v.dropna()
        v.sort_values(ascending=False, inplace=True)
        # If the distribution is extremely peaked, set bins appropriately
        v_counts = v.value_counts().sort_index(ascending=False)
        ratio = v_counts.iloc[0]/sum(v_counts)
        if(ratio >= 0.1):
            bin_sequence = [0, 1-ratio, 0.3, 1.]
            bin_sequence.sort()
        else:
            bin_sequence = np.linspace(0, 1, n_bins_max+1, endpoint=True)
        bins = np.quantile(v, q=bin_sequence)
        bins = list(dict.fromkeys(bins))  # remove duplicates
        # Add or remove small number; cater for negative or zero values
        bins[0] = bins[0] * (1-np.sign(bins[0]) *
                             cls.eps) if bins[0] != 0 else bins[0] - cls.eps
        bins[-1] = bins[-1]*(1+np.sign(bins[-1]) *
                             cls.eps) if bins[-1] != 0 else bins[-1]+cls.eps
        # Round to 6 significant figures and remove duplicates again
        # just in case
        bins=[float(('%.' + str(6) + 'e') % x) for x in bins]
        bins = list(dict.fromkeys(bins))  # remove duplicates

        return bins

    @classmethod
    # Create a string representation of the bin from its edges a and b
    def create_interval_label(cls, a, b, oo):
        """
        Class method.
        Create a string representation of the bin from its edges a and b in the form (a, b].\n
        If the limits are null, return a string representing the outlier.

        :param float a: lower limit of bin.
        :param float b: upper limit of bin.
        :param str oo: name of outlier bin.
        :return: The generated label.
        :rtype: str

        """
        # cls.get_current_function_name()
        if not math.isnan(a) and not math.isnan(b):
            return '('+str(a)+', '+str(b)+']'
        else:
            return oo

    @classmethod
    def assign_to_bins(cls, v, nn, bins, oo):
        """
        Class method.
        Assign values to bins, making sure we don't have boundary problems,
        then count entries for each bin.

        :param pandas.Series v: column of numeric data. Null values are removed.
        :param str nn: name of numeric column.
        :param list[float] bins: bin limits.
        :param str oo: name of outlier bin.
        :return: a data structure with columns ['level', 'count', 'variable'].
        :rtype: pandas.DataFrame

        """
        # cls.get_current_function_name()
        v = v.dropna()
        # Make sure data don't fall out of lowest bin; cater for sign and zero
        v[v <= bins[0]] = bins[0] * \
            (1+np.sign(bins[0])*cls.eps) if bins[0] != 0 else bins[0]+cls.eps
        # Return the indices of the bins to which each value in input array belongs
        vbins = np.digitize(v, bins, right=True)
        binstart = [bins[x-1] if x > 0 else np.nan for x in vbins]
        binend = [bins[x] if x < len(bins) else np.nan for x in vbins]
        # Create a label representation of the bin
        level = [cls.create_interval_label(a, b, oo)
                 for a, b in zip(binstart, binend)]
        tmp = pd.DataFrame({'level': level})
        XP_nn = tmp.value_counts().to_frame().reset_index()
        XP_nn.columns = ['level', 'count']
        XP_nn["variable"] = nn
        return XP_nn

    # Object methods -----------------------------------------------------------

    def __init__(self, auto_detect_numeric=True, include_nulls=True,
                 binning_type='quantile',
                 n_bins_max=20, name_of_null_level='missing',
                 name_of_outlier_level='outlier', numeric=[]):
        '''
        Initialize object by storing the relevant information.
        Save instance attributes passed in into special
        instance variable __init_attributes__.


        Parameters
        ----------
        auto_detect_numeric : bool, optional
            If True, class will use class variable numeric_dtypes to decide
            which variables are numeric;
            otherwise the input parameter numeric is used. The default is True.
        include_nulls : bool, optional
            if True, include null values as a separate level; otherwise
            ignore null values. The default is True.
        binning_type : str, optional
            One of ['quantile', 'fixed_width', '01'].
            The default is 'quantile'.
        n_bins_max : int, optional
            Maximum number of bins. The default is 20.
        name_of_null_level : str, optional
            Name to give to level containing null values.
            The default is 'missing'.
        name_of_outlier_level : str, optional
            Name to give to level containing outliers.
            The default is 'outlier'.
        numeric : list of str, optional
            List of variables to treat as numeric, if auto_detect_numeric is
            False; otherwise ignored. The default is [].

        Raises
        ------
        ValueError
            When n_bins_max<=0 or the binning_type is not
            one of ['quantile', 'fixed_width', '01'].

        Returns
        -------
        None.

        '''
        self.__class__.get_current_function_name()
        self.auto_detect_numeric = auto_detect_numeric
        self.binning_type = binning_type
        self.n_bins_max = n_bins_max
        self.include_nulls = include_nulls
        self.name_of_null_level = name_of_null_level
        self.name_of_outlier_level = name_of_outlier_level
        self.numeric = numeric
        # Allowable binning types
        bin_types = ['quantile', 'fixed_width', '01']
        if n_bins_max <= 0:
            raise ValueError('`bins` should be a positive integer')
        if binning_type not in bin_types:
            raise ValueError('`binning_type` should be one of',
                             ', '.join(bin_types))

        # Save a copy of the instance attributes defined during construction
        self.__init_attributes__ = self.__dict__.copy()

        return None

    def setup_from_object(self, XP):
        """
        Reverse engineer bins from existing processed dataframe.
        Used when bins generated for a dataframe are applied to a new dataframe.\n
        Fills instance variable *numeric* with the numeric variables found in the processed dataframe. \n
        Fills dataframe *B_ref* with the bin limits for each numeric variable.
        This dataframe has structure ['variable', 'bin'] where 'bin' is a string containing the collapsed list of bins
        for each variable.

        :param pandas.DataFrame XP: the processed dataframe to use as a blueprint.
        :raise KeyError: if the ['variable', 'startbin', 'endbin'] columns do not exist in the input dataframe.

        """
        self.__class__.get_current_function_name()
        sep = self.__class__.separator
        if 'variable' not in XP.columns:
            raise KeyError(str(
                self.__class__)+'.setup_from_object: Column: variable not found in input dataframe')
        if 'startbin' not in XP.columns:
            raise KeyError(str(
                self.__class__)+'.setup_from_object: Column: startbin not found in input dataframe')
        if 'endbin' not in XP.columns:
            raise KeyError(str(
                self.__class__)+'.setup_from_object: Column: endbin not found in input dataframe')

        # Generate the bins
        self.numeric = list(dict.fromkeys(XP['variable']))
        B_ref = pd.DataFrame(data={"variable": self.numeric, 'bin': pd.Series(
            data=[None]*len(self.numeric), dtype='str')})
        XP.sort_values(by=['startbin'], inplace=True)
        for nn in self.numeric:
            bins = XP.loc[XP['variable'] == nn, 'endbin'].dropna().tolist()
            bin0 = XP.loc[XP['variable'] == nn, 'startbin'].dropna().tolist()
            bins.insert(0, bin0[0])
            # Pack bins array and store
            B_ref.loc[B_ref.variable == nn, 'bin'] = sep.join(
                str(b) for b in bins)

        self.B_ref = B_ref
        return self

    def setup(self, X):
        """
        Calculate bins from input dataframe. \n
        Fills instance variable *numeric* with the numeric variables.\n
        Fills dataframe *B_ref* with the bin limits for each numeric variable.
        This dataframe has structure ['variable', 'bin'] where 'bin' is a string containing the collapsed list of bins
        for each variable.

        :param pandas.DataFrame X: the input dataframe to use for setup. Values +/-infinite are replaced with nan.
        :raise KeyError: if the input parameter *numeric* contains columns that do not exist in the input dataframe.
        :raise KeyError: if the input parameter *binning_type* contains columns that do not exist in the input dataframe.

        """

        self.__class__.get_current_function_name()

        # Detect and cast dates
        X = self.__class__.detect_and_cast_date_types(X)

        sep = self.__class__.separator
        # Types recognized as numeric columns are stored in class variable numeric_dtypes
        if self.auto_detect_numeric:
            self.numeric = X.select_dtypes(
                include=self.__class__.numeric_dtypes).columns.tolist()
        else:
            # Check columns listed in numeric exist in the data frame
            if not set(self.numeric).issubset(set(X.columns)):
                bad_numeric = []
                for bn in self.numeric:
                    if bn not in X.columns:
                        bad_numeric.append(bn)

                raise KeyError(
                    str(self.__class__)+'.setup: Numeric not in data frame: '+', '.join(bad_numeric))

        # Isolate the integers and turn them into floating point numbers
        integer_cols = X[self.numeric].select_dtypes(
            include=self.__class__.integer_dtypes).columns.tolist()
        if len(integer_cols) > 0:
            X[integer_cols] = X[integer_cols].astype(float)

        # Generate the bins
        B_ref = pd.DataFrame(
            data={"variable": self.numeric, 'bin': [None]*len(self.numeric)})

        if X.shape[0] > 0:  # any rows in data frame?
            for nn in self.numeric:
                # Replace +/-infinite with nan
                X[nn].replace([np.inf, -np.inf], np.nan, inplace=True)
                # Do not try to modify bin edges if the variable is integer (would result in type error)
                if X[nn].count() > 0:  # any non null data in column?
                    if self.binning_type == 'quantile':
                        bins = self.__class__.calculate_quantile_bin_edges(
                            X[nn], self.n_bins_max)
                    elif self.binning_type == 'fixed_width':
                        bins = self.__class__.calculate_bin_edges(
                            X[nn], self.n_bins_max)
                    elif self.binning_type == '01':
                        bins = np.linspace(0, 1, self.n_bins_max+1)
                        #must round them to avoid weird numeric precision issues
                        bins = [ round(elem, 2) for elem in bins ]
                    # Store bins array as cell
                    B_ref.loc[B_ref.variable == nn,
                              'bin'] = sep.join(map(str, bins))

        self.B_ref = B_ref
        return self

    def get_bin_end(self, b):
        """
        Return the value of the right bin border.
        For instance, if a bin is defined as "(9.999, 12.714]" this function returns 12.714.

        :param str b: the bin label.
        :return: a number representing the right bin border.
        :rtype: float or None if the label is not of the form (a, b].

        """
        # self.__class__.get_current_function_name()
        try:
            b = re.sub('\\s+', '', b).split(',')[1]
            b = re.sub('\\]', '', b)
            return float(b)
        except:
            return None

    def get_bin_start(self, a):
        """
        Return the value of the left bin border.
        For instance, if a bin is defined as "(9.999, 12.714]" this function returns 9.999.

        :param str a: the bin label.
        :return: a number representing the left bin border.
        :rtype: float or None if the label is not of the form (a, b].

        """
        # self.__class__.get_current_function_name()
        try:
            a = re.sub('\\s+', '', a).split(',')[0]
            a = re.sub('\\(', '', a)
            return float(a)
        except:
            return None

    def process_column(self, X_nn, nn):
        """
        Process each numeric column. First values are assigned to bins.
        Empty values are processed separately and added as an extra bin.

        :param pandas.Series X_nn: column of numeric data.
        :param int nn: name of the numeric column.
        :return: a data structure with columns ['level', 'count', 'variable']
        :rtype: pandas.DataFrame.

        """
        self.__class__.get_current_function_name()
        sep = self.__class__.separator
        # Replace +/-infinite with nan
        X_nn = X_nn.replace([np.inf, -np.inf], np.nan)
        # Count nulls for this column
        null_nn = X_nn.isna().sum()
        # Initialize output data frame
        XP_nn = pd.DataFrame(data={"level": [], "count": [], "variable": []})
        # Isolate bins for this variable
        B_ref_nn = self.B_ref.loc[self.B_ref.variable == nn, 'bin']

        if X_nn.count() > 0 and (not B_ref_nn.isnull().all()):
            # Unpack stored bins
            bins = np.array(B_ref_nn.values[0].split(sep), dtype=float)
            # Process non null values
            XP_nn = self.__class__.assign_to_bins(
                X_nn, nn, bins, self.name_of_outlier_level)
            # Add empty bins as they do matter if we compare to an existing binned object
            breaks = pd.IntervalIndex.from_breaks(bins).values.to_tuples()
            all_levels = [self.__class__.create_interval_label(
                a, b, self.name_of_outlier_level) for a, b in breaks]
            empty_levels = set(all_levels)-set(XP_nn['level'])
            if len(empty_levels) > 0:
                XP_nn0 = pd.DataFrame(data={"level": list(empty_levels)})
                XP_nn0['count'] = 0
                XP_nn0['variable'] = nn
                XP_nn = pd.concat([XP_nn, XP_nn0], ignore_index=True)

        # Add nulls as a new bin the name of which is specified in input
        if null_nn > 0 and self.include_nulls:
            XP_null_nn = pd.DataFrame(
                data={"level": [self.name_of_null_level], "count": [null_nn], "variable": [nn]})
            XP_nn = pd.concat([XP_nn, XP_null_nn], ignore_index=True)

        return XP_nn

    def process(self, X):
        """
        Process entire dataset. Values are assigned to bins.

        :param pandas.DataFrame X: the input dataframe.
        :return: a data structure with columns ['variable', 'level', 'count', 'startbin', 'endbin']
        :rtype: pandas.DataFrame.

        """
        self.__class__.get_current_function_name()
        if not isinstance(X, pd.core.frame.DataFrame):
            X = pd.DataFrame(X)

        X = X[self.numeric]
        # Isolate the integers annd turn them into floating point numbers
        integer_cols = X[self.numeric].select_dtypes(
            include=self.__class__.integer_dtypes).columns.tolist()
        if len(integer_cols) > 0:
            X[integer_cols] = X[integer_cols].astype(float)

        XP = pd.DataFrame(data={"level": [], "count": [],
                          "variable": [], "startbin": [], "endbin": []})

        if X.shape[0] > 0:
            for nn in self.numeric:
                # Use pipe to apply processing to each column
                XP_nn = X[nn].pipe(self.process_column, nn)
                XP = pd.concat([XP, XP_nn], ignore_index=True)
            # Reorder columns
            XP = XP[['variable', 'level', 'count']]
            # Extract stard and end value of bin from level
            XP['startbin'] = XP['level'].apply(lambda x: self.get_bin_start(x))
            XP['endbin'] = XP['level'].apply(lambda x: self.get_bin_end(x))
            XP.sort_values(by='endbin', inplace=True)
            XP.reset_index(inplace=True)
            XP.drop(['index'], axis=1, inplace=True)
        return XP


# -----------------------------------------------------------------------------
# Worker to turn datetime variables into bins
#

class DatetimeBinsWorker(NumericBinsWorker):
    """
    A class for binning numerical variables including date/datetime.
    Extends the functionality of NumericBinsWorker by handling datetimes as timestamps.
    The parameters list is the same as NumericBinsWorker.

    Returns a data frame with columns:\n
    * variable: the name of the original variable, e.g. Mileage.\n
    * level: a label for the numeric bin, in the form (a, b], e.g. (0.0, 10.0].\n
    * count: the number of rows in the input dataframe that fall into that bin.\n
    * startbin: the numeric lower limit of the bin.\n
    * endbin: the numeric upper limit of the bin.\n
    * startdate: the datetime representation of the lower limit of the bin, empty if not a date/datetime.\n
    * enddate: the datetime representation of the upper limit of the bin, empty if not a date/datetime.


    """

    # Class variables ----------------------------------------------------------

    #: list[str]: data types recognized as datetime  (class variable)
    datetime_dtypes = [np.dtype('M')]

    column_signature=['variable','level','count','startbin','endbin','startdate','enddate']
    column_place_holder_values=['NA','NA',0.0,0.0,0.0,0.0,0.0]

    # Class utility functions --------------------------------------------------

    # Object methods -----------------------------------------------------------

    def __init__(self, *args, **kwargs):
        '''
        Initialize object by storing the relevant information.
        Invokes the super class function.

        Parameters
        ----------
        *args : dict
            Arguments.
        **kwargs : dict
            Keyword arguments.

        Returns
        -------
        None.

        '''
        self.__class__.get_current_function_name()
        super(DatetimeBinsWorker, self).__init__(*args, **kwargs)
        return None

    def setup(self, X):
        """
        Calculate bins from input dataframe. \n
        Fill instance variable *datetimes* with the variables of type date/datetime. \n
        Turn their values into numeric timestamps.\n
        Then call *setup* of the superclass.

        :param pandas.DataFrame X: the input dataframe to use for setup.

        """
        self.__class__.get_current_function_name()

        # Detect and cast dates
        X = self.__class__.detect_and_cast_date_types(X)

        # Select columns of date type
        self.datetimes = X.select_dtypes(
            include=self.__class__.datetime_dtypes).columns
        # Create a dataframe where these columns are turned into timestamps (integers)
        X2 = X.copy()
        for dd in self.datetimes:
            # Check for correct coding of nulls ( = nat)
            # otherwise it converts to a funny negative number
            X2[dd] = X2[dd].apply(
                lambda x: x.value if not pd.isnull(x) else np.nan)
        return super(self.__class__, self).setup(X2)

    def setup_from_object(self, XP):
        """
        Reverse engineer bins from existing processed dataframe.
        Fill instance variable *datetimes* with the variables of type date/datetime. \n
        Then call *setup_from_object* of the superclass.

        :param pandas.DataFrame XP: the processed dataframe.
        :raise KeyError: if the 'variable' column does not exist in the input dataframe.
        """
        self.__class__.get_current_function_name()
        self.datetimes = []
        if 'variable' not in XP.columns:
            raise KeyError(str(
                self.__class__)+'.setup_from_object: Column: variable not found in input dataframe')

        # Select columns of date type, this time from a result of binning
        if 'startdate' in XP.columns:
            tmp_df = XP[~XP['startdate'].isna()]
            self.datetimes = list(set(tmp_df['variable']))

        return super(self.__class__, self).setup_from_object(XP)

    def process(self, X):
        """
        Process entire dataset. Values are assigned to bins. \n
        Turn date/datetime variables into numeric timestamps. \n
        Then call the *process* function of the superclass.\n
        At the end, turn *startbin* and *endbin* back into date/datetime format (*startdate*, *enddate*).

        :param pandas.DataFrame X: the input dataframe.
        :return: a data structure with columns ['variable', 'level', 'count', 'startbin', 'endbin', 'startdate', 'enddate']
        :rtype: pandas.DataFrame.

        """
        self.__class__.get_current_function_name()
        X2 = X.copy()
        # Create a dataframe where date columns are turned into timestamps (integers)
        for dd in self.datetimes:
            # Check for nulls ( = nat)
            # otherwise it converts to a funny negative number
            X2[dd] = X2[dd].apply(
                lambda x: x.value if not pd.isnull(x) else np.nan)
        result = super(self.__class__, self).process(X2)
        # Add startdate and enddate columns containing the dates for startbin and endbin
        # Removed parameter infer_datetime_format as it will be removed in the future
        # and replaced by a default processing of the format, which "should" be safe
        for dd in self.datetimes:
            result.loc[result['variable'] == dd, 'startdate'] = pd.to_datetime(
                result.loc[result['variable'] == dd, 'startbin'])
            result.loc[result['variable'] == dd, 'enddate'] = pd.to_datetime(
                result.loc[result['variable'] == dd, 'endbin'])
        return result


#
# --- SUMMARY STATISTICS ------------------------------------------------------

# Class to calculate descriptive statistics
#
class DescribeWorker(BaseMetadataWorker):
    """
    A class for generating descriptive statistics for all variables.
    Contains methods for retrieving selected parts of the output dataframe.

    Returns a data frame with columns:\n
    * variable: the name of the original variable \n
    * dtype: the data type \n
    * count_nulls: the number of null values \n
    * count_invalid: the number of invalid values (+/- inf, numeric only) \n
    * count_empty: the number of empty values (categorical) \n
    * count: the total count of values \n
    * top: the most frequent level (categorical) \n
    * mean: the arithmetic mean (numeric) \n
    * std: the standard deviation (numeric) \n
    * min: the minimum value (numeric) \n
    * 25%: the 25th percentile (numeric) \n
    * 50%: the median (numeric) \n
    * 75%: the 75th percentile (numeric) \n
    * max: the minimum value (numeric) \n
    * unique: the number of unique values \n
    * max_freq: the maximum count out of all values \n
    * min_freq: the minimum count out of all values \n
    * median_freq: the median count out of all values \n
    * max_to_median_freq_ratio: the ratio of max_freq/median_freq \n
    * max_freq_to_count_ratio: the ratio of max_freq/count \n
    * unique_to_count_ratio:     the ratio of unique/count \n


    :param bool datetime_is_numeric: Whether to treat datetime dtypes as numeric. Directive to pandas.Describe. (Default: True).
    :param str include: Which columns to include. Directive to pandas.Describe. (Default: 'all').
    :param bool empty_as_null: Treat empty strings as null. (Default: False).

    """

    # Class variables ----------------------------------------------------------

    #: list[str]: data types recognized as datetime  (class variable)
    datetime_dtypes = [np.dtype('M')]

    #: list[str]: desired order of columns  (class variable)
    col_order = ['metric', 'variable', 'value']

    describe_cols=[
     'count',
     'top',
     'mean',
     'min',
     '25%',
     '50%',
     '75%',
     'max',
     'std']

    # Columns with values that can be turned back into datetimes
    columns_for_datetimes=[
     'mean',
     'min',
     '25%',
     '50%',
     '75%',
     'max']    
    
    column_signature=['variable',
     'dtype',
     'count_nulls',
     'count_invalid',
     'count_empty',
     'count',
     'top',
     'mean',
     'min',
     '25%',
     '50%',
     '75%',
     'max',
     'std',
     'unique',
     'max_freq',
     'min_freq',
     'median_freq',
     'max_to_median_freq_ratio',
     'max_freq_to_count_ratio',
     'unique_to_count_ratio']

    column_place_holder_values=['NA','NA',0,0,0,0,'NA',0.0,0.0,0.0,0.0,0.0,0.0,0.0,
                                0,0,0,0.0,0.0,0.0,0.0,]

    # Class utility functions --------------------------------------------------

    # Object methods -----------------------------------------------------------

    def __init__(self, datetime_is_numeric=True, include='all',
                 empty_as_null=False):
        '''
        Initialize object by storing the relevant information.
        Save instance attributes passed in into special
        instance variable __init_attributes__.

        Parameters
        ----------
        datetime_is_numeric : bool, optional
            Whether to treat datetime dtypes as numeric. Directive to pandas.Describe. The default is True.
        include : str, optional
            Which columns to include. Directive to pandas.Describe. The default is 'all'.
        empty_as_null : bool, optional
            Treat empty strings as null. The default is False.

        Returns
        -------
        None.

        '''
        self.__class__.get_current_function_name()
        self.datetime_is_numeric = datetime_is_numeric
        self.include = include
        self.empty_as_null = empty_as_null
        # Save a copy of the instance attributes
        # that were defined during construction
        self.__init_attributes__ = self.__dict__.copy()

        return None

    def setup(self, X):
        '''
        This function does all the work.
        Returns a data frame with columns:
        variable: the name of the original variable
        dtype: the data type
        count_nulls: the number of null values
        count_invalid: the number of invalid values (+/- inf, numeric only)
        count_empty: the number of empty values (categorical)
        count: the total count of values
        top: the most frequent level (categorical)
        mean: the arithmetic mean (numeric)
        std: the standard deviation (numeric)
        min: the minimum value (numeric)
        25%: the 25th percentile (numeric)
        50%: the median (numeric)
        75%: the 75th percentile (numeric)
        max: the minimum value (numeric)
        unique: the number of unique values
        max_freq: the maximum count out of all values
        min_freq: the minimum count out of all values
        median_freq: the median count out of all values
        max_to_median_freq_ratio: the ratio of max_freq/median_freq
        max_freq_to_count_ratio: the ratio of max_freq/count
        unique_to_count_ratio:     the ratio of unique/count

        Parameters
        ----------
        X : data frame
            The input data frame.

        Raises
        ------
        RuntimeError
            When an error is encountered running pandas.describe.
            Might signal that a new pandas version has changed some
            key parameters or behaviour.

        Returns
        -------
        data frame
            The descriptive statistics for every variable.

        '''
        self.__class__.get_current_function_name()

        # Detect and cast dates
        X = self.__class__.detect_and_cast_date_types(X)

        # First count invalid, empty and nulls
        count_nulls = X.isna().sum()
        count_invalid = X[X.isin([np.inf, -np.inf])].count()
        count_empty = X[X == ''].count()
        describe_X0 = pd.DataFrame(
            {'count_nulls': count_nulls, 'count_invalid': count_invalid, 'count_empty': count_empty})

        # If datetime_is_numeric is True, turn datetimes into numbers for processing
        X2 = X.copy()
        if self.datetime_is_numeric:
            # Select columns of date type
            self.datetimes = X2.select_dtypes(
                include=self.__class__.datetime_dtypes).columns
            # Create a dataframe where these columns are turned into timestamps (integers)
            for dd in self.datetimes:
                # Check for correct coding of nulls ( = nat)
                # otherwise it converts to a funny negative number
                X2[dd] = X2[dd].apply(
                    lambda x: x.value if not pd.isnull(x) else np.nan)
        else:
            self.datetimes=[]
            
        # Replace +/- inf and optionally empty string with nulls,
        # take a copy to avoid modifying the original dataframe
        if self.empty_as_null:
            invalid_list = [np.inf, -np.inf, '']
        else:
            invalid_list = [np.inf, -np.inf]
        X1 = X2.replace(invalid_list, np.nan).copy()

        try:
            describe_X1 = X1.describe(include=self.include)

        except Exception as e: # Catch exceptions in pandas.describe
            raise RuntimeError('An exception occurred in {this_class} {function}: {error}'.\
                               format(this_class=self.__class__, function='pandas.describe',error=e))

        describe_X1 = describe_X1.transpose()

        # if there are no categorical columns, pandas describe does not produce
        # a column called 'top'
        # conversely, a number of numerical metrics are not produced for
        # purely categorical data
        missing_cols = set(self.__class__.describe_cols)-set(describe_X1.columns)
        for mc in missing_cols:
            if mc=='top':
                describe_X1[mc]=None
            else:
                describe_X1[mc]=np.nan


        # Adding .astype(str) stores the label e.g. dtype('O') is stored as object
        describe_X2 = pd.Series(X.dtypes.astype(str), name='dtype')

        # Adding counts for categorical columns
        N = X.shape[0]
        n_unique, max_freq, min_freq, median_freq, max_median_freq_ratio, \
        max_freq_to_N_ratio, cardinality_to_N_ratio = \
        [], [], [], [], [], [], []
        for cc in X.columns:
            frequencies = X[cc].value_counts()
            cardinality_cc = len(frequencies.tolist())
            max_freq_cc = frequencies.max()
            min_freq_cc = frequencies.min()
            median_freq_cc = frequencies.median()

            max_median_freq_ratio_cc = round(max_freq_cc/median_freq_cc, 4)
            max_freq_to_N_ratio_cc = round(max_freq_cc/N, 4)
            cardinality_to_N_ratio_cc = cardinality_cc/N
            # accumulate
            n_unique.append(cardinality_cc)
            min_freq.append(min_freq_cc)
            max_freq.append(max_freq_cc)
            median_freq.append(median_freq_cc)
            max_median_freq_ratio.append(max_median_freq_ratio_cc)
            max_freq_to_N_ratio.append(max_freq_to_N_ratio_cc)
            cardinality_to_N_ratio.append(cardinality_to_N_ratio_cc)

        describe_X3 = pd.DataFrame({'n_unique': n_unique, 'max_freq': max_freq, 'min_freq': min_freq, 'median_freq': median_freq,
                                    'max_to_median_freq_ratio': max_median_freq_ratio,
                                    'max_freq_to_count_ratio': max_freq_to_N_ratio, 'unique_to_count_ratio': cardinality_to_N_ratio})
        describe_X3.index = X.columns

        # Put everything together
        describe_X = pd.concat(
            [describe_X2, describe_X0, describe_X1, describe_X3], axis=1)

        describe_X.reset_index(inplace=True)
        describe_X.rename({'index': 'variable'}, axis=1, inplace=True)
        describe_X.sort_values(by=['variable'], inplace=True)

        if 'count' in describe_X.columns:
            describe_X = describe_X.astype({'count': 'int64'})
        # Delete freq since we have max_freq and unique since we have n_unique
        if 'unique' in describe_X.columns:
            describe_X.drop(columns=['unique'], inplace=True)
        if 'freq' in describe_X.columns:
            describe_X.drop(columns=['freq'], inplace=True)

        # Rename n_unique to unique
        describe_X.rename(columns={'n_unique': 'unique'}, inplace=True)


        # If we turned dates into numbers, turn back some generated metrics into dates
        if len(self.datetimes)>0:
            datevars_and_measures = [(a,b) for a in self.datetimes for b in self.__class__.columns_for_datetimes ]
            for dd,nn in datevars_and_measures:
                # astype(..) formats by removing info beyond seconds.
                describe_X.loc[describe_X['variable'] == dd, nn] = pd.to_datetime(
                    describe_X.loc[describe_X['variable'] == dd, nn]).astype('datetime64[s]')
            # Remove standard deviation numeric value, as it looks odd now
            for dd in self.datetimes:
                describe_X.loc[describe_X['variable'] == dd, 'std'] = np.nan
        
        self.describe_X = describe_X
        self.describe_columns = describe_X.columns.tolist()

        return self


    def process(self, X=None):
        '''
        Return the dataframe containing the complete descriptive statistics.
        Wrapper function to align with other metadata worker classes.

        Parameters
        ----------
        X : data frame, optional
            DESCRIPTION. The default is None.
            IGNORED.

        Returns
        -------
        data frame
            The dataframe containing the complete descriptive statistics.

        '''
        return self.get_description_data_frame()

    # Reverse engineer descriptive statistics from existing binned object

    def setup_from_object(self, W):
        '''
        Reverse engineer from existing descriptive statistics.

        Parameters
        ----------
        W : data frame
            The input descriptive statistics data frame.

        Returns
        -------
        self
            This object.

        '''
        self.__class__.get_current_function_name()
        self.describe_X = W
        self.describe_columns = W.columns.tolist()
        return self


    def get_description_data_frame(self):
        '''
        Return the dataframe containing the complete descriptive statistics.

        Returns
        -------
        data frame
            The dataframe containing the complete descriptive statistics.

        '''
        self.__class__.get_current_function_name()
        return self.describe_X


    def get_variables(self):
        '''
        Return a list of the variables in the original data frame.

        Returns
        -------
        list
            List of the variables in the original data frame.

        '''
        self.__class__.get_current_function_name()
        return list(set(self.describe_X['variable']))


    def get_metrics(self):
        '''
        Return a list of the available metrics

        Returns
        -------
        metrics : list
            List of calculated metrics.

        '''
        self.__class__.get_current_function_name()
        metrics = list(set(self.describe_columns)-{'variable', 'dtype'})
        return metrics


    def get_data_types(self):
        '''
        Return a list of the data types in the original data frame

        Returns
        -------
        list
            List of data types in original data frame.

        '''
        self.__class__.get_current_function_name()
        return list(set(self.describe_X['dtype']))


    def get_variable(self, variable):
        '''
        Return the descriptive statistics of one or more specific variables

        Parameters
        ----------
        variable : str or list, tuple
            Variable(s) to return information for.

        Returns
        -------
        data frame
            The descriptive statistics for the selected variable(s).

        '''
        self.__class__.get_current_function_name()
        if not isinstance(variable, (list, tuple)):
            variable = [variable]
        return self.describe_X.loc[self.describe_X['variable'].isin(variable)]


    def get_metric(self, metric):
        '''
        Return the descriptive statistics for one or more specific metrics

        Parameters
        ----------
        metric : str or list, tuple
            Metric(s) to return information for.

        Returns
        -------
        data frame
            The descriptive statistics for the selected metric(s).

        '''
        self.__class__.get_current_function_name()
        if not isinstance(metric, (list, tuple)):
            metric = [metric]
        metric.append('variable')
        return self.describe_X[metric]


    def get_data_type(self, dtype):
        '''
        Return the descriptive statistics for one or more data types

        Parameters
        ----------
        dtype : str or list, tuple
            Data type(s) to return information for.

        Returns
        -------
        data frame
            The descriptive statistics for the selected data type(s).

        '''
        self.__class__.get_current_function_name()
        if not isinstance(dtype, (list, tuple)):
            dtype = [dtype]
        return self.describe_X.loc[(self.describe_X['dtype'].isin(dtype))]


#
# --- CORRELATIONS AND ASSOCIATIONS -------------------------------------------

# Class to calculate numeric correlations
# method: pearson, kendall, spearman
#
class CorrelationWorker(BaseMetadataWorker):
    """A class for generating linear correlation between numerical variables."""

    # Class variables ----------------------------------------------------------

    column_signature=['variable1','variable2','correlation','corr_bin','variable12']
    column_place_holder_values=['NA','NA',0.0,'NA','NA']

    #: list[str]: data types recognized as numeric  (class variable)
    numeric_dtypes = [np.number]
    #: list[float]: bins to discretize correlation values [-1, 1] (class variable)
    correlation_bins = [-np.inf, -0.75, -0.5, -0.3, 0.3, 0.5, 0.75, 1]
    #: list[str]: names associated to bins
    correlation_names = ['-H', '-M', '-L', 'VL', 'L', 'M', 'H']

    # Class utility functions --------------------------------------------------

    # Object methods -----------------------------------------------------------

    def __init__(self, method='spearman'):
        '''
        Initialize object by storing the relevant information.
        Save instance attributes passed in into special
        instance variable __init_attributes__.

        Parameters
        ----------
        method : str, optional
            Correlation method. One of ['pearson','kendall','spearman'].
            Uses pandas.DataFrame.corr.
            The default is 'spearman'.

        Returns
        -------
        None.

        '''
        self.__class__.get_current_function_name()
        self.method = method
        # Save a copy of the instance attributes defined during construction
        self.__init_attributes__ = self.__dict__.copy()

        return None

    def setup(self, X):
        """
        Define variable pairs from input dataframe.
        Fills instance variable *correlation_columns* with the numeric variable pairs.

        :param pandas.DataFrame X: the input dataframe for setup.
        """
        self.__class__.get_current_function_name()

        # Detect and cast dates
        X = self.__class__.detect_and_cast_date_types(X)

        self.correlation_columns = X.select_dtypes(
            include=self.__class__.numeric_dtypes).columns.tolist()
        return self

    def setup_from_object(self, XP):
        """
        Reverse engineer bins from existing processed dataframe.
        Fills instance variable *correlation_columns* with the numeric variable pairs.

        :param pandas.DataFrame XP: the processed dataframe.
        :raise KeyError: if the ['variable1', 'variable2'] columns do not exist in the input dataframe.
        """

        self.__class__.get_current_function_name()
        if 'variable1' not in XP.columns:
            raise KeyError(str(
                self.__class__)+'.setup_from_object: Column: variable1 not found in input dataframe')
        if 'variable2' not in XP.columns:
            raise KeyError(str(
                self.__class__)+'.setup_from_object: Column: variable2 not found in input dataframe')

        self.correlation_columns = list(
            set(XP['variable1'].tolist()+XP['variable2'].tolist()))
        return self

    def process(self, X):
        '''
        Calculate the linear correlation for every numeric
        variable pair of the input data frame.

        Parameters
        ----------
        X : data frame
            The input data frame.

        Returns
        -------
        correlation : data frame
            A dataframe with calculated correlation for every
            distinct variable pair.

        '''
        self.__class__.get_current_function_name()
        correlation = X[self.correlation_columns].corr(method=self.method)
        #replace Nan (when variables have only one value) with 0
        correlation.fillna(0,inplace=True)
        # Make sure rows and columns are always sorted the same way,
        # when removing the lower triangle
        correlation.sort_index(axis=0, inplace=True)
        correlation.sort_index(axis=1, inplace=True)
        corr_index = correlation.index
        corr_columns = correlation.columns
        # Keep upper triangle, the rest is set to Nan
        indices_to_remove = np.triu_indices(len(self.correlation_columns))
        correlation=correlation.to_numpy()
        correlation[indices_to_remove]=np.nan
        correlation = pd.DataFrame(correlation, columns=corr_columns, index=corr_index)
        correlation = correlation.stack().reset_index()
        correlation.columns = ['variable1', 'variable2', 'correlation']
        correlation['variable12'] = correlation['variable1'] + \
            self.__class__.separator + correlation['variable2']

        correlation['corr_bin'] = pd.cut(correlation['correlation'], self.__class__.correlation_bins,
                                         labels=self.__class__.correlation_names)
        correlation['variable12'] = correlation['variable1'] + \
            self.__class__.separator + correlation['variable2']

        return correlation


#
#
# --- INTERNAL ENTRY POINTs ---------------------------------------------------


def get_conditions_for_regrouping(XP_cc,
                                  use_imbalance_for_low_cardinality=False,
                                  max_categorical_levels=30):
    """
    Decide which categorical variables should be regrouped
    based on how many levels there are or optionally
    on how imbalanced they are.

    :param pandas.DataFrame XP_cc: the processed categorical column we want to inspect
    :param bool use_imbalance_for_low_cardinality: if True, regroup levels based on imbalance, not just on number of levels
    :param int max_categorical_levels: the minimum number of levels for regrouping (if *use_imbalance_for_low_cardinality* is False)
    :raise KeyError: if the *count* column does not exist in the input dataframe.

    :return: whether or not categorical variable needs regrouping
    :rtype: bool
    """
    if 'count' not in XP_cc.columns:
        raise KeyError(
            'get_conditions_for_regrouping: Column: count not found in input dataframe')

    # Number of unique levels
    n_unique = XP_cc.shape[0]
    # Max frequency of levels
    max_freq = XP_cc['count'].max()
    # Median frequency of levels
    median_freq = XP_cc['count'].median()

    # Condition 1: we have more than 30 levels
    #set to False if max_categorical_levels=-1
    mask1 = max_categorical_levels != -1 and n_unique >= max_categorical_levels

    # Conditions 2 are on imbalance, we can decide not to apply them
    if use_imbalance_for_low_cardinality:
        # Condition 2a: we have between 2 and 30 levels
        mask2a = n_unique > 2 & n_unique < max_categorical_levels
        # Condition 2b: the ratio of max vs median frequency is 'high enough'
        mask2b = max_freq/median_freq > 10
    else:
        mask2a = False
        mask2b = False

    mask = (mask1) | ((mask2a) & (mask2b))
    if mask:
        regroup = True
    else:
        regroup = False

    return regroup


def calculate_metadata_categorical(X, name_of_null_level,
                                   use_imbalance_for_low_cardinality,
                                   max_categorical_levels):

    """
    Process input categorical variables and
    either create a metadata dataframe with counts for all levels
    or create a grouped metadata dataframe with only few explicitly named levels.

    :param pandas.DataFrame X: the input dataframe
    :param bool use_imbalance_for_low_cardinality: if True, regroup levels based on imbalance, not just on number of levels
    :param int max_categorical_levels: the minimum number of levels for regrouping (if *use_imbalance_for_low_cardinality* is False)
    :raise KeyError: if the *count* column does not exist in the input dataframe.

    :return: tuple of objects: processed categories, grouped categories, category worker, group worker, list of columns that have been regrouped
    :rtype: tuple
    """

    # First calculate the level counts for all categorical variables
    cat_worker_parms = {'auto_detect_categories': True, 'include_nulls': True, 'empty_as_null': True,
                        'name_of_null_level': name_of_null_level, 'categories': []}
    cat_worker = CategoricalFrequenciesWorker(**cat_worker_parms)
    tmp_cat_counts = cat_worker.setup_and_process(X)
    categories = cat_worker.categories

    # If there are no categories, skip this and set candidate_cats to an empty list
    if len(categories)>0:
        # Create a temporary summary stats object for the categorical variables
        tmp_desc_worker = DescribeWorker(datetime_is_numeric=True, include='all', empty_as_null=False)
        tmp_desc_df = tmp_desc_worker.setup_and_process(X[categories])
    
        # Choose columns we want to carry forward: candidate_cats
        # ...remove columns with a single value
        # ...remove columns with as many values as the number of rows
        if tmp_desc_df.shape[0] > 0:
            candidate_cats = tmp_desc_df.loc[(tmp_desc_df['unique'] > 1 & (
                tmp_desc_df['unique'] < tmp_desc_df['count'])), 'variable']
        else:
            candidate_cats = []
    else:
       candidate_cats = [] 

    # Divide these into columns to regroup or not to regroup
    regroup = []
    for cc in candidate_cats:
        XP_cc = tmp_cat_counts.loc[tmp_cat_counts['variable'] == cc]
        # Use pipe to apply transformations
        if XP_cc.pipe(get_conditions_for_regrouping, use_imbalance_for_low_cardinality, max_categorical_levels):
            regroup.append(cc)

    # Finally...
    # Apply normal counts to columns where regroup is False , again (unavoidable)
    cat_json_schema, cat_json_body, cat_json_df = \
        CategoricalFrequenciesWorker.pack_json(cat_worker_parms,
                                               X.drop(regroup, axis=1), 'md_cat_parms', 'md_cat_df')

    # Apply regrouping to columns where regroup is True
    worker_parms = {'cutoff_major_levels': 0.3, 'name_of_null_level': name_of_null_level}
    catgroup_json_schema, catgroup_json_body, catgroup_json_df = \
        CategoricalFrequenciesGrouper.pack_json(worker_parms,
                                                X[regroup], 'md_catgroup_parms', 'md_catgroup_df')

    return (cat_json_schema, cat_json_body, cat_json_df,
            catgroup_json_schema, catgroup_json_body, catgroup_json_df)


def unpack_data_metadata(mdd_json, supply_place_holders=False):
    """
    Unpack the entire metadata json and create metadata workers and dataframes.

    :param str mdd_json: the input json string

    :return: tuple of objects: workers and processed dataframes
    :rtype: tuple
    """
    # Turn json string into dictionary
    received_json = json.loads(mdd_json)

    # Categorical frequencies
    received_cat_worker, received_cat_df = CategoricalFrequenciesWorker.unpack_json(
        received_json, return_df=True)
    # Categorical grouped frequencies
    received_catgroup_worker, received_catgroup_df = CategoricalFrequenciesGrouper.unpack_json(
        received_json, return_df=True)
    # Numeric bins including Dates
    received_num_worker, received_num_df = DatetimeBinsWorker.unpack_json(
        received_json, return_df=True)
    # Descriptive statistics
    received_desc_worker, received_desc_df = DescribeWorker.unpack_json(
        received_json, return_df=True)
    # Correlations
    received_corr_worker, received_corr_df = CorrelationWorker.unpack_json(
        received_json, return_df=True)

    if supply_place_holders:
        if received_num_df.shape[0]==0:
            received_num_df=DatetimeBinsWorker.place_holder_result()
        if received_cat_df.shape[0]==0:
            received_cat_df=CategoricalFrequenciesWorker.place_holder_result()
        if received_catgroup_df.shape[0]==0:
            received_catgroup_df=CategoricalFrequenciesGrouper.place_holder_result()
        if received_desc_df.shape[0]==0:
            received_desc_df=DescribeWorker.place_holder_result()
        if received_corr_df.shape[0]==0:
            received_corr_df=CorrelationWorker.place_holder_result()

    return (received_cat_worker, received_catgroup_worker, received_num_worker, received_desc_worker, received_corr_worker,
            received_cat_df, received_catgroup_df, received_num_df, received_desc_df, received_corr_df)

#
#
# --- USER ENTRY POINT --------------------------------------------------------


def calculate_data_metadata(df, target,
                            correlation_method='spearman',
                            numeric_binning_type='quantile',
                            numeric_bins_max=10,
                            name_of_null_level='missing',
                            name_of_outlier_level='outlier',
                            use_imbalance_for_low_cardinality=False,
                            max_categorical_levels=-1,
                            supply_place_holders=False):
    '''
    Process input variables and create metadata representations.

    Parameters
    ----------
    df : data frame
        The input dataframe.
    target : string
        The name of the target variable (can be null if we don't have a target).
    numeric_binning_type : string
        Type of binning for continuous variables ('quantile', 'fixed_width' or '01'. Default:'quantile').
    numeric_bins_max : integer
        Maximum number of numeric bins; must be >0. (Default:10)
    name_of_null_level : string
        Name to give to level containing null values.(Default: 'missing').
    name_of_outlier_level : string
        Name to give to level containing outliers. (Default: 'outlier').
    correlation_method : string
        The method to use for linear correlation ('spearman', 'pearson' or 'kendall'. Default: 'spearman').
    use_imbalance_for_low_cardinality : boolean
        If True, regroup levels based on imbalance, not just on number of levels.
        NOTE: Grouping not currently used: set this to False.
    max_categorical_levels : integer
        The minimum number of levels for regrouping (if use_imbalance_for_low_cardinality is False).
        NOTE: Grouping not currently used: set this to -1.
    supply_place_holders : boolean, optional
        If True and the binned result is empty, create an empty row. The default is False.

    Returns
    -------
    complete_json : string
        The complete metadata in JSON format.
    cat_df : data frame
        Metadata for categorical variables.
    catgroup_df : data frame
        Metadata for grouped categorical variables (not currently used).
    num_df : data frame
        Metadata for numeric  variables.
    desc_df : data frame
        Descriptive statistics.
    corr_df : data frame
        Metadata for linear pair correlations.

    '''

    #FOR NOW, GROUPING IS DISABLED BY THESE HARD-WIRED OPTIONS:
    use_imbalance_for_low_cardinality=False
    max_categorical_levels=-1

    # Identify predictors as all incoming columns minus the target
    predictors = list(df.columns)
    if target is not None and target in predictors:
        predictors.remove(target)
    # Now X is the data frame we are going to process
    X = df[predictors]

    # Process categorical variables
    cat_json_schema, cat_json_body, cat_json_df, \
        catgroup_json_schema, catgroup_json_body, catgroup_json_df = \
        calculate_metadata_categorical(
            X, name_of_null_level, use_imbalance_for_low_cardinality, max_categorical_levels)


    # Process numeric variables (including datetime)
    worker_parms = {'auto_detect_numeric': True, 'include_nulls': True,
                    'binning_type': numeric_binning_type,
                    'n_bins_max': numeric_bins_max,
                    'name_of_null_level': name_of_null_level,
                    'name_of_outlier_level': name_of_outlier_level,
                    'numeric': []}
    num_json_schema, num_json_body, num_json_df = \
        DatetimeBinsWorker.pack_json(worker_parms,
                                     X, 'md_num_parms', 'md_num_df')


    # Summary stats
    worker_parms = {'datetime_is_numeric': True, 'include': 'all', 'empty_as_null': True}
    desc_json_schema, desc_json_body, desc_json_df = \
        DescribeWorker.pack_json(worker_parms, X, 'md_desc_parms', 'md_desc_df')


    # Correlations
    worker_parms = {'method': correlation_method}
    corr_json_schema, corr_json_body, corr_json_df = \
        CorrelationWorker.pack_json(worker_parms,
                                    X, 'md_corr_parms', 'md_corr_df')


    # PACKAGE UP

    # Create a schema for extracting information
    json_schema = {**cat_json_schema, **catgroup_json_schema, **
                   num_json_schema, **desc_json_schema, **corr_json_schema}
    json_schema = json.dumps(json_schema)  # turn into a json string
    json_schema = {'schema': json_schema}  # create a dictionary

    # Build json: the schema and then the json body for each metadata class
    complete_json = {**json_schema, **cat_json_body, **catgroup_json_body,
                     **num_json_body, **desc_json_body, **corr_json_body}

    # Turn dictionary into json string
    complete_json = json.dumps(complete_json)

    # Restore data frames

    cat_df = pd.DataFrame(json.loads(cat_json_df))
    num_df = pd.DataFrame(json.loads(num_json_df))
    catgroup_df = pd.DataFrame(json.loads(catgroup_json_df))
    desc_df = pd.DataFrame(json.loads(desc_json_df))
    corr_df = pd.DataFrame(json.loads(corr_json_df))

    if supply_place_holders:
        if num_df.shape[0]==0:
            num_df=DatetimeBinsWorker.place_holder_result()
        if cat_df.shape[0]==0:
            cat_df=CategoricalFrequenciesWorker.place_holder_result()
        if catgroup_df.shape[0]==0:
            catgroup_df=CategoricalFrequenciesGrouper.place_holder_result()
        if desc_df.shape[0]==0:
            desc_df=DescribeWorker.place_holder_result()
        if corr_df.shape[0]==0:
            corr_df=CorrelationWorker.place_holder_result()

    return (complete_json, cat_df, catgroup_df, num_df, desc_df, corr_df)




# MAIN -----------------------------------------------------------------------
if __name__ == '__main__':
    # just quick tests
    # help(BaseMetadataWorker.setup_and_process)
    help(DescribeWorker.setup)


