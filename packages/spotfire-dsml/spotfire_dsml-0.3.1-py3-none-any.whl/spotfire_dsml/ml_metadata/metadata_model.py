#
# --- LIBRARIES ---------------------------------------------------------------
import numpy as np
import pandas as pd
import json
#work in progress, not currently used
#import base64
#import collections
#import random
#import re
#import requests
#import warnings

#spotfire-dsml modules
from spotfire_dsml.ml_metadata import metadata_data as mdd


# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
# Scorer classes

class BaseModelScorer():
    '''
    A base implementation for a model Scorer.
    '''

    # class variables ----------------------------------------------------------
    # Name of column containing prediction
    prediction_col = 'prediction'
    #: str: prefix for json schema parms description
    worker_parms_description_prefix = 'init parameters for class '

    # class methods -----------------------------------------------------------
    @classmethod
    def choose_scorer(cls, model_origin, model_type, target=None, target_orig_classes=[], target_int_values=[]):
        '''
        Class method.
        Depending on the value of model_origin, initialise the correct
        Scorer subclass. If the model_origin or model_type are not implemented,
        raise a NotImplemented error.

        Parameters
        ----------
        model_origin : str
            The source of the model. Currently only "sklearn" implemented.
        model_type : str
            One of "classification" or "regression".
        target : str, optional
            The name of the target variable. The default is None.
        target_orig_classes : list of str, optional
            The list of class names, if model_type is "classification".
            The default is [].
        target_int_values : list of int, optional
            The list of class integer values, if model_type is "classification".
            The default is [].

        Raises
        ------
        NotImplementedError
            If the model_origin is not implemented, raise
            a NotImplemented error stating that the model_origin is
            not implemented yet.
            Likewise, if the model_type is not one of "classification"
            or "regression".

        Returns
        -------
        Subclass of BaseModelScorer
            Currently returns an instance of SklearnScorer, or None if
            model_origin not "sklearn".

        '''
        if not model_type in ['classification','regression']:
            raise NotImplementedError(str(cls)+'.choose_scorer: The '+model_type+'model_type is not implemented yet')
            return None

        if model_origin == 'sklearn':
            return SklearnScorer(model_type, target, target_orig_classes, target_int_values)
        else:
            raise NotImplementedError(str(cls)+'.choose_scorer: The '+model_origin+'model_origin is not implemented yet')
            return None

    @classmethod
    def unpack_json(cls, received_json):
        '''
        Class method. Unpack a JSON object into its original Scorer object.

        Parameters
        ----------
        received_json : dictionary or string
            The JSON object to unpack. If the object is in string format,
            it will be automatically loaded into a dictionary.

        Raises
        ------
        KeyError
            If the schema, the parameters or the metadata for this Worker were not
            found in the JSON object.

        Returns
        -------
        Scorer object.
            The unpacked Scorer object.

        '''

        #If the json is not in dictionary form, turn it into one
        if type(received_json)== str:
            received_json = json.loads(received_json)

        try:
            schema = json.loads(received_json['schema'])
        except KeyError:
            raise KeyError(
                str(cls)+'.unpack_json: The schema key was not in json dictionary')

        # Find class name (remove whatever comes before last dot)
        my_class_name = cls.__name__.split('.')[-1]
        # Construct description strings (same as in function pack_json)
        key_parms_search = cls.worker_parms_description_prefix + my_class_name
        # Find them in the schema dictionary
        parms_key = list(filter(lambda x: key_parms_search in x, schema))

        if len(parms_key) > 0:
            parms = schema[parms_key[0]]
            scorer_attributes = json.loads(received_json[parms])
            # Create a new score object
            scorer = cls.choose_scorer(**scorer_attributes)
        else:
            raise KeyError(
                str(cls)+'.unpack_json: The parms parameter was not in json dictionary: '+key_parms_search)

        return scorer

    # object methods -----------------------------------------------------------

    def pack_json(self, scorer_parms_name):
        '''
        Take all information from this object, and turn it into
        JSON.

        Parameters
        ----------
        scorer_parms_name : str
            The name for the scorer parameters. This will be stored in
            json_schema to be retrieved in json_body.

        Returns
        -------
        json_schema : dictionary
            The json minischema.
        json_body : dictionary
            The json body.

        '''
        json_parms = self.init_attributes_to_json()
        # Find class name (remove whatever comes before last dot)
        # ..but find the base class because the unpack method is class-based on the parent class
        immediate_parent = self.__class__.__bases__[0]
        my_class_name = immediate_parent.__name__.split('.')[-1]
        # Create labels and mini schema
        worker_parms_description = self.__class__.worker_parms_description_prefix + my_class_name
        json_schema = {worker_parms_description: scorer_parms_name}
        # Create body of json
        json_body = {scorer_parms_name: json_parms}
        return (json_schema, json_body)


    def __init__(self, model_origin, model_type, target=None, target_orig_classes=[], target_int_values=[]):
        '''
        Initialize object by storing the relevant information.
        Save instance attributes passed in into special
        instance variable __init_attributes__.

        Parameters
        ----------
        model_origin : str
            The source of the model. Currently only "sklearn" implemented.
        model_type : str
            One of "classification" or "regression".
        target : str, optional
            The name of the target variable. The default is None.
        target_orig_classes : list of str, optional
            The list of class names, if model_type is "classification".
            The default is [].
        target_int_values : list of int, optional
            The list of class integer values, if model_type is "classification".
            The default is [].

        Returns
        -------
        None.

        '''
        self.model_origin = model_origin
        self.model_type = model_type
        self.target = target
        self.target_orig_classes=target_orig_classes
        self.target_int_values=[int(x) for x in target_int_values]

        # save a copy of the instance attributes that were defined during construction
        self.__init_attributes__ = self.__dict__.copy()

        return None

    def init_attributes_to_json(self):
        '''
        Collect the instance attributes defined at construction,
        and turn them into a json string.
        Used within a constructor method.

        Returns
        -------
        string
            JSON string containing instance attributes needed to
            configure scorer.

        '''
        return json.dumps(self.__init_attributes__)

    def setup(self, model):
        '''
        Store predictive model as instance variable

        Parameters
        ----------
        model : bytes or sklearn pipeline
            The predictive model object.

        Returns
        -------
        self
            This object.

        '''
        self.model = model
        return self

    def get_prediction_column(self):
        '''
        Fetch the name of the prediction column.

        Returns
        -------
        str
            The name of the prediction column.

        '''
        return self.__class__.prediction_col

    def get_orig_classes(self):
        '''
        Fetch the names of the original target classes.

        Returns
        -------
        list
            The names of the original target classes, if model_type
            is "classification".

        '''
        return self.target_orig_classes

    def get_int_values(self):
        '''
        Fetch the integers assigned to the target classes.

        Returns
        -------
        list
            The integers assigned to the target classes, if model_type
            is "classification".

        '''
        return self.target_int_values

    def get_target_name(self):
        '''
        Fetch the name of the target variable.

        Returns
        -------
        str
            The name of the target variable..

        '''
        return self.target

    def predict(self):
        '''
        Empty implementation.

        Returns
        -------
        None.

        '''
        pass

    def predict_probability(self):
        '''
        Empty implementation.

        Returns
        -------
        None.

        '''
        pass


    def calc_prediction(self, X):
        '''
        Calculate prediction for regression or classification models.
        Dispatch task to either calc_regression_prediction or
        calc_classification_prediction.

        Parameters
        ----------
        X : data frame
            The input data frame for calculating model predictions.

        Returns
        -------
        data frame
            The model predictions.

        '''
        # Any other model type is blocked when constructing the Scorer object.
        if self.model_type == 'regression':
            return self.calc_regression_prediction(X)
        elif self.model_type == 'classification':
            return self.calc_classification_prediction(X)


    def calc_regression_prediction(self, X):
        '''
        Calculate prediction for regression models.

        Parameters
        ----------
        X : data frame
            The input data frame for calculating model predictions.

        Returns
        -------
        prediction_df : data frame
            The model predictions, under a column of name
            BaseModelScorer.prediction_col.
        '''
        pred_col = self.__class__.prediction_col
        prediction_df = pd.DataFrame(columns=[pred_col])
        prediction_df[pred_col] = self.predict(X)
        return prediction_df


    def calc_classification_prediction(self, X):
        '''
        Calculate prediction for classification models.

        Parameters
        ----------
        X : data frame
            The input data frame for calculating model predictions.

        Returns
        -------
        prediction_df : data frame
            The model predictions, under a column of name
            BaseModelScorer.prediction_col. In addition,
            the class probabilities for each class are returned in
            additional columns, with names equal to the class names
            contained in the object variable target_orig_classes.
        '''
        pred_col = self.__class__.prediction_col
        pred_cols = self.get_orig_classes().copy()
        pred_cols.append(pred_col)

        prediction_df = pd.DataFrame(columns=pred_cols)
        prediction_df[pred_col] = self.predict(X)

        y_prob = self.predict_probability(X)
        prediction_df[self.get_orig_classes()] = pd.DataFrame(y_prob)
        # Avoid spurious numeric noise by rounding
        prediction_df[self.get_orig_classes()] = prediction_df[self.get_orig_classes()].round(4)

        return prediction_df


class SklearnScorer(BaseModelScorer):
    '''
    SKlearn implementation of the model Scorer
    '''
    # class variables ----------------------------------------------------------

    # object methods -----------------------------------------------------------

    def __init__(self, model_type, target=None,target_orig_classes=[], target_int_values=[]):
        '''
        Initialize object by storing the relevant information.
        Use super class with model_type="sklearn".

        Parameters
        ----------
        model_origin : str
            The source of the model. Currently only "sklearn" implemented.
        model_type : str
            One of "classification" or "regression".
        target : str, optional
            The name of the target variable. The default is None.
        target_orig_classes : list of str, optional
            The list of class names, if model_type is "classification".
            The default is [].
        target_int_values : list of int, optional
            The list of class integer values, if model_type is "classification".
            The default is [].

        Returns
        -------
        None.

        '''
        super(self.__class__, self).__init__('sklearn', model_type, target, target_orig_classes, target_int_values)

        return None


    def setup(self, model):
        '''
        Implementation of the setup function from the base scorer.
        Store the model. If this is a bytes object, cloud-pickle it into
        the original model object.
        Uses cloudpickle.

        Parameters
        ----------
        model : pipeline, bytes or str
            The input model.

        Returns
        -------
        Itself.
            Use the base scorer to store model.

        '''
        if type(model)==bytes:
            import cloudpickle
            model=cloudpickle.loads(model)
        return super(self.__class__, self).setup(model)


    def predict(self, X):
        '''
        Apply model to data frame and return prediction array.

        Parameters
        ----------
        X : data frame
            The input data frame for calculating model predictions.

        Returns
        -------
        numpy.ndarray
            The predicted values, in a monodimensional array.

        '''
        return self.model.predict(X)


    def predict_probability(self, X):
        '''
        Apply model to data frame and return predicted class probabilities.

        Parameters
        ----------
        X : data frame
            The input data frame for calculating model predictions.

        Returns
        -------
        numpy.ndarray
            The predicted class probability, in an array of as many columns
            as there are classes.

        '''
        return self.model.predict_proba(X)



# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
# Evaluator classes

class BaseModelEvaluator():
    '''
    A base model Evaluator class to calculate performance metrics and variable
    importance.
    '''

    # class variables --------------------------------------------------
    variable_column = 'variable'
    value_column = 'value'
    relative_value_column = 'relative_value'

    #: str: prefix for json schema description
    evaluator_parms_description = 'init parameters for Evaluator'
    varimp_parms_description = 'data for variable importance'
    performance_parms_description = 'data for performance'

    # class utility functions --------------------------------------------------
    @classmethod
    def choose_evaluator(cls, model_type, sensitivity_metric):
        '''
        Class method.
        Invoke the appropriate Evaluator sub-class depending on the model type.

        Parameters
        ----------
        model_type : str
            One of "classification" or "regression".
        sensitivity_metric : str
            One of "rmse","mape", "r2" for regression, or "accuracy","fscore"
            for classification.

        Returns
        -------
        Either a RegressionModelEvaluator or a ClassificationModelEvaluator,
        depending on the value of model_type.
        '''

        if model_type == 'regression':
            return RegressionModelEvaluator(sensitivity_metric)
        elif model_type == 'classification':
            return ClassificationModelEvaluator(sensitivity_metric)

    @classmethod
    def get_negative_metrics(cls):
        '''
        Class method.
        Negative metrics = the lower, the better.

        Returns
        -------
        list
            A list of the supported negative metrics.

        '''
        return ['rmse', 'mape']

    @classmethod
    def get_positive_metrics(cls):
        '''
        Class method.
        Positive metrics = the higher, the better.

        Returns
        -------
        list
            A list of the supported positive metrics.
        '''
        return ['accuracy', 'fscore', 'r2']

    # object methods -----------------------------------------------------------

    def __init__(self, sensitivity_metric):
        '''
        Initialize object by storing the relevant information.
        Save instance attributes passed in into special
        instance variable __init_attributes__.

        Parameters
        ----------
        sensitivity_metric : : str
            One of "rmse","mape", "r2" for regression, or "accuracy","fscore"
            for classification.

        Raises
        ------
        NotImplementedError
            If the sensitivity metric is not implemented.

        Returns
        -------
        None.

        '''
        self.sensitivity_metric = sensitivity_metric
        # save a copy of the instance attributes that were passed to construction
        self.__init_attributes__ = self.__dict__.copy()
        if sensitivity_metric in self.__class__.get_positive_metrics():
            self.metric_direction = 1
        elif sensitivity_metric in self.__class__.get_negative_metrics():
            self.metric_direction = -1
        else:
            raise NotImplementedError(str(self.__class__)+'.__init__: The selected '+\
                                      sensitivity_metric+' sensitivity_metric is not implemented yet')

        return None

    def init_attributes_to_json(self):
        '''
        Collect the instance attributes defined at construction,
        and turn them into a json string.
        Used within a constructor method.

        Returns
        -------
        string
            JSON string containing instance attributes needed to
            configure scorer.

        '''
        return json.dumps(self.__init_attributes__)


    def setup(self, model_scorer):
        '''
        Store the model Scorer object in this Evaluator object.

        Parameters
        ----------
        model_scorer : subclass of BaseModelScorer
            The model Scorer for this Evaluator.

        Returns
        -------
        An object of this class.
        '''
        self.scorer = model_scorer
        return self

    def calc_permutation_sensitivity(self, X, y, num_repeats=3):
        '''
        Wrapper function to decide which version of permutation sensitivity
        to use, depending on the number of rows of the input data frame.
        For now, this limit is hard-coded to 10,000 rows, sampled to 5,000.

        Parameters
        ----------
        X : data frame
            The input data frame.
        y : numpy array or series
            The reference prediction.
        num_repeats : int, optional
            The number of times to repeat the calculation for each variable.
            The default is 3.

        Returns
        -------
        variable_importance_df : data frame
            The variable importance result.

        '''
        # If there are more than 10000 rows, calculate variable importance
        # ...with sampling
        if X.shape[0]>10000:
            #what fraction to sample to generate 5000 rows
            frac = 5000/X.shape[0]
            variable_importance_df = self.calc_permutation_sensitivity_with_sampling(X, y, num_repeats, sample_frac=frac)
        else:
            variable_importance_df = self.calc_permutation_sensitivity_no_sampling(X, y, num_repeats)

        return variable_importance_df


    def calc_permutation_sensitivity_no_sampling(self, X, y,num_repeats):
        '''
        Model agnostic variable importance using sensitivity
        needs multiple calls to model scoring
        In this version, no row sampling is done.

        Parameters
        ----------
        X : data frame
            The input data frame.
        y : numpy array or series
            The reference prediction.
        num_repeats : int
            The number of times to repeat the calculation for each variable.

        Returns
        -------
        sens_df : data frame
            The variable importance result.

        '''
        predictors = X.columns.tolist()
        sens_df = pd.DataFrame(predictors, columns=[self.__class__.variable_column])
        for pp in predictors:
            X_shuffle_pp = X.copy(deep=True)

            sensitivity_rep = [0]*num_repeats
            for rep in range(num_repeats):
                # Reshuffle column pp
                X_shuffle_pp[pp] = X[pp].sample(frac=1,random_state=rep).values
                # Score new dataset
                y_pred_pp = pd.Series(self.scorer.predict(X_shuffle_pp))
                sensitivity_rep[rep] = self.calc_individual_performance_metric(
                    self.sensitivity_metric, y_pred_pp, y)
            sensitivity = sum(sensitivity_rep)/num_repeats

            sens_df.loc[sens_df[self.__class__.variable_column] == pp, self.__class__.value_column] = \
                sensitivity if self.metric_direction == -1 else 1-sensitivity

        sens_df.sort_values(by=self.__class__.value_column, axis=0, ascending=False, inplace=True)
        max_sens = max(sens_df[self.__class__.value_column])
        sens_df[self.__class__.relative_value_column] = sens_df[self.__class__.value_column]/max_sens

        return sens_df


    def calc_permutation_sensitivity_with_sampling(self, X, y,num_repeats,sample_frac=0.3,replace=False):
        '''
        Model agnostic variable importance using sensitivity
        needs multiple calls to model scoring
        In this version, row sampling is performed.

        Parameters
        ----------
        X : data frame
            The input data frame.
        y : numpy array or series
            The reference prediction.
        num_repeats : int
            The number of times to repeat the calculation for each variable.
        sample_frac: real, optional''
            The fraction of rows to sample at every iteration.
            The default is 0.3.
        replace : bool, optional
            Whether to perform sampling with replacement. The default is False.

        Returns
        -------
        sens_df : data frame
            The variable importance result.

        '''
        predictors = X.columns.tolist()
        sens_df = pd.DataFrame(predictors, columns=[self.__class__.variable_column])
        if not isinstance(y,pd.Series):
            y=pd.Series(y)
        for pp in predictors:
            X_shuffle_pp = X.copy(deep=True)
            # Reshuffle column pp once
            X_shuffle_pp[pp] = X[pp].sample(frac=1,random_state=num_repeats+10).values

            sensitivity_rep = [0]*num_repeats
            for rep in range(num_repeats):
                # Score sample of new dataset (take SAME sample of y)
                y_pred_pp = pd.Series(self.scorer.predict(X_shuffle_pp.sample(frac=sample_frac, replace=replace,random_state=rep)))
                sensitivity_rep[rep] = self.calc_individual_performance_metric(
                    self.sensitivity_metric, y_pred_pp, y.sample(frac=sample_frac, replace=replace,random_state=rep))
            sensitivity = sum(sensitivity_rep)/num_repeats

            sens_df.loc[sens_df[self.__class__.variable_column] == pp, self.__class__.value_column] = \
                sensitivity if self.metric_direction == -1 else 1-sensitivity

        sens_df.sort_values(by=self.__class__.value_column, axis=0, ascending=False, inplace=True)
        max_sens = max(sens_df[self.__class__.value_column])
        sens_df[self.__class__.relative_value_column] = sens_df[self.__class__.value_column]/max_sens

        return sens_df


    def process(self, X, y=None):
        '''
        Calculate prediction, variable importance and performance
        (if label is provided). These are stored as object variables.
        If X has over 10,000 rows, the variable importance uses sampling to
        5,000 rows.

        Parameters
        ----------
        X : data frame
            The input data frame.
        y : series, optional
            The true label. The default is None.

        Returns
        -------
        None.

        '''
        if y is not None:
            y.reset_index(drop=True, inplace=True)
        # Calculate prediction data table, and isolate prediction column
        # ...into y_pred for calculating performance
        self.prediction_df = self.scorer.calc_prediction(X)
        y_pred = self.prediction_df[self.scorer.get_prediction_column()]
        # Calculate variable importance using permutation sensitivity
        self.variable_importance_df = self.calc_permutation_sensitivity(X, y_pred)

        # Calculate model performance (if y is available)
        self.performance_df = self.calc_model_performance(X, y_pred, y)

        return None


    def calc_individual_performance_metric(self, metric, y, y_pred, round_to=3):
        '''
        Individual call to a single performance metric.
        Implemented in sub classes.

        Parameters
        ----------
        metric : str
            The name of the performance metric.
        y : series
            The ground truth (label).
        y_pred : series
            The prediction.
        round_to : int, optional
            How many significant figures to round to. The default is 3.

        Returns
        -------
        None.

        '''
        pass


    def calc_model_performance(self, X, y_pred, y=None):
        '''
        Overall performance matrix.
        Implemented in sub classes.

        Parameters
        ----------
        metric : str
            The name of the performance metric.
        y : series
            The ground truth (label).
        y_pred : series
            The prediction.

        Returns
        -------
        None.

        '''
        pass

    def pack_json(self):
        '''
        Implemented in sub classes.

        Returns
        -------
        None.

        '''
        pass


class ClassificationModelEvaluator(BaseModelEvaluator):
    '''
    A classification model Evaluator class to calculate performance metrics and variable
    importance.
    '''
    # class utility functions --------------------------------------------------
    @classmethod
    def unpack_json(cls, received_json):
        '''
        Class method.
        Take the model JSON object of a classification model
        and re-build the original
        model metadata and metadata-processing classes.

        Parameters
        ----------
        received_json : str or dict
            The JSON object.

        Returns
        -------
        received_num_worker : NumericBinsWorker
            The object for binning numeric variables.
        received_cat_worker : CategoricalFrequenciesWorker
            The object for binning categorical variables.
        received_predicted_classes_df : data frame
            The baseline predictions.
        received_class_probabilities_df : data frame
            The baseline class probabilities, binned.
        received_model_scorer : a subclass of BaseModelScorer
            The model Scorer object.
        received_model_evaluator : ClassificationModelEvaluator
            The model Evaluator object.
        received_variable_importance_df : data frame
            The baseline variable importance.
        received_performance_df : data frame
            The baseline performance (empty if no target present).

        '''
        # Unpack json and create metadata workers
        #If the json is not in dictionary form, turn it into one
        if type(received_json)== str:
            received_json = json.loads(received_json)
        # Class probabilities (which were binned) and associated numeric bins worker
        received_num_worker, received_class_probabilities_df = mdd.NumericBinsWorker.unpack_json(
            received_json, return_df=True)

        # Predicted classes (which were binned) and associated categorical bins worker
        received_cat_worker, received_predicted_classes_df = mdd.CategoricalFrequenciesWorker.unpack_json(
            received_json, return_df=True)

        # Model scorer
        received_model_scorer = BaseModelScorer.unpack_json(received_json)
        # Variable importance, performance and associated model evaluator
        received_model_evaluator_attributes = json.loads(
            received_json['model_evaluator_json'])
        received_model_evaluator = cls(**received_model_evaluator_attributes)
        received_variable_importance_df = pd.DataFrame(
            json.loads(received_json['variable_importance_json']))
        received_performance_df = pd.DataFrame(
            json.loads(received_json['performance_json']))

        return (received_num_worker, received_cat_worker, received_predicted_classes_df,
                received_class_probabilities_df,
                received_model_scorer,
                received_model_evaluator, received_variable_importance_df, received_performance_df)

    # object methods -----------------------------------------------------------

    def setup(self, model_scorer):
        '''
        Store the specified model Scorer object in this object.
        Create a target map from origial class names to integer values.

        Parameters
        ----------
        model_scorer : A subclass of BaseModelScorer
            The Scorer object.

        Returns
        -------
        self
            This object.

        '''
        self.scorer = model_scorer
        self.target_map = pd.DataFrame({'target': model_scorer.get_orig_classes(), 'class': model_scorer.get_int_values()})

        return self


    def calc_individual_performance_metric(self, metric, y, y_pred, round_to=3):
        '''
        Individual call to a single performance metric.
        Calls sklearn.metrics to calculate the desired performance metric.

        Parameters
        ----------
        metric : str
            The name of the performance metric. One of "accuracy" or "fscore"
            (f1 weighted).
        y : series
            The ground truth (label).
        y_pred : series
            The prediction.
        round_to : int, optional
            How many significant figures to round to. The default is 3.


        Returns
        -------
        real
            The calculated performance metric.

        '''
        from sklearn.metrics import accuracy_score, f1_score

        if metric == 'accuracy':
            performance_metric = accuracy_score(y, y_pred)
        elif metric == 'fscore':
            # Default average is binary but we would need to define an int target class (pos_label)
            #np.unique(y_pred) is there to avoid warnings in case not all labels are represented
            performance_metric = f1_score(y, y_pred, average='weighted', labels=np.unique(y_pred))
        else:
            performance_metric = np.nan

        return round(performance_metric, round_to)


    def calc_model_performance(self, X, y_pred, y=None):
        '''
        If y is not null, calculate a performance table including
        precision, recall, fscore, support for each class.
        Otherwise return an empty data frame.
        Calls sklearn.metrics to calculate the desired performance metrics.

        Parameters
        ----------
        X : data frame
            The input dataset.
        y_pred : series
            The prediction.
        y : series, optional
            The ground truth (label). The default is None.

        Returns
        -------
        performance_df : data frame
            The performance table.

        '''
        from sklearn.metrics import precision_recall_fscore_support

        if y is None:
            performance_df = pd.DataFrame(
                columns=['precision', 'recall', 'fscore', 'support', 'class', 'target_class'])
        else:
            accuracy = self.calc_individual_performance_metric('accuracy', y, y_pred)
            #np.unique(y_pred) is there to avoid warnings in case not all labels are represented
            prfs = precision_recall_fscore_support(y, y_pred, labels=np.unique(y_pred))

            performance_df = pd.DataFrame(np.column_stack(prfs), columns=[
                                          'precision', 'recall', 'fscore', 'support'])
            performance_df['accuracy'] = accuracy
            performance_df['class'] = performance_df.index
            # Add actual target values
            performance_df = performance_df.merge(self.target_map, on='class')
            performance_df = pd.melt(performance_df, id_vars=['target', 'class'])

        return performance_df

    def pack_json(self):
        '''
        Take all information from this object, and turn it into
        JSON.

        Returns
        -------
        complete_json : str
            The complete description of this object as a JSON string.

        '''
        # Name of column containing the prediction
        pred_col = self.scorer.get_prediction_column()
        y_pred = self.prediction_df[[pred_col]].astype(object)
        y_prob = self.prediction_df[self.scorer.get_orig_classes()]

        # Decode predictions to original classes
        target_decode=dict(zip(self.scorer.get_int_values(),self.scorer.get_orig_classes()))
        #only decode if all the elements in the series to decode are contained in the mapper
        if all(item in y_pred[pred_col].unique().tolist() for item in list(target_decode.keys())):
            y_pred[pred_col]=y_pred[pred_col].map(target_decode)

        # Bin prediction and turn to json
        num_binner_parms = {'auto_detect_numeric': True, 'include_nulls': True,
                            'binning_type': '01',
                            'n_bins_max': 20,
                            'name_of_null_level': 'missing',
                            'name_of_outlier_level': 'outlier',
                            'numeric': []}

        num_schema, num_json_body, num_json_df =\
            mdd.NumericBinsWorker.pack_json(num_binner_parms, y_prob,
                                            'numeric_binner_json', 'binned_probabilities_json')

        # Store binned prediction
        self.class_probabilities_df = pd.DataFrame(json.loads(num_json_df))

        # Bin classes and turn to json
        cat_binner_parms = {'auto_detect_categories': True, 'include_nulls': True,
                            'empty_as_null': True,
                            'name_of_null_level': 'missing',
                            'categories': []}
        cat_schema, cat_json_body, cat_json_df =\
            mdd.CategoricalFrequenciesWorker.pack_json(cat_binner_parms, y_pred,
                                                       'cat_binner_json', 'binned_classes_json')
        # Store binned prediction
        self.predicted_classes_df = pd.DataFrame(json.loads(cat_json_df))

        # Model scorer
        scorer_schema, scorer_json = self.scorer.pack_json('scorer_json')

        # Model evaluator, variable importance and performance
        model_evaluator_json = self.init_attributes_to_json()
        variable_importance_json = self.variable_importance_df.to_json()
        performance_json = self.performance_df.to_json()

        evaluator_json = {'model_evaluator_json': model_evaluator_json,
                          'variable_importance_json': variable_importance_json,
                          'performance_json': performance_json}

        # Create labels and mini schema
        evaluator_parms_description = self.__class__.evaluator_parms_description
        varimp_parms_description = self.__class__.varimp_parms_description
        performance_parms_description = self.__class__.performance_parms_description
        evaluator_schema = {evaluator_parms_description: 'evaluator_parms',
                            varimp_parms_description: 'varimp_parms',
                            performance_parms_description: 'performance_parms'}
        # Build json: the schema and then the json body for each metadata class
        json_schema = {**num_schema, **cat_schema, **scorer_schema, **evaluator_schema}
        complete_json = {**evaluator_json, **num_json_body, **cat_json_body, **scorer_json}

        json_schema = json.dumps(json_schema)  # turn into a json string
        json_schema = {'schema': json_schema}  # create a dictionary

        # Build json: the schema and then the json body for each metadata class
        complete_json = {**json_schema, **complete_json}
        complete_json = json.dumps(complete_json)

        return (complete_json)
# ------------------------------------------------------------------------------


class RegressionModelEvaluator(BaseModelEvaluator):
    '''
    A regression model Evaluator class to calculate performance metrics and variable
    importance.
    '''

    # class utility functions --------------------------------------------------
    @classmethod
    def unpack_json(cls, received_json):
        '''
        Class method.
        Take the model JSON object of a regression model and re-build the original
        model metadata and metadata-processing classes.

        Parameters
        ----------
        received_json : str or dict
            The JSON object containing the model metadata.

        Returns
        -------
        received_num_worker : NumericBinsWorker
            The object for binning numeric variables.
        received_binned_prediction_df : data frame
            The baseline prediction table, binned.
        received_model_scorer : a subclass of BaseModelScorer
            The model Scorer object.
        received_model_evaluator : RegressionModelEvaluator
            The model Evaluator object.
        received_variable_importance_df : data frame
            The baseline variable importance.
        received_performance_df : data frame
            The baseline performance (empty if no target present).

        '''
        # Unpack json and create metadata workers
        #If the json is not in dictionary form, turn it into one
        if type(received_json)== str:
            received_json = json.loads(received_json)
        # Prediction (which was binned) and associated numeric bins worker
        received_num_worker, received_binned_prediction_df = mdd.NumericBinsWorker.unpack_json(
            received_json, return_df=True)

        # Model scorer
        received_model_scorer = BaseModelScorer.unpack_json(received_json)
        # Variable importance, performance and associated model evaluator
        received_model_evaluator_attributes = json.loads(
            received_json['model_evaluator_json'])
        received_model_evaluator = cls(**received_model_evaluator_attributes)
        received_variable_importance_df = pd.DataFrame(
            json.loads(received_json['variable_importance_json']))
        received_performance_df = pd.DataFrame(
            json.loads(received_json['performance_json']))

        return (received_num_worker, received_binned_prediction_df, received_model_scorer,
                received_model_evaluator, received_variable_importance_df, received_performance_df)

    # object methods -----------------------------------------------------------

    def setup(self, model_scorer):
        '''
        Store the model Scorer object in this Evaluator object.
        Use the base class method.

        Parameters
        ----------
        model_scorer : subclass of BaseModelScorer
            The model Scorer for this Evaluator.

        Returns
        -------
        An object of this class.
        '''

        return super(self.__class__, self).setup(model_scorer)


    def calc_individual_performance_metric(self, metric, y, y_pred, round_to=3):
        '''
        Individual call to a single performance metric.
        Calls sklearn.metrics to calculate the desired performance metric.

        Parameters
        ----------
        metric : str
            The name of the performance metric. One of "rmse",
            "mape" or "r2".
        y : series
            The ground truth (label).
        y_pred : series
            The prediction.
        round_to : int, optional
            How many significant figures to round to. The default is 3.


        Returns
        -------
        real
            The calculated performance metric.
        '''

        from sklearn.metrics import mean_squared_error, \
            mean_absolute_percentage_error, r2_score

        if metric == 'rmse':
            performance_metric = mean_squared_error(y, y_pred, squared=False)
        elif metric == 'mape':
            performance_metric = mean_absolute_percentage_error(y, y_pred)
        elif metric == 'r2':
            performance_metric = r2_score(y, y_pred)
        else:
            performance_metric = np.nan

        return round(performance_metric, round_to)


    def calc_residual_normality(self, y_res):
        '''
        Use scipy.stats with alpha=0.05 to evaluate residual normality.

        Parameters
        ----------
        y_res : vector of real.
            The residuals.

        Returns
        -------
        residual_normality : str
            Either 'normal', 'not normal' or nan.
        p : real
            The p value.

        '''

        # check if residual distribution is normal
        from scipy.stats import normaltest
        alpha = 0.05
        k2, p = normaltest(y_res)
        if p < alpha:
            residual_normality = 'not normal'
        elif p >= alpha:
            residual_normality = 'normal'
        else:
            residual_normality = np.nan

        return (residual_normality, p)


    def calc_model_performance(self, X, y_pred, y=None):
        '''
        If y is not null, calculate a performance table including
        rmse, mape, r2, residual normality and its p value.
        Otherwise return an empty data frame.

        Parameters
        ----------
        X : data frame
            The input dataset.
        y_pred : series
            The prediction.
        y : series, optional
            The ground truth (label). The default is None.

        Returns
        -------
        performance_df : data frame
            The performance table.

        '''

        df_cols = ['rmse', 'mape', 'r2', 'res_norm', 'res_norm_p']
        df_types = [pd.Series(dtype='float'), pd.Series(dtype='float'), pd.Series(
            dtype='float'), pd.Series(dtype='str'), pd.Series(dtype='float')]
        cols_types = dict(zip(df_cols, df_types))

        if y is None:
            performance_df = pd.DataFrame(cols_types)
        else:
            y = y.astype('float64')
            y_res = y-y_pred
            y_res = y_res.astype('float64')

            rmse = self.calc_individual_performance_metric('rmse', y, y_pred)
            mape = self.calc_individual_performance_metric('mape', y, y_pred)
            r2 = self.calc_individual_performance_metric('r2', y, y_pred)
            res_norm, res_norm_p = self.calc_residual_normality(y_res)
            prfs = [rmse, mape, r2, res_norm, res_norm_p]
            performance_df = pd.DataFrame(np.column_stack(prfs), columns=df_cols)

        return performance_df

    def pack_json(self):
        '''
        Take all information from this object, and turn it into
        JSON.

        Returns
        -------
        complete_json : str
            The complete description of this object as a JSON string.

        '''

        # Name of column containing the prediction
        pred_col = self.scorer.get_prediction_column()
        y_pred = self.prediction_df[[pred_col]]

        # Bin prediction and turn to json
        num_binner_parms = {'auto_detect_numeric': True, 'include_nulls': True,
                            'binning_type': 'quantile',
                            'n_bins_max': 10,
                            'name_of_null_level': 'missing',
                            'name_of_outlier_level': 'outlier',
                            'numeric': []}

        num_schema, num_json_body, num_json_df =\
            mdd.NumericBinsWorker.pack_json(num_binner_parms, y_pred,
                                            'numeric_binner_json', 'binned_prediction_json')
        # Store binned prediction
        self.binned_prediction_df = pd.DataFrame(json.loads(num_json_df))

        # Model scorer
        scorer_schema, scorer_json = self.scorer.pack_json('scorer_json')

        # Model evaluator, variable importance and performance
        model_evaluator_json = self.init_attributes_to_json()
        variable_importance_json = self.variable_importance_df.to_json()
        performance_json = self.performance_df.to_json()

        evaluator_json = {'model_evaluator_json': model_evaluator_json,
                          'variable_importance_json': variable_importance_json,
                          'performance_json': performance_json}

        # Create labels and mini schema
        evaluator_parms_description = self.__class__.evaluator_parms_description
        varimp_parms_description = self.__class__.varimp_parms_description
        performance_parms_description = self.__class__.performance_parms_description
        evaluator_schema = {evaluator_parms_description: 'evaluator_parms',
                            varimp_parms_description: 'varimp_parms',
                            performance_parms_description: 'performance_parms'}

        # Build json: the schema and then the json body for each metadata class
        json_schema = {**num_schema, **scorer_schema, **evaluator_schema}
        complete_json = {**evaluator_json, **num_json_body, **scorer_json}

        json_schema = json.dumps(json_schema)  # turn into a json string
        json_schema = {'schema': json_schema}  # create a dictionary

        # Build json: the schema and then the json body for each metadata class
        complete_json = {**json_schema, **complete_json}
        complete_json = json.dumps(complete_json)

        return (complete_json)


# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------

# INTERNAL ENTRY POINTs


def init_scorer(score_mechanism, model, model_type, target=None,
                target_orig_classes=[], target_int_values=[]):
    '''
    Create a new Scorer object of the desired type.

    Parameters
    ----------
    score_mechanism : str
        The source of the model. Currently only "sklearn" implemented.
    model : bytes or sklearn pipeline
        The model object.
    model_type : str
        One of "classification" or "regression".
    target : str, optional
        The name of the target variable. The default is None.
    target_orig_classes : list of str, optional
        The list of class names, if model_type is "classification".
        The default is [].
    target_int_values : list of int, optional
        The list of class integer values, if model_type is "classification".
        The default is [].

    Returns
    -------
    scorer : Subclass of BaseModelScorer
        Currently returns an instance of SklearnScorer, or None if
        model_origin not "sklearn".

    '''
    scorer = BaseModelScorer.choose_scorer(score_mechanism, model_type, target,target_orig_classes, target_int_values)
    scorer.setup(model)

    return scorer


def init_evaluator(scorer, sensitivity_metric):
    '''
    Invoke the appropriate Evaluator sub-class depending on the model type.

    Parameters
    ----------
    scorer : Subclass of BaseModelScorer
        The model Scorer object to use.
    sensitivity_metric : str
        One of "rmse","mape", "r2" for regression, or "accuracy","fscore"
        for classification.

    Returns
    -------
    Either a RegressionModelEvaluator or a ClassificationModelEvaluator,
    depending on the value of the model_type stored within the Scorer
    object.
    '''
    model_type = scorer.model_type
    evaluator = BaseModelEvaluator.choose_evaluator(model_type, sensitivity_metric)
    evaluator.setup(scorer)

    return evaluator



def unpack_classification_model_metadata(complete_json, model):
    '''
    Take the model JSON string of a classification model and re-build the original
    model metadata and metadata-processing classes. Add the model to the Scorer
    object and add this to the Evaluator object.

    Parameters
    ----------
    complete_json : str or dict
        The JSON object containing the model metadata.
    model : bytes or sklearn pipeline
        The classification model object.

    Returns
    -------
    received_num_worker : NumericBinsWorker
        The object for binning numeric variables.
    received_cat_worker : CategoricalFrequenciesWorker
        The object for binning categorical variables.
    received_predicted_classes_df : data frame
        The baseline predictions.
    received_class_probabilities_df : data frame
        The baseline class probabilities, binned.
    received_model_scorer : a subclass of BaseModelScorer
        The model Scorer object.
    received_model_evaluator : RegressionModelEvaluator
        The model Evaluator object.
    received_variable_importance_df : data frame
        The baseline variable importance.
    received_performance_df : data frame
        The baseline performance (empty if no target present).

    '''
    received_num_worker, received_cat_worker, received_predicted_classes_df, \
        received_class_probabilities_df,\
        received_model_scorer,\
        received_model_evaluator, received_variable_importance_df, received_performance_df\
        = ClassificationModelEvaluator.unpack_json(complete_json)

    received_model_scorer.setup(model)
    received_model_evaluator.setup(received_model_scorer)

    return (received_num_worker, received_cat_worker,
            received_predicted_classes_df, received_class_probabilities_df,
            received_model_scorer,
            received_model_evaluator, received_variable_importance_df, received_performance_df)


def unpack_regression_model_metadata(complete_json, model):
    '''
    Take the model JSON string of a regression model and re-build the original
    model metadata and metadata-processing classes. Add the model to the Scorer
    object and add this to the Evaluator object.

    Parameters
    ----------
    complete_json : str or dict
        The JSON object containing the model metadata.
    model : bytes or sklearn pipeline
        The regression model object.

    Returns
    -------
    received_num_worker : NumericBinsWorker
        The object for binning numeric variables.
    received_binned_prediction_df : data frame
        The baseline prediction table, binned.
    received_model_scorer : a subclass of BaseModelScorer
        The model Scorer object.
    received_model_evaluator : RegressionModelEvaluator
        The model Evaluator object.
    received_variable_importance_df : data frame
        The baseline variable importance.
    received_performance_df : data frame
        The baseline performance (empty if no target present).

    '''
    received_num_worker, received_binned_prediction_df, received_model_scorer,\
        received_model_evaluator, received_variable_importance_df, received_performance_df\
        = RegressionModelEvaluator.unpack_json(complete_json)

    received_model_scorer.setup(model)
    received_model_evaluator.setup(received_model_scorer)

    return (received_num_worker, received_binned_prediction_df, received_model_scorer,
            received_model_evaluator, received_variable_importance_df, received_performance_df)


#
#
# --- USER ENTRY POINTs--------------------------------------------------------

def calculate_classification_model_metadata(model, df, target,encode_target,
                            target_orig_classes,target_int_values,scorer_type='sklearn'):
    '''
    Calculate initial model metadata and return JSON object. In addition, return
    initial variable importance, performance (if target present in input dataset),
    predictions and class probabilities tables.

    Parameters
    ----------
    model : bytes or sklearn pipeline
        The model to use for predictions.
    df : data frame
        The input dataset. This is supposed to contain only the predictor
        variables. It might also contain the target variable, but this will
        be removed before processing.
    target : str
        The name of classification target variable.
    encode_target : bool
        If True, we assume the target column has been encoded when training
        the model.
    target_orig_classes : list
        The names of the original target classes, before any encoding.
    target_int_values : TYPE
        The target integer values, in order.
    scorer_type : str, optional
        The type of Scorer object to initialize. Currently
        only "sklearn" (the default) is supported.

    Returns
    -------
    complete_json : str
        The model metadata.
    data frame
        variable importance.
    data frame
        performance. Empty if no target variable present.
    data frame
        predictions.
    data frame
        class probabilities. These are binned to 20 bins.

    '''

    # Prepare dataset
    predictors = list(df.columns)
    if target in predictors:
        predictors.remove(target)
        y = df[target]
    else:
        y = None
    X = df[predictors]

    # Create a target map: from original values to integers
    target_orig_classes=target_orig_classes.split(',')
    target_int_values=target_int_values.split(',')
    target_encode0=dict(zip(target_orig_classes,[int(x) for x in target_int_values]))
    #if we had encoded the target when generating the model, do it here
    if encode_target and y is not None:
        y=y.map(target_encode0)
        y=y.astype(int)
    # Initiate scorer and evaluator ----------------------------------------------------------------
    model_scorer = init_scorer(scorer_type, model, 'classification', target, target_orig_classes, target_int_values)
    model_evaluator = init_evaluator(model_scorer, 'fscore')
    # Calculate metrics ----------------------------------------------------------------------------
    model_evaluator.process(X, y)

    # Build json object ----------------------------------------------------------------------------
    complete_json = model_evaluator.pack_json()

    return (complete_json, model_evaluator.variable_importance_df,
            model_evaluator.performance_df, model_evaluator.predicted_classes_df,
            model_evaluator.class_probabilities_df)


def calculate_regression_model_metadata(model, df, target,scorer_type='sklearn'):
    '''
    Calculate initial model metadata and return JSON object. In addition, return
    initial variable importance, performance (if target present in input dataset),
    predictions tables.

    Parameters
    ----------
    model : bytes or sklearn pipeline
        The model to use for predictions.
    df : data frame
        The input dataset. This is supposed to contain only the predictor
        variables. It might also contain the target variable, but this will
        be removed before processing.
    target : str
        The name of classification target variable.
    scorer_type : str, optional
        The type of Scorer object to initialize. Currently
        only "sklearn" (the default) is supported.

    Returns
    -------
    complete_json : str
        The model metadata.
    data frame
        variable importance.
    data frame
        performance. Empty if no target variable present.
    data frame
        predictions. These are binned to 10 quantile bins.

    '''
    # Prepare dataset
    predictors = list(df.columns)
    if target in predictors:
        predictors.remove(target)
        y = df[target]
    else:
        y = None
    X = df[predictors]

    # Initiate scorer and evaluator -------------------------------------------
    model_scorer = init_scorer(scorer_type, model, 'regression', target)
    model_evaluator = init_evaluator(model_scorer, 'mape')
    # Calculate metrics -------------------------------------------------------
    model_evaluator.process(X, y)

    # Build json object -------------------------------------------------------
    complete_json = model_evaluator.pack_json()

    return (complete_json, model_evaluator.variable_importance_df,
            model_evaluator.performance_df, model_evaluator.binned_prediction_df)


# MAIN ------------------------------------------------------------------------
if __name__ == '__main__':
    pass
