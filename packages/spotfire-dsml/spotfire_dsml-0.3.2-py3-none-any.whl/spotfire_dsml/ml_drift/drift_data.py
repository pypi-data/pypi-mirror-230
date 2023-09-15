#
# --- LIBRARIES ---------------------------------------------------------------
import numpy as np
import pandas as pd
import math
from scipy.stats import chi2_contingency as chi2

#spotfire-dsml modules
from spotfire_dsml.ml_metadata import metadata_data as mdd
from spotfire_dsml.ml_metadata import metadata_model as mdm

# ---------------------------------------------------------------------------
# DRIFT DETECTOR CLASSES  ---------------------------------------------------

class BaseDriftDetector():
    '''
    Base class for calculating drift.
    '''

    # These needed to be superseded for each class
    column_signature=['variable','distance','drift']
    column_place_holder_values=['NA',0.0,0.0]
    drift_variable='drift'

    @classmethod
    def place_holder_result(cls):
        '''
        Returns a new dataframe with only one row of generic values.
        Used to supply a result with the correct column names and types
        where this matters (e.g. in a Spotfire data function).
        Uses column names and data types as specified in each subclass.
        '''
        return pd.DataFrame(data=[cls.column_place_holder_values],
                            columns=cls.column_signature)

    def setup_and_process(self, X, Y):
        '''
        Perform the current object setup method, followed by the process
        method.

        Parameters
        ----------
        X : data frame
            The baseline dataframe.
        Y : data frame
            The new dataframe to compare to X.

        Returns
        -------
        data frame
            The drift result.

        '''
        self.setup(X)
        return self.process(Y)


class CosineDriftDetector(BaseDriftDetector):
    '''
    Class for calculating drift using cosine distance.
    '''
    column_signature=['variable','distance','cosine_drift']
    column_place_holder_values=['NA',0.0,0.0]
    drift_variable='cosine_drift'

    # class utility functions ---

    @classmethod
    def post_process(cls, D):
        '''
        Create a normalized drift column based on distance metrics results.
        For cosine drift, it is simply the cosine distance, since
        this is already bound between 0 and 1.

        Parameters
        ----------
        D : data frame
            The calculated drift dataframe.

        Returns
        -------
        D : data frame
            The drift dataframe with added drift column.

        '''
        D[cls.drift_variable] = D['distance']
        return D

    # object methods ---

    def __init__(self, count_variable='count'):
        '''
        Initialize object by storing the relevant information.

        Parameters
        ----------
        count_variable : string, optional
            The name of the metadata column representing a count
            (frequency) of values for each variable of the original dataset.
            The default is 'count'.

        Returns
        -------
        None.

        '''
        self.count_variable = count_variable
        return None

    # use metadata as input
    def setup(self, X):
        '''
        Setup using the input metadata.
        categories: the list of variables in the dataset
        n_categories: the number of variables in the dataset
        X_ref: the reference dataset
        is_setup: confirm the setup happened (legacy, not really used)

        Parameters
        ----------
        X : data frame
            DESCRIPTION.

        Returns
        -------
        self

        '''
        self.categories = X['variable'].unique().tolist()  # the number of  columns is fixed
        self.n_categories = len(self.categories)
        self.X_ref = X  # the possible values depend on the dataset
        self.is_setup = True
        return self

    def cosine_distance(self, x, y):
        '''
        Calculate the cosine distance between two vectors of counts.
        Cosine distance = 1 - Cosine similarity.
        Cosine similarity measures the similarity between two vectors of
        an inner product space. It is measured by the cosine of the angle
        between two vectors and determines whether two vectors are pointing
        in roughly the same direction. It is often used to measure document
        similarity in text analysis. Whereas documents are represented by
        word frequency vectors, in this case datasets are represented by bin
        (or category) frequency vectors for each variable.

        Formula:
            x*y/(||x||*||y||)

        Parameters
        ----------
        x : list
            The first vector to be compared.
        y : list
            The second vector to be compared.

        Returns
        -------
        numeric
            Cosine distance between x and y.

        '''
        cos_sim = sum([i*j for i, j in zip(x, y)]) / \
            (math.sqrt(sum([i*i for i in x])) * math.sqrt(sum([i*i for i in y])))
        return 1-cos_sim

    def process(self, X):
        '''
        Given an input metadata object, calculate the distance from a reference
        object. A metadata object is a dataframe containing pre-calculated
        counts for each variable"s categories or binned values.


        Parameters
        ----------
        X : data frame
            Metadata representing the dataset we want to compare to
            the reference dataset X_ref.

        Returns
        -------
        data frame
            Distance estimation for each variable in the original dataframe,
            calculated between reference data and new data.

        '''
        distance = [None]*self.n_categories
        ci = 0
        for cc in self.categories:
            s0 = self.X_ref[self.X_ref['variable'] == cc]
            s1 = X[X['variable'] == cc]
            s01 = pd.merge(s0, s1, how='outer', on=['variable', 'level'])  # merge keeping all rows
            s01.fillna(0, inplace=True)
            count_x = self.count_variable+'_x'
            count_y = self.count_variable+'_y'
            try:
                distance[ci] = self.cosine_distance(s01[count_x].tolist(), s01[count_y].tolist())
            except:
                distance[ci] = np.nan
            ci = ci+1
        result = pd.DataFrame({'variable': self.categories, 'distance': distance})

        return self.__class__.post_process(result)



class RankDriftDetector(BaseDriftDetector):
    '''
    NOTE: This class is not currently in use.
    Class for calculating drift using a special rank distance. This is to
    be applied to a type of metadata object that encodes categorical
    variables with a high number of values and high imbalance in frequencies,
    that have been re-grouped and represented by a metadata object created by
    a CategoricalFrequenciesGrouper class. See metadata_data in
    ml_metadata module.
    '''

    # class variables ----------------------------------------------------------
    #  Separator for collapsing vectors into strings (must be same as metadata data)
    separator = '|'

    column_signature=['variable','distance','distance_normalized','drift','rank_drift']
    column_place_holder_values=['NA',0.0,0.0,False,0.0]
    drift_variable='rank_drift'

    # class utility functions ---
    @classmethod
    def post_process(cls, D):
        '''
        Create a normalized drift column based on distance metrics results.
        For rank drift, this is calculated as a straight line approximation
        of an S curve:
            0 if D<=0.3
            a straight line between 0 and 1 if D between 0.3 and 0.7
            1 if D>0.7

        Parameters
        ----------
        D : data frame
            The calculated drift dataframe.

        Returns
        -------
        D : data frame
            The drift dataframe with added drift column.

        '''
        conditions = [
            (D['distance_normalized'] <= 0.3),
            (D['distance_normalized'] > 0.3) & (D['distance_normalized'] <= 0.7),
            (D['distance_normalized'] > 0.7)
        ]
        # between 0.3 and 0.7 draw a line from 0 to 1
        values = [0, (D['distance_normalized']-0.3)/0.4, 1]
        D[cls.drift_variable] = np.select(conditions, values)
        return D

    # object methods ---

    def __init__(self, drift_cutoff=1, count_variable='count'):
        '''
        Initialize class by storing the relevant information.

        Parameters
        ----------
        drift_cutoff: integer, The default is 1.
        count_variable : string, optional
            The name of the metadata column representing a count
            (frequency) of values for each variable of the original dataset.
            The default is 'count'.

        Returns
        -------
        None.

        '''
        self.drift_cutoff = drift_cutoff
        self.count_variable = count_variable
        return None

    # use metadata as input
    def setup(self, X):
        '''
        From a data frame containing level counts for each categorical
        variable, store the relevant information for further processing.

        Parameters
        ----------
        X : data frame
            The input data frame, in the format output by
            CategoricalFrequenciesWorker.

        Returns
        -------
        self
            This object.

        '''
        self.categories = X['variable'].unique().tolist()  # the number of  columns is fixed
        self.n_categories = len(self.categories)
        self.X_ref = X  # the possible values depend on the dataset
        self.is_setup = True
        return self

    def process(self, X):
        '''
        Compute rank distance as the change in rank between old and new levels.

        Parameters
        ----------
        X : data frame
            The new data frame, in the format output by
            CategoricalFrequenciesWorker.

        Returns
        -------
        data frame
            A data frame with the calculated rank distance.

        '''
        distance = [None]*self.n_categories
        distance_normalized = [None]*self.n_categories
        sep = self.__class__.separator
        ci = 0
        for cc in self.categories:
            s0 = self.X_ref.loc[(self.X_ref['variable'] == cc),
                                self.count_variable].reset_index(drop=True)
            s1 = X.loc[(X['variable'] == cc), self.count_variable].reset_index(drop=True)

            # add 1 so we don't start from zero
            s0.index += 1
            s1.index += 1
            s01 = pd.DataFrame({'s0': s0, 's1': s1})
            # keep rows where original levels were explicitly listed
            s01 = s01.loc[s01['s0'] != '']

            s01['s0'] = s01['s0'].str.split(sep)
            s01_x = s01.explode('s0')[['s0']]
            s01_x.reset_index(inplace=True)
            s01_x.columns = ['index0', 'level']

            s01['s1'] = s01['s1'].str.split(sep)
            s01_y = s01.explode('s1')[['s1']]
            s01_y.reset_index(inplace=True)
            s01_y.columns = ['index1', 'level']

            s01_compare = pd.merge(s01_x, s01_y, on='level', how='outer')
            # Remove a named level that simply disappeared, as it is accounted for
            s01_compare = s01_compare.loc[s01_compare['level'] != '']

            # impute missing ranks with the previous non-rank bin
            impute_index = min(s01_compare['index0'].values)-1
            s01_compare = s01_compare.apply(lambda x: x.fillna(
                impute_index) if x.dtype != 'object' else x.fillna(''))

            try:
                # raw distance: sum of rank changes for named levels
                d = sum(abs(s01_compare['index0']-s01_compare['index1']))
                distance[ci] = float(d)
                # normalize to maximum possible distance
                sum0 = sum(s01_x.index0)  # sum of named levels (e.g. 7+8+8+9...)
                # subtract sum of borderline minor levels e.g. 5*n
                m = sum0-impute_index*s01_x.shape[0]
                # maximum distance: if all original levels exit the major bins
                # what is the scale? 10% of the original levels exiting? Or simply 1 (no real need to normalize?)
                # print(sum0,impute_index,m,d,d/m)
                distance_normalized[ci] = d/m
            except:
                distance[ci] = 0.0
                distance_normalized[ci] = 0.0
            ci = ci+1

        result = pd.DataFrame({'variable': self.categories, 'distance': distance,
                              'distance_normalized': distance_normalized})
        result['is_drift'] = result['distance_normalized'] >= self.drift_cutoff

        return self.__class__.post_process(result)



class CramerVDriftDetector(BaseDriftDetector):
    '''
    Class for calculating drift using adjusted Cramer's V.
    '''

    column_signature=['variable','cramerv','cramerv_drift']
    column_place_holder_values=['NA',0.0,0.0]
    drift_variable='cramerv_drift'

    # class utility functions ---

    @classmethod
    def post_process(cls, D):
        '''
        Create a normalized drift column based on distance metrics results.
        For Cramer's V drift, it is simply the calculated drift, since
        this is already bound between 0 and 1.

        Parameters
        ----------
        D : data frame
            The calculated drift dataframe.

        Returns
        -------
        D : data frame
            The drift dataframe with added drift column.

        '''
        D[cls.drift_variable] = D['cramerv']
        return D

    @classmethod
    def calculate_cramerv(cls, con_tab, correct_for_size=True):
        '''
        Calculate Cramer's V with correction for data count imbalance
        and then add bias correction.

        Parameters
        ----------
        con_tab : numpy arry
            The contingency table.
        correct_for_size : bool, optional
            Whether to apply the data count imbalance correction.
            The default is True.

        Returns
        -------
        V : real
            Cramer's V.

        '''
        # apply first correction for data count imbalance
        if correct_for_size:
            total1 = con_tab[0].sum()
            total2 = con_tab[1].sum()
            if total1 > total2:
                def f(x): return np.ceil(x * total2/total1)
                con_tab[0, :] = f(con_tab[0, :])
            if total1 < total2:
                def f(x): return np.ceil(x * total1/total2)
                con_tab[1, :] = f(con_tab[1, :])
        # then calculate cramerV with its own correction
        chisq,  *rest = chi2(con_tab, lambda_='pearson', correction=False)
        n = np.sum(con_tab)
        k, r = con_tab.shape
        phi2 = chisq/n
        factor = (k-1)*(r-1)/(n-1)
        phi2_tilde = max(0, phi2-factor)
        k_tilde = k-(k-1) ** 2/(n-1)
        r_tilde = r-(r-1) ** 2/(n-1)
        c_tilde = min(k_tilde, r_tilde)
        V = math.sqrt(phi2_tilde / (c_tilde-1))
        return V

    # object methods ---

    def __init__(self, count_variable='count'):
        '''
        Initialize class by storing the relevant information.

        Parameters
        ----------
        count_variable : string, optional
            The name of the metadata column representing a count
            (frequency) of values for each variable of the original dataset.
            The default is 'count'.

        Returns
        -------
        None.

        '''
        self.count_variable = count_variable
        return None

    # use metadata as input
    def setup(self, X):
        '''
        From a data frame containing level counts for each categorical
        variable, store the relevant information for further processing.

        Parameters
        ----------
        X : data frame
            The input data frame, in the format output by
            CategoricalFrequenciesWorker.

        Returns
        -------
        self
            This object.

        '''
        self.categories = X['variable'].unique().tolist()  # the number of  columns is fixed
        self.n_categories = len(self.categories)
        self.X_ref = X  # the possible values depend on the dataset
        self.is_setup = True
        return self

    def process(self, X):
        '''
        Given an input metadata object, calculate the distance from a reference
        object. A metadata object is a dataframe containing pre-calculated
        counts for each variable"s categories or binned values.
        Any exception in the calculation results in the result assigned to
        np.nan.


        Parameters
        ----------
        X : data frame
            Metadata representing the dataset we want to compare to
            the reference dataset X_ref.

        Returns
        -------
        data frame
            Distance estimation for each variable in the original dataframe,
            calculated between reference data and new data.

        '''
        cramerv = [None]*self.n_categories
        ci = 0
        for cc in self.categories:
            s0 = self.X_ref[self.X_ref['variable'] == cc]
            s1 = X[X['variable'] == cc]
            s01 = pd.merge(s0, s1, how='outer', on=['variable', 'level'])  # merge keeping all rows
            s01.fillna(0, inplace=True)
            count_x = self.count_variable+'_x'
            count_y = self.count_variable+'_y'
            # remove records where both counts are zero
            s01 = s01.loc[s01[count_x]+s01[count_y] > 0]
            try:
                contingency_table = s01[[count_x, count_y]].to_numpy().transpose()
                cramerv[ci] = self.__class__.calculate_cramerv(contingency_table)
            except Exception as err:
                #print("cramerV exception")
                #print(err.__class__)
                #print(err)
                #print(contingency_table)
                cramerv[ci] = np.nan
            ci = ci+1
        result = pd.DataFrame({'variable': self.categories, 'cramerv': cramerv})

        return self.__class__.post_process(result)




class OverlapDriftDetector(BaseDriftDetector):
    '''
    Class for calculating drift using simple % overlap between
    distributions.
    '''

    column_signature=['variable','overlap','overlap_drift']
    column_place_holder_values=['NA',0.0,0.0]
    drift_variable='overlap_drift'

    # class utility functions ---

    @classmethod
    def post_process(cls, D):
        '''
        Create a normalized drift column based on distance metrics results.
        For overlap drift, it is (100-overlap)/100, so for zero overlap, the
        drift is 1 and for 100% overlap, the drift is 0.

        Parameters
        ----------
        D : data frame
            The calculated drift dataframe.

        Returns
        -------
        D : data frame
            The drift dataframe with added drift column.

        '''
        D[cls.drift_variable] = (100.0-D['overlap'])/100.0
        return D

    # object methods ---

    def __init__(self):
        '''
        Initialize class by storing the relevant information.

        Parameters
        ----------
        no parameters

        Returns
        -------
        None.

        '''
        return None

    # use metadata as input
    def setup(self, X):
        '''
        From a data frame containing level counts for each categorical
        variable, store the relevant information for further processing.

        Parameters
        ----------
        X : data frame
            The input data frame, in the format output by
            CategoricalFrequenciesWorker.

        Returns
        -------
        self
            This object.
        '''
        self.categories = X['variable'].unique().tolist()  # the number of columns is fixed
        self.n_categories = len(self.categories)
        self.X_ref = X  # the possible values depend on the dataset
        self.is_setup = True
        return self

    def process(self, X):
        '''
        Given an input metadata object, calculate the distance from a reference
        object. A metadata object is a dataframe containing pre-calculated
        counts for each variable"s categories or binned values.


        Parameters
        ----------
        X : data frame
            Metadata representing the dataset we want to compare to
            the reference dataset X_ref.

        Returns
        -------
        data frame
            Distance estimation for each variable in the original dataframe,
            calculated between reference data and new data.
        '''

        overlap = [None]*self.n_categories
        ci = 0
        for cc in self.categories:
            s0 = self.X_ref[self.X_ref['variable'] == cc]
            s1 = X[X['variable'] == cc]
            s01 = pd.merge(s0, s1, on=['variable', 'level'], how='outer')
            s01 = s01[s01.count_x.isna()]  # remove levels that do not exist in original data
            outliers_percent = round(sum(s01['count_y'])/sum(s1['count'])*100, 1)
            overlap[ci] = 100.0-outliers_percent
            ci = ci+1
        result = pd.DataFrame({'variable': self.categories, 'overlap': overlap})

        return self.__class__.post_process(result)


class SimpleVariableDriftDetector(BaseDriftDetector):
    '''
    Class for calculating drift by directly comparing two data frames.
    '''

    column_signature=['variable','value_old','value_new','delta','drift']
    column_place_holder_values=['NA',0.0,0.0,0.0,0.0]
    drift_variable='drift'

    # object methods ---

    def __init__(self, drift_limits, compare_variable='count',
                 delta_variable='delta',
                 merge_variable='variable', base_suffix='old', new_suffix='new'
                 ):
        '''
        Initialize class by storing the relevant information.

        Parameters
        ----------
        drift_limits : list of two elements
            Numeric limits for generating the normalised distance in the
            post_process function.
        compare_variable : string, optional
            The name of the metadata column representing a count
            (frequency) of values for each variable of the original dataset.
            The default is 'count'.
        delta_variable : string, optional
            DESCRIPTION. The default is 'delta'.
        merge_variable : string, optional
            DESCRIPTION. The default is 'variable'.
        base_suffix : string, optional
            DESCRIPTION. The default is 'old'.
        new_suffix : string, optional
            DESCRIPTION. The default is 'new'.

        Returns
        -------
        None.

        '''
        self.drift_limits = drift_limits
        self.compare_variable = compare_variable
        self.delta_variable = delta_variable
        self.merge_variable = merge_variable
        self.base_suffix = base_suffix
        self.new_suffix = new_suffix

        return None

    # use metadata as input
    def setup(self, X):
        '''
        From a data frame containing an old and new value of a numeric column
        to be compared
        for each categorical
        variable, store the relevant information for further processing.

        Parameters
        ----------
        X : data frame
            The input data frame, in the format output by
            CategoricalFrequenciesWorker.

        Returns
        -------
        self
            This object.
    '''
        self.X_ref = X
        self.is_setup = True
        return self



    def post_process(self, D):
        '''
        Create a normalized drift column based on distance metrics results.
        If some drift limits are provided, this is calculated as a straight
        line approximation of an S curve, using the stored drift limits:


        There are four possible cases:
        drift_limits=[b,c]
        in this case the drift is calculated as:
            0 if the unsigned difference is <=b
            a line from 0 to 1 if the unsigned difference ∊ (b,c]
            1 if the unsigned difference is >c

        drift_limits=[a,b,c,d] with e=0.1, f=0.9 fixed
        in this case the drift is calculated as:
            0 if the unsigned difference is <=a
            a line from 0 to e if the unsigned difference ∊ (a,b]
            a line from e to f if the unsigned difference ∊ (b,c]
            a line from f to 1 if the unsigned difference ∊ (c,d]
            1 if the unsigned difference is >d

        drift_limits = [d]
        in this case the drift is calculated as:
            the unsigned difference /d

        else
        the drift is simply the unsigned difference in the relative values, with no further mapping.

        Note this is not a class method as it depends on a lot of instance values
        such as delta_variable, drift_limits etc.

        If the drift limits are an empty list, the drift is passed through
        without mapping.

        Parameters
        ----------
        D : data frame
            The calculated drift dataframe.

        Returns
        -------
        D : data frame
            The drift dataframe with added drift column.

        '''
        if len(self.drift_limits)==2:
            b=self.drift_limits[0]
            c=self.drift_limits[1]
            slope=1.0/(c-b)
            intercept=-b*slope
            conditions = [
                (D[self.delta_variable] <= b),
                (D[self.delta_variable] > b) & (
                    D[self.delta_variable] <= c),
                (D[self.delta_variable] > c)
            ]
            # between b and c draw a line from 0 to 1. Lower than b:0, higher than c:1
            values = [0, D[self.delta_variable]*slope+intercept, 1]
            D[self.__class__.drift_variable] = np.select(conditions, values)
        elif len(self.drift_limits)==4:
            a=self.drift_limits[0]
            b=self.drift_limits[1]
            c=self.drift_limits[2]
            d=self.drift_limits[3]
            e=0.1 #fixed joint height between first and second line
            f=0.9 #fixed joint height between second and third line
            slope1=e/(b-a)
            intercept1=-slope1*a
            slope2=(f-e)/(c-b)
            intercept2=f-slope2*c
            slope3=(1-f)/(d-c)
            intercept3=1-slope3*d

            conditions = [
                D[self.delta_variable] <=a,
                (D[self.delta_variable] > a) & (
                    D[self.delta_variable] <= b),
                (D[self.delta_variable] > b) & (
                    D[self.delta_variable] <= c),
                (D[self.delta_variable] > c) & (
                    D[self.delta_variable] <= d),
                D[self.delta_variable] > d
                ]
            # draw 3 lines: a>b,b>c and c>d. Lower than a:0, higher than d:1
            values = [0,D[self.delta_variable]*slope1+intercept1,
                      D[self.delta_variable]*slope2+intercept2 ,
                      D[self.delta_variable]*slope3+intercept3, 1]
            D[self.__class__.drift_variable] = np.select(conditions, values)

        # assume that the drift limit is the max value and that the min is 0.
        # simply normalize as z=x-min(x)/(max(x)-min(x)) = x/max(x)
        elif len(self.drift_limits)==1:
            D[self.__class__.drift_variable] = D[self.delta_variable]/self.drift_limits[0]

        else:
            D[self.__class__.drift_variable] = D[self.delta_variable]


        return D

    def process(self, X):
        '''
        Given an input a data frame containing an old and new value of a numeric column
        to be compared for each categorical variables, calculate the difference
        in values and map it to a 0-1 range.


        Parameters
        ----------
        X : data frame
            Metadata representing the dataset we want to compare to
            the reference dataset X_ref.

        Returns
        -------
        data frame
            Distance estimation for each variable in the original dataframe,
            calculated between reference data and new data.

        '''

        compare_variable_base = self.compare_variable+'_'+self.base_suffix
        compare_variable_new = self.compare_variable+'_'+self.new_suffix

        self.X_ref.rename(columns={self.compare_variable: compare_variable_base}, inplace=True)
        X.rename(columns={self.compare_variable: compare_variable_new}, inplace=True)

        result = pd.merge(self.X_ref, X, on=self.merge_variable)
        #This is always the absolute value
        result[self.delta_variable] = abs(
            result[compare_variable_base]-result[compare_variable_new])

        return self.post_process(result)


# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
#
# --- INTERNAL ENTRY POINTs ---------------------------------------------------

def calculate_variable_drift(detector, detector_parms, my_worker, old_md_df, new_df):
    '''
    Calculate drift for individual variables with pre-binned values.

    Parameters
    ----------
    detector : A subclass of DriftDetector
        The detector to use.
    detector_parms : dict
        The input parameters for the detector.
    my_worker : A subclass of BaseMetadataWorker
        DESCRIPTION.
    old_md_df : data frame
        The binned baseline data frame.
    new_df : data frame
        The new data frame.

    Returns
    -------
    drift_df : data frame
        A data frame containing a drift metric for each variable.

    '''

    new_md_df = my_worker.setup_from_object_and_process(new_df, old_md_df)
    my_detector = detector(**detector_parms)
    drift_df = my_detector.setup_and_process(old_md_df, new_md_df)

    return drift_df


def calculate_simple_variable_drift(detector, detector_parms, old_md_df, new_md_df):
    '''
    Calculate drift for correlation and variable importance, where the data
    structure of the input data frames is already in a format that allows
    direct comparison.

    Parameters
    ----------
    detector : A subclass of DriftDetector
        The detector to use.
    detector_parms : dict
        The input parameters for the detector.
    my_worker : A subclass of BaseMetadataWorker
        DESCRIPTION.
    old_md_df : data frame
        The processed baseline data frame.
    new_md_df : data frame
        The processed new data frame.

    Returns
    -------
    drift_df : data frame
        A data frame containing a drift metric for each variable or
        variable pair.

    '''
    my_detector = detector(**detector_parms)
    drift_df = my_detector.setup_and_process(old_md_df, new_md_df)

    return drift_df

# Calculate all data drift metrics
def calculate_data_drift(baseline_cat_worker, baseline_catgroup_worker,
                         baseline_num_worker, baseline_corr_worker,
                         baseline_cat_df, baseline_num_df, baseline_catgroup_df,
                         baseline_corr_df, new_df,
                         supply_place_holders=False):
    '''
    Calculate and combine, where appropriate, all drift metrics for
    the dataset.

    Parameters
    ----------
    baseline_cat_worker : CategoricalFrequenciesWorker
        The metadata Worker object for categories.
    baseline_catgroup_worker : CategoricalFrequenciesGrouper
        The metadata Worker object for high-cardinality categories..
    baseline_num_worker : DatetimeBinsWorker
        The metadata Worker object for numbers including dates.
    baseline_corr_worker : CorrelationWorker
        The metadata Worker object for correlations.
    baseline_cat_df : data frame
        The metadata frame for the baseline categories.
    baseline_num_df : data frame
        The metadata frame for the baseline numeric columns.
    baseline_catgroup_df : data frame
        The metadata frame for the baseline high-cardinality categories.
    baseline_corr_df : data frame
        The metadata frame for the baseline linear correlation.
    new_df : data frame
        The new dataset to compare to baseline.
    supply_place_holders : bool, optional
        If true, and returned data frames are empty, add a line
        so data types can be inferred. The default is False.

    Returns
    -------
    data_1var_drift : data frame
        Drift table for individual variables.
    data_2var_drift : data frame
        Drift table for variable pairs.

    '''

    # Calculate single-variable drift contributions ---------------------------

    # Calculate Cramers V drift for every type of metadata
    detector_parms = {'count_variable': 'count'}
    drift0 = calculate_variable_drift(
        CramerVDriftDetector, detector_parms, baseline_cat_worker, baseline_cat_df, new_df)
    drift1 = calculate_variable_drift(
        CramerVDriftDetector, detector_parms, baseline_catgroup_worker, baseline_catgroup_df, new_df)
    drift2 = calculate_variable_drift(
        CramerVDriftDetector, detector_parms, baseline_num_worker, baseline_num_df, new_df)
    cramerv_drift = pd.concat([drift0, drift1, drift2])

    # Calculate Cosine drift for every type of metadata
    detector_parms = {'count_variable': 'count'}
    drift0 = calculate_variable_drift(
        CosineDriftDetector, detector_parms, baseline_cat_worker, baseline_cat_df, new_df)
    drift1 = calculate_variable_drift(
        CosineDriftDetector, detector_parms, baseline_catgroup_worker, baseline_catgroup_df, new_df)
    drift2 = calculate_variable_drift(
        CosineDriftDetector, detector_parms, baseline_num_worker, baseline_num_df, new_df)
    cosine_drift = pd.concat([drift0, drift1, drift2])

    # Calculate Overlap drift (excluding grouped categorical data)
    detector_parms = {}
    drift0 = calculate_variable_drift(
        OverlapDriftDetector, detector_parms, baseline_cat_worker, baseline_cat_df, new_df)
    drift1 = calculate_variable_drift(
        OverlapDriftDetector, detector_parms, baseline_num_worker, baseline_num_df, new_df)
    overlap_drift = pd.concat([drift0, drift1])

    # Calculate Rank drift (grouped categorical data only)
    detector_parms = {'drift_cutoff': 0.2, 'count_variable': 'levels'}
    rank_drift = calculate_variable_drift(
        RankDriftDetector, detector_parms, baseline_catgroup_worker, baseline_catgroup_df, new_df)

    # Calculate pair-variable drift contributions ---------------------------

    # Calculate Correlation drift (numeric data only)
    #detector_parms = {'drift_limits': [0,0.2,0.5,2], 'compare_variable': 'correlation',
    #              'delta_variable': 'delta',
    #              'merge_variable':'variable12'}
    # for now implement a simple mapping between 0-2 and 0-1
    detector_parms = {'drift_limits': [2], 'compare_variable': 'correlation',
                  'delta_variable': 'delta',
                  'merge_variable':'variable12'}
    #we must pre-calculate the correlation for SimpleVariableDriftDetector
    corr_new_df=baseline_corr_worker.process(new_df)
    correlation_drift = calculate_simple_variable_drift(
        SimpleVariableDriftDetector, detector_parms, baseline_corr_df, corr_new_df)

    # There are cases in which we need to return something in the data frame
    if supply_place_holders:
        if cramerv_drift.shape[0]==0:
            cramerv_drift=CramerVDriftDetector.place_holder_result()
        if cosine_drift.shape[0]==0:
            cosine_drift=CosineDriftDetector.place_holder_result()
        if overlap_drift.shape[0]==0:
            overlap_drift=OverlapDriftDetector.place_holder_result()
        if rank_drift.shape[0]==0:
            rank_drift=RankDriftDetector.place_holder_result()
        if correlation_drift.shape[0]==0:
            correlation_drift=SimpleVariableDriftDetector.place_holder_result()

    # Rationalize variable names (this would be better at source, TO DO)
    cramerv_drift.rename({CramerVDriftDetector.drift_variable:'drift'},inplace=True, axis = 1)
    cosine_drift.rename({CosineDriftDetector.drift_variable:'drift'},inplace=True, axis = 1)
    overlap_drift.rename({OverlapDriftDetector.drift_variable:'drift'},inplace=True, axis = 1)
    rank_drift.rename({RankDriftDetector.drift_variable:'drift'},inplace=True, axis = 1)
    correlation_drift.rename({SimpleVariableDriftDetector.drift_variable:'drift'},inplace=True, axis = 1)

    # Assign drift type (this would be better at source, TO DO)
    cramerv_drift['drift_type']='cramerv'
    cosine_drift['drift_type']='cosine'
    overlap_drift['drift_type']='overlap'
    rank_drift['drift_type']='rank'
    correlation_drift['drift_type']='correlation'

    #Concatenate together can extend if we wish
    keep_cols = ['variable','drift','drift_type']
    list_to_concat=cramerv_drift[keep_cols], \
                    cosine_drift[keep_cols],\
                    overlap_drift[keep_cols], \
                    rank_drift[keep_cols]
    data_1var_drift=pd.concat(list_to_concat,axis=0)
    data_1var_drift.reset_index(inplace=True, drop=True)
    data_1var_drift.dropna(inplace=True)
    data_1var_drift = pd.pivot_table(data_1var_drift,
                                       values='drift', index='variable',
                                       columns=['drift_type'])

    keep_cols = ['variable12','drift','drift_type']
    list_to_concat=[correlation_drift[keep_cols]]
    data_2var_drift=pd.concat(list_to_concat)
    data_2var_drift.reset_index(inplace=True, drop=True)
    data_2var_drift.dropna(inplace=True)

    # Now re-pivot
    data_2var_drift = pd.pivot_table(data_2var_drift,
                                           values='drift', index=['variable12'],
                                           columns=['drift_type'])
    return (data_1var_drift, data_2var_drift)



def calculate_model_drift(evaluator,
                         num_worker,
                         baseline_binned_prediction_df,
                         baseline_variable_importance_df, baseline_performance_df,
                         new_df, baseline_predicted_classes=None):
    '''
    Calculate drift when the model is applied to a new dataset.
    Currently the drift is calculated on the permutation importance
    (with respect to the original predictions) and drift in the distribution
    of predictions. For a regression model, the predictions are the
    straightforward numeric predictions. For a classification model, the shapes
    of the individual class probabilities are compared to the baseline.

    Parameters
    ----------
    evaluator : TYPE
        DESCRIPTION.
    num_worker : TYPE
        DESCRIPTION.
    baseline_binned_prediction_df : data frame
        DESCRIPTION.
    baseline_variable_importance_df : data frame
        DESCRIPTION.
    baseline_performance_df : data frame
        DESCRIPTION.
    new_df : data frame
        The new dataset to compare to baseline.
    baseline_predicted_classes : data frame, optional
        The distribution of class probability, for a classification
        model, or None for a regression model. The default is None.

    Returns
    -------
    model_1var_drift : data frame
        Variable-based model drift. Currently only includes variable
        importance.
    model_prediction_drift : data frame
        Drift in model prediction profile. For a regression model, this contains
        one variable, the prediction. For a classification model, it shows the
        drift in probability profile for each class.
    model_performance_drift : data frame
        Drift in model performance metrics, if the label (ground-truth) of
        the new dataset is available.
    y_pred : data frame
        The prediction dataset for the new data.
    y_prob : data frame
        The class probabilities for the new data. None if this is
        a regression model.
    variable_importance_df : data frame
        The variable importance for the new data.

    '''

    # Find the type of model (one of "classification" or "regression")
    model_type = evaluator.scorer.model_type
    # The name of the target variable
    target = evaluator.scorer.target
    # Isolate target column if available
    predictors = list(new_df.columns)
    if target in predictors:
        predictors.remove(target)
        y = new_df[target]
    else:
        y = None
    X = new_df[predictors]

    # Calculate prediction data table
    prediction_df = evaluator.scorer.calc_prediction(X)
    y_pred = prediction_df[evaluator.scorer.prediction_col]
    y_pred0= y_pred.copy() #store the prediction straight from the scorer

    #only for classification: the prediction data table will also
    #contain the class probabilities
    if model_type == 'classification':
        y_prob = prediction_df[evaluator.scorer.get_orig_classes()]

        #decode target values if necessary
        target_decode=dict(zip(evaluator.scorer.get_int_values(),evaluator.scorer.get_orig_classes()))
        #only decode if all the elements in the series to decode are contained in the mapper
        if all(item in y_pred.unique().tolist() for item in list(target_decode.keys())):
            y_pred=y_pred.map(target_decode)
    else:
        y_prob=None


    # Calculate model performance drift (if y is available)
    performance_df = evaluator.calc_model_performance(X, y_pred, y)

    # Calculate simple performance drift
    baseline_performance_df['data'] = 'Old'
    performance_df['data'] = 'New'
    model_performance_drift = pd.concat([baseline_performance_df, performance_df])

    # Calculate 1var model based drift ----------------------------------------

    #  Variable importance drift
    detector_parms = {'drift_limits': [0.1, 0.3], 'compare_variable': 'relative_value',
                      'delta_variable': 'importance_delta'}
    #Variable importance needs the prediction as it comes out of the scorer
    variable_importance_df = evaluator.calc_permutation_sensitivity(X, y_pred0)

    variable_importance_drift = calculate_simple_variable_drift(
        SimpleVariableDriftDetector, detector_parms, baseline_variable_importance_df, variable_importance_df)
    variable_importance_drift['drift_type']='variable importance'

    #Concatenate together... can extend if we wish
    keep_cols = ['variable','drift','drift_type']
    list_to_concat=[variable_importance_drift[keep_cols]]
    model_1var_drift=pd.concat(list_to_concat,axis=0)
    model_1var_drift.reset_index(inplace=True, drop=True)
    model_1var_drift.dropna(inplace=True)
    model_1var_drift = pd.pivot_table(model_1var_drift,
                                       values='drift', index='variable',
                                       columns=['drift_type'])

    # Calculate prediction drift ----------------------------------------------

    use_overlap=False #For now assume there is always overlap
    if model_type=='classification':
        y_for_pred_drift = y_prob.copy()
    else:
        y_for_pred_drift = y_pred0.copy()

    # drift in overall prediction distribution,
    # ...by class if this is a classification model
    detector_parms = {'count_variable': 'count'}
    cramerv_drift = calculate_variable_drift(
        CramerVDriftDetector, detector_parms, num_worker, baseline_binned_prediction_df, y_for_pred_drift)
    if use_overlap:
        detector_parms = {}
        overlap_drift = calculate_variable_drift(
            OverlapDriftDetector, detector_parms, num_worker, baseline_binned_prediction_df, y_for_pred_drift)
    detector_parms = {'count_variable': 'count'}
    cosine_drift = calculate_variable_drift(
        CosineDriftDetector, detector_parms, num_worker, baseline_binned_prediction_df, y_for_pred_drift)


    # Rationalize variable names (this would be better at source, TO DO)
    cramerv_drift.rename({CramerVDriftDetector.drift_variable:'drift'},inplace=True, axis = 1)
    cosine_drift.rename({CosineDriftDetector.drift_variable:'drift'},inplace=True, axis = 1)
    if use_overlap:
        overlap_drift.rename({OverlapDriftDetector.drift_variable:'drift'},inplace=True, axis = 1)

    # Assign drift type (this would be better at source, to do in next version)
    cramerv_drift['drift_type']='cramerv'
    cosine_drift['drift_type']='cosine'
    if use_overlap:
        overlap_drift['drift_type']='overlap'

    #Concatenate together can extend if we wish
    keep_cols = ['variable','drift','drift_type']
    list_to_concat=[cramerv_drift[keep_cols], \
                    cosine_drift[keep_cols]]
    if use_overlap:
        list_to_concat.append(overlap_drift[keep_cols])

    model_prediction_drift=pd.concat(list_to_concat,axis=0)
    model_prediction_drift.reset_index(inplace=True, drop=True)
    model_prediction_drift.dropna(inplace=True)
    model_prediction_drift = pd.pivot_table(model_prediction_drift,
                                       values='drift', index='variable',
                                       columns=['drift_type'])
    return (model_1var_drift, model_prediction_drift, model_performance_drift, y_pred, y_prob, variable_importance_df)


#
#
# --- USER ENTRY POINT --------------------------------------------------------

def calculate_drift_entry_point(mdd_json,mdm_json,model_pipeline,model_type,
                                new_df, target=None, combine_option='sum'):
    '''
    Calculate drift for a new dataset, using information from the baseline
    dataset and model behaviour.

    Parameters
    ----------
    mdd_json : str
        The JSON object describing the data metadata.
    mdm_json : str
        The JSON object describing the data metadata.
    model_pipeline : bytes or sklearn pipeline
        The trained model pipeline to use.
    model_type : str
        One of ["classification","regression"].
    new_df : data frame
        The new dataset to compare to baseline.
    target : str, optional
        The name of the target variable. The default is None.
    combine_option : str, optional
        When different metrics can be combined, this defines
        how this is implemented. The default is 'sum'.

    Raises
    ------
    NotImplementedError
        If the model_type is not one of ["classification","regression"], raise
        a NotImplemented error stating that the model_type is
        not implemented yet.

    Returns
    -------
    all_1var_drift : data frame
        Variable based drift.
    data_2var_drift : data frame
        Variable based data drift.
    model_prediction_drift : data frame
        Drift in model predictions.
    y_prob or y_pred: data frame
        For a classification model, the class probabilities for the new data.
        For a regression model, the predictions for the new data.
    variable_importance : data frame
        The variable importance for the new data.
    result : data frame
        Summary of all drift measures.

    '''

    if not model_type in ['classification','regression']:
        raise NotImplementedError('calculate_drift_entry_point: The selected '+\
                                      model_type+' model_type is not implemented yet')


    # Unpack json and create metadata workers: data
    received_cat_worker,received_catgroup_worker,received_num_worker,received_desc_worker,received_corr_worker,\
            received_cat_df,received_catgroup_df,received_num_df,received_desc_df,received_corr_df =\
        mdd.unpack_data_metadata(mdd_json)
    # Unpack json and create metadata workers: model
    if model_type=='regression':
        model_num_worker,baseline_binned_prediction_df,\
            model_scorer, model_evaluator,\
            baseline_variable_importance_df,baseline_performance_df = \
            mdm.unpack_regression_model_metadata(mdm_json, model_pipeline)
    elif model_type=='classification':
        model_num_worker, _, baseline_predicted_classes,baseline_binned_prediction_df,\
            model_scorer, model_evaluator,\
            baseline_variable_importance_df,baseline_performance_df = \
            mdm.unpack_classification_model_metadata(mdm_json, model_pipeline)

    # Detect data drift -------------------------------------------------------
    #data_1var_drift is the drift in individual variables
    #data_2var_drift is the drift in variable pairs
    data_1var_drift,data_2var_drift = \
        calculate_data_drift(received_cat_worker, received_catgroup_worker, received_num_worker, received_corr_worker,
                             received_cat_df, received_num_df, received_catgroup_df, received_corr_df, new_df)

    # Detect model drift -------------------------------------------------------
    if model_type == 'regression':
        baseline_predicted_classes=None

    # Note: for a regression model the returned y_prob is None
    #model_1var_drift is the variable importance drift
    #model_prediction_drift is the drift in model prediction profiles

    model_1var_drift, model_prediction_drift, _, y_pred, y_prob,variable_importance=\
        calculate_model_drift(model_evaluator, model_num_worker,
                baseline_binned_prediction_df, baseline_variable_importance_df,
                baseline_performance_df, new_df, baseline_predicted_classes)

    # PUT INFORMATION TOGETHER -----------------------------------------------

    # 1 - average on different metrics per variable or pair or class

    data_1var_drift['mean_drift_data'] = data_1var_drift.mean(
        axis=1, skipna=True, numeric_only=True)
    model_1var_drift['mean_drift_model'] = model_1var_drift.mean(
        axis=1, skipna=True, numeric_only=True)
    all_1var_drift=pd.merge(data_1var_drift,model_1var_drift,on='variable')

    data_2var_drift['mean_drift_data'] = data_2var_drift.mean(
        axis=1, skipna=True, numeric_only=True)

    model_prediction_drift['mean_drift_model'] = model_prediction_drift.mean(
        axis=1, skipna=True, numeric_only=True)

    # put back variable, which became an index
    all_1var_drift = all_1var_drift.reset_index().rename(columns={'index': 'variable'})
    data_2var_drift = data_2var_drift.reset_index().rename(columns={'index': 'variable'})
    model_prediction_drift = model_prediction_drift.reset_index().rename(columns={'index': 'variable'})


    # 2 - average or sum over all variables

    if combine_option == 'avg':

        # individual variables
        total_single_data = all_1var_drift['mean_drift_data'] .sum()/all_1var_drift.shape[0]
        total_single_model = all_1var_drift['mean_drift_model'].sum()/all_1var_drift.shape[0]
        #variable pairs
        total_pair = data_2var_drift['mean_drift_data'].sum()/data_2var_drift.shape[0]
        #classes or single regression prediction
        total_pred = model_prediction_drift['mean_drift_model'] .sum()/model_prediction_drift.shape[0]

    else: #sum

        # individual variables
        total_single_data = all_1var_drift['mean_drift_data'] .sum()
        total_single_model = all_1var_drift['mean_drift_model'].sum()
        #variable pairs
        total_pair = data_2var_drift['mean_drift_data'].sum()
        #classes or single regression prediction
        total_pred = model_prediction_drift['mean_drift_model'] .sum()


    result = pd.DataFrame({'total_pred':[total_pred],
                           'total_single_data': [total_single_data],
                           'total_single_model': [total_single_model],
                           'total_pair': [total_pair]})

    if model_type=='classification':
        return (all_1var_drift,data_2var_drift,model_prediction_drift,y_prob,variable_importance,result)
    else:
        return (all_1var_drift,data_2var_drift,model_prediction_drift,y_pred,variable_importance,result)