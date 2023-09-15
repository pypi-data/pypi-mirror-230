
# In standalone mode (running 'main'), create matplotlib plots as well if PLOTS = True.
# 'main' sets PLOTS = True, and resets it to FALSE.
# You can also set PLOT = True here when using the functions in Spotfire, in which
# case matplotlib plots will pop up, without you having to create Spotfire visualizations,
# which may be a good debugging tool to have.

PLOTS = False


# Ideally, we would make this function non-exportable. That, however, is not really an option in Python.
# Instead signal to other programmers using a leading underscore in the name.

def _ExtractColumnLists(dfX, max_low_cardinality, max_high_cardinality):
    
    '''
    Generates four lists that the ColumnTransformers need in the pipeline definition.
    The responsibility of setting default values for max_low_cardinality and max_high_cardinality is
    placed on the callers.

    input: dfX = dataframe
           max_low_cardinality = maximum cardinality for one hot encoding, otherwise target encoding
           max_high_cardinality = maximum cardinality, if higher the feature is ignored

    output: lists of numeric, categoric, low and high cardinality categoric features
    
    '''
    
    import pandas as pd
    import numpy as np
    
    categoric_columns = dfX.select_dtypes(exclude=np.number).columns
    numeric_columns = dfX.select_dtypes(include=np.number).columns

    low_cardinality_categoric_columns = []
    high_cardinality_categoric_columns = []
    for col in categoric_columns:
        non_nan_values = dfX.loc[:,col].dropna().values
        cardinality = len(np.unique(non_nan_values))
        if cardinality < max_low_cardinality + 1:
            low_cardinality_categoric_columns.append(col)
        elif cardinality < max_high_cardinality + 1:
            high_cardinality_categoric_columns.append(col)
                    
    return numeric_columns, categoric_columns, low_cardinality_categoric_columns, high_cardinality_categoric_columns


def _ExtractGridSearchData(cv_results_, grid_args, mode):

    '''
    Creates dataframe df_cv_results for plotting a parallel coordinates plot with grid search results
    
    mode: 'classifier' or 'regressor'
    
    '''

    import pandas as pd

    df_cv_results = pd.DataFrame.from_dict(cv_results_['params'])
    df_cv_results['mean_test_score'] = (-1 ** int(mode=='regression')) * cv_results_['mean_test_score']
    df_cv_results = df_cv_results.sort_values('mean_test_score', ascending=(mode=='regression'))

    if False:

        import matplotlib.pyplot as plt
        from yellowbrick.features import ParallelCoordinates
        
        df_cv_results_plot = df_cv_results.copy()
        df_cv_results_plot['mean_test_score_bin'] = pd.cut(df_cv_results_plot['mean_test_score'], bins=df_cv_results.shape[0], labels=False)
        df_cv_results_plot = df_cv_results_plot.select_dtypes(exclude='object')
        df_cv_results_plot.loc[:,'mean_test_score_bin'] = df_cv_results_plot.loc[:,'mean_test_score_bin']
        df_cv_results_plot = df_cv_results_plot.sort_values(by='mean_test_score_bin')
        
        features = df_cv_results_plot.columns[:-1]
        classes = list(sorted(df_cv_results_plot['mean_test_score_bin'].unique()))
        
        df_cv_results_plot.loc[:,'mean_test_score_bin'] = df_cv_results_plot.loc[:,'mean_test_score_bin'].astype(str)

        print(df_cv_results_plot[['mean_test_score','mean_test_score_bin']])
        print(df_cv_results_plot.dtypes)

        features = df_cv_results_plot.columns[:-1]
        classes = list(df_cv_results_plot['mean_test_score_bin'].unique())

        print(features)
        print(classes)
    
        fig, ax = plt.subplots()
        kwargs = {}
        pc = ParallelCoordinates(classes=classes, features=features, normalize='minmax', colormap='coolwarm', **kwargs)
        pc.fit(df_cv_results_plot[features], df_cv_results_plot['mean_test_score_bin'])
        pc.transform(df_cv_results_plot[features])
        ax.set_xticklabels(ax.get_xticklabels(), rotation=45)
        pc.poof()
        plt.show()
    

    return df_cv_results


def CreateClassificationPipeline(dfX,
                                 max_low_cardinality=6,
                                 max_high_cardinality=50,
                                 algo='randomforest',
                                 classifier_args={}):
    
    '''
    Creates a Pipeline object.
    
    Categorical pipeline:
    SimpleImputer + [OneHotEncoder (if low cardinality) | TargetEncoder (if higher cardinality) | drop feature (highest cardinality)]

    Numeric pipeline:
    SimpleImputer(mean) + StandardScaler + Addition new feature: outlier_score

    Classifier:
    RandomForestClassifier | XGBClassifier | LogisticRegression | KerasClassifier

    input: dfX = training data, sued here to extract num v low cardinality cat v high cardinality cat
           max_low_cardinality (optional) = max cardinality for one hot encoding, otherwise target encoding
           max_high_cardinality (optional) = features with higher cardinality are ignored
           algo (optional) = classification algorithm
           classifier_args (optional) = dictionary of arguments passed to the classifier specified in algo

    output: classifier pipeline object (untrained) 
    
    '''

    from sklearn.compose import ColumnTransformer
    from sklearn.impute import SimpleImputer
    from sklearn.pipeline import Pipeline
    from sklearn.preprocessing import StandardScaler, OneHotEncoder
    from sklearn.preprocessing import FunctionTransformer
    
    from category_encoders.target_encoder import TargetEncoder
    
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.linear_model import LogisticRegression
    from xgboost import XGBClassifier

    import numpy as np

    if algo == 'randomforest':
        
        # possibly remove k,v pairs from input classifier_args if we want them hardcoded here
        classifier = RandomForestClassifier(**classifier_args)
        
    elif algo == 'xgboost':
        
        # remove k,v pairs from input classifier_args that we want hardcoded here
        if 'objective' in classifier_args.keys():
            del classifier_args['objective']
        if 'eval_metric' in classifier_args.keys():
            del classifier_args['eval_metric']
        if 'use_label_encoder' in classifier_args.keys():
            del classifier_args['use_label_encoder']
        classifier = XGBClassifier(objective='binary:logistic',
                                   eval_metric='logloss',
                                   use_label_encoder=False, 
                                   **classifier_args)
        
    elif algo == 'logisticregression':
        
        # possibly remove k,v pairs from classifier_args if we want them hardcoded here
        classifier = LogisticRegression(**classifier_args)
        
    elif algo == 'neuralnet':
        
        import tensorflow as tf
        from tensorflow import keras
        from scikeras.wrappers import KerasClassifier

        tf.random.set_seed(59)

        if 'patience' in classifier_args.keys():
            patience = classifier_args['patience']
        else:
            patience = 10

        if 'epochs' in classifier_args.keys():
            epochs = classifier_args['epochs']
        else:
            epochs = 100    

        if 'batch_size' in classifier_args.keys():
            batch_size = classifier_args['batch_size']
        else:
            batch_size = min(100, int(dfX.shape[0]/10))

        if 'hidden_layers_sizes' in classifier_args.keys():
            hidden_layers_sizes = classifier_args['hidden_layers_sizes']
        else:
            nn = int(np.sqrt(0.5 * dfX.shape[0]))
            hidden_layers_sizes = (nn,nn,)

        if 'learning_rate' in classifier_args.keys():
            learning_rate = classifier_args['learning_rate']
        else:
            learning_rate = 0.001

        if 'dropout' in classifier_args.keys():
            dropout = classifier_args['dropout']
        else:
            dropout = 0.1
            
        early_stopping_callback = tf.keras.callbacks.EarlyStopping(monitor='val_loss', 
                                                                   mode='min',
                                                                   patience=patience,
                                                                   restore_best_weights=True,
                                                                   verbose=1)

        # For now: disable one-hot encoding and dropping of non-numeric variables,
        # to avoid logic to determine input_shape inside the pipeline. That is:
        # we use targetEncoder for all non-numeric variables

        n_in = dfX.shape[1]
        max_low_cardinality = 0
        max_high_cardinality = 10000

        def build_classifier_neural_net(hidden_layers_sizes, dropout, n_in):

            model = keras.models.Sequential()
            model.add(keras.layers.Input(shape=(n_in,)))
            for hidden_layer_size in hidden_layers_sizes:
                model.add(keras.layers.Dense(hidden_layer_size, activation='relu'))
                model.add(keras.layers.Dropout(dropout))
            model.add(keras.layers.Dense(1, activation='sigmoid'))
            return model
  
        params_keras = {'model__n_in':n_in,
                        'model__hidden_layers_sizes':hidden_layers_sizes,
                        'model__dropout':dropout,
                        'optimizer':'adam',
                        'optimizer__learning_rate':learning_rate,
                        'validation_split':0.1,
                        'epochs':epochs,
                        'batch_size':batch_size,
                        'loss':'binary_crossentropy',
                        'callbacks':[early_stopping_callback],
                        'verbose':0
                        }
        
        classifier = KerasClassifier(model=build_classifier_neural_net, **params_keras) 
        
    else:
        
        raise ValueError('The algorithm {} is not supported. \
                          The options are: randomforest, xgboost, logisticregression, neuralnet'.format(algo))
    
    numeric_columns, categoric_columns, low_cardinality_categoric_columns, high_cardinality_categoric_columns = \
        _ExtractColumnLists(dfX, max_low_cardinality, max_high_cardinality)

    high_cardinality_cat_encoder_pipe = Pipeline([
        ('imputer', SimpleImputer(strategy='constant', fill_value='NA')),
        ('high_cardinality_encoding', TargetEncoder())
    ])

    low_cardinality_cat_encoder_pipe = Pipeline([
        ('imputer', SimpleImputer(strategy='constant', fill_value='NA')),
        ('low_cardinality_encoding', OneHotEncoder(handle_unknown='ignore'))
    ])

    cat_encoder_pipe = ColumnTransformer([
        ('high_cardinality', high_cardinality_cat_encoder_pipe, high_cardinality_categoric_columns),
        ('low_cardinality', low_cardinality_cat_encoder_pipe, low_cardinality_categoric_columns)    
    ])

    # categoric preprocessing
    categoric_pipe = Pipeline([
        ('encoder', cat_encoder_pipe)
    ])

    numeric_pipe = Pipeline([
        ('imputer', SimpleImputer()),
        ('scaler', StandardScaler())
    ])

    # this allows for separate processing of categoric and numeric features
    preprocessing = ColumnTransformer(
        [('cat', categoric_pipe, categoric_columns),
         ('num', numeric_pipe, numeric_columns)])

    # final random forest pipeline
    classifier_pipeline = Pipeline([
        ('preprocess', preprocessing),
        ('classifier', classifier)
    ])
    
    return classifier_pipeline



def TrainXGBClassifier(pipeline, dfX_train, dfy_train, dfX_test=None, dfy_test=None, classifier_args={}):

    """
    Dedicate train function for pipelines with an XGB classifier, supporting early_stopping_rounds

    """

    from sklearn.pipeline import Pipeline
    from xgboost import XGBClassifier

    if 'early_stopping_rounds' in classifier_args.keys() and dfX_test is not None and dfy_test is not None:

        fitted_preprocessor = pipeline['preprocess'].fit(dfX_train, dfy_train)
        dfX_test_trans = fitted_preprocessor.transform(dfX_test)
        fit_params = {'classifier__eval_set':[(dfX_test_trans, dfy_test)],
                      'classifier__verbose':True
                     }
    else:
        fit_params = {}

    model = pipeline.fit(dfX_train, dfy_train, **fit_params)

    return model


def TrainClassifier(pipeline, dfX_train, dfy_train, dfX_test=None, dfy_test=None, classifier_args={}):

    """
    Dedicate train function for classifier pipelines

    """

    from sklearn.pipeline import Pipeline

    algo = str(pipeline.named_steps['classifier']).split('(')[0]


    if algo != 'XGBClassifier':

        model = pipeline.fit(dfX_train, dfy_train)

    else:

        if 'early_stopping_rounds' in classifier_args.keys() and dfX_test is not None and dfy_test is not None:

            fitted_preprocessor = pipeline['preprocess'].fit(dfX_train, dfy_train)
            dfX_test_trans = fitted_preprocessor.transform(dfX_test)
            fit_params = {'classifier__eval_set':[(dfX_test_trans, dfy_test)],
                          'classifier__verbose':True
                         }
        else:
            fit_params = {}

        model = pipeline.fit(dfX_train, dfy_train, **fit_params)

    return model

    
    
def ClassificationGridSearchCV(pipeline,
                               dfX_train, dfy_train,
                               dfX_test=None, dfy_test=None,
                               cv=4,
                               scoring='roc_auc',
                               pos_label=1,
                               classifier_grid_args={}):
    
    '''
    Performs a grid search to train the pipeline 
    scoring: 'roc_auc' or 'average_precision'

    input: pipeline, pipeline to be trained using grid search
           dfX_train, dfy_train are dataframes
           dfX_test, dfy_test are dataframes only needed for xgb pipelines for early stopping (to do)
           scoring = 'roc_auc' or 'average_precision'

    output: trained classifier pipeline
    
    '''

    import numpy as np
    import pandas as pd
    from sklearn.model_selection import GridSearchCV
    
    algo = str(pipeline.named_steps['classifier']).split('(')[0]
 
    if algo == 'RandomForestClassifier':
        
        print('Grid search with RandomForestClassifier')
        
        if not classifier_grid_args:
            pipeline_params = {
                           'preprocess__num__imputer__strategy':['mean'],
                           'classifier__n_estimators':[100],
                           'classifier__min_samples_leaf':[1,2,3],
                           'classifier__class_weight':['balanced',None],
                           }
        else:
            pipeline_params = {
                           'preprocess__num__imputer__strategy':['mean'],
                           }

            for k,v in classifier_grid_args.items():
                pipeline_params['classifier__' + k] = v  
              
        fit_params = {         
                     }

    elif algo == 'XGBClassifier':
        
        print('Grid search with XGBClassifier')
        
        y_pos = len(dfy_train[dfy_train == pos_label])
        y_min = len(dfy_train[dfy_train != pos_label])
        scale_pos_weight = (1.0*y_min)/y_pos
        
        if not classifier_grid_args:
            
            pipeline_params = {
                           'classifier__n_estimators':[50,100],
                           'classifier__scale_pos_weight':[scale_pos_weight, 1],
                           'classifier__min_child_weight':[1,2],
                           'classifier__learning_rate':[0.1,0.03],
                           'classifier__max_depth':[5,6],
                           'classifier__use_label_encoder':[False],
                           'classifier__objective':['binary:logistic'],
                           }
        else:
            
            pipeline_params = {
                           'preprocess__num__imputer__strategy':['mean'],
                           }

            for k,v in classifier_grid_args.items():
                           pipeline_params['classifier__' + k] = v   
        fit_params = {         
                     }
        
    elif algo == 'LogisticRegression':
        
        print('Grid search with LogisticRegression')
        
        if not classifier_grid_args:
            
            pipeline_params = {
                           'preprocess__num__imputer__strategy':['mean'],
                           'classifier__class_weight':['balanced', None],
                           'classifier__C':[0.01, 0.1, 1, 10, 100],
                          }
        else:
            
            pipeline_params = {
                           'preprocess__num__imputer__strategy':['mean'],
                           }
            
            for k,v in classifier_grid_args.items():
                           pipeline_params['classifier__' + k] = v              
        fit_params = {  
                     }

    elif algo == 'KerasClassifier':

        print('Grid search with KerasClassifier')
        
        if not classifier_grid_args:
            
            param_grid = {'classifier__model__n_in':[dfX_train.shape[1]],
                          'classifier__model__hidden_layers_sizes':[(1000,),(500,500,),(333,334,333,)],
                          'classifier__optimizer__learning_rate':[0.003,0.01],
                          'classifier__batch_size':[100,1000],
                          'classifier__epochs':[200]
                         }

        else:

            param_grid = {'classifier__model__n_in':[dfX_train.shape[1]]
                         }

            for k,v in classifier_grid_args.items():

                if k in ('hidden_layers_sizes','dropout'):
                    param_grid['classifier__model__' + k] = v
                elif k in ('learning_rate'):
                    param_grid['classifier__optimizer__' + k] = v
                else:
                    param_grid['classifier__' + k] = v
        
    
    if algo != 'KerasClassifier':
        
        grid = GridSearchCV(estimator=pipeline, 
                            param_grid=pipeline_params, 
                            cv=cv,
                            scoring=scoring, 
                            refit=True,
                            verbose=1,
                            n_jobs=1)
    else:

        grid = GridSearchCV(pipeline, param_grid=param_grid, scoring='roc_auc')

    import time
    start = time.time()
    trained_classifier = grid.fit(dfX_train, dfy_train) #, **fit_params)
    print("Running time =", time.time() - start, "seconds")

    df_grid_search = _ExtractGridSearchData(grid.cv_results_, classifier_grid_args, 'classification')
        
    return trained_classifier



def CreateRegressionPipeline(dfX,
                             max_low_cardinality=6,
                             max_high_cardinality=50,
                             algo='randomforest',
                             regressor_args={}):

    '''
    Creates a Pipeline object
    Categorical pipeline: SimpleImputer + OneHotEncoder (low cardinailty) + TargetEncoder (high cardinality)
    Numeric pipeline: SimpleImputer + StandardScaler
    Regressor: RandomForestRegressor | XGBRegressor | Ridge | Lasso | KerasRegressor

    input: dfX = training data, sued here to extract num v low cardinality cat v high cardinality cat
           max_low_cardinality = max cardinality for one hot encoding, otherwise target encoding
           max_high_cardinality = features with higher cardinality are ignored
           algo = classification algorithm

    output: regressor pipeline object (untrained)
    
    '''

    from sklearn.compose import ColumnTransformer
    from sklearn.impute import SimpleImputer
    from sklearn.pipeline import Pipeline
    from sklearn.preprocessing import StandardScaler, OneHotEncoder
    
    from category_encoders.target_encoder import TargetEncoder
    
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.linear_model import Ridge, Lasso
    from xgboost import XGBRegressor

    import numpy as np

    if algo == 'randomforest':
        
        regressor = RandomForestRegressor(**regressor_args)
        
    elif algo == 'xgboost':
        
        # remove k,v pairs from regressor_args that we want them hardcoded here
        if 'objective' in regressor_args.keys():
            del regressor_args['objective']
        if 'eval_metric' in regressor_args.keys():
            del regressor_args['eval_metric']
        if 'use_label_encoder' in regressor_args.keys():
            del regressor_args['use_label_encoder']
        regressor = XGBRegressor(objective='reg:squarederror',
                                 use_label_encoder=False,
                                 **regressor_args)
        
    elif algo == 'ridge':
        
        regressor = Ridge(**regressor_args)
        
    elif algo == 'lasso':
        
        regressor = Lasso(**regressor_args)

    elif algo == 'neuralnet':
        
        import tensorflow as tf
        from tensorflow import keras
        from scikeras.wrappers import KerasRegressor

        tf.random.set_seed(59)

        if 'patience' in regressor_args.keys():
            patience = regressor_args['patience']
        else:
            patience = 10

        if 'epochs' in regressor_args.keys():
            epochs = regressor_args['epochs']
        else:
            epochs = 100    

        if 'batch_size' in regressor_args.keys():
            batch_size = regressor_args['batch_size']
        else:
            batch_size = min(100, int(dfX.shape[0]/10))

        if 'hidden_layers_sizes' in regressor_args.keys():
            hidden_layers_sizes = regressor_args['hidden_layers_sizes']
        else:
            nn = int(np.sqrt(0.5 * dfX.shape[0]))
            hidden_layers_sizes = (nn,nn,)

        if 'learning_rate' in regressor_args.keys():
            learning_rate = regressor_args['learning_rate']
        else:
            learning_rate = 0.001

        if 'dropout' in regressor_args.keys():
            dropout = regressor_args['dropout']
        else:
            dropout = 0.1
            
        early_stopping_callback = tf.keras.callbacks.EarlyStopping(monitor='val_loss', 
                                                                   mode='min',
                                                                   patience=patience,
                                                                   restore_best_weights=True,
                                                                   verbose=1)

        # For now: disable one-hot encoding and dropping of non-numeric variables,
        # to avoid logic to determine input_shape inside the pipeline. That is:
        # we use targetEncoder for all non-numeric variables
        
        n_in = dfX.shape[1]
        max_low_cardinality = 0
        max_high_cardinality = 10000

        def build_regressor_neural_net(hidden_layers_sizes, dropout, n_in):

            model = keras.models.Sequential()
            model.add(keras.layers.Input(shape=(n_in,)))
            for hidden_layer_size in hidden_layers_sizes:
                model.add(keras.layers.Dense(hidden_layer_size, activation='relu'))
                model.add(keras.layers.Dropout(dropout))
            model.add(keras.layers.Dense(1, activation=None))
            return model
  
        params_keras = {'model__n_in':n_in,
                        'model__hidden_layers_sizes':hidden_layers_sizes,
                        'model__dropout':dropout,
                        'optimizer':'adam',
                        'optimizer__learning_rate':learning_rate,
                        'validation_split':0.1,
                        'epochs':epochs,
                        'batch_size':batch_size,
                        'loss':'mean_squared_error',
                        'callbacks':[early_stopping_callback],
                        'verbose':0
                        }
        
        regressor = KerasRegressor(model=build_regressor_neural_net, **params_keras)       
        
    else:
        
        raise ValueError('The algorithm {} is not supported. The options are: randomforest, xgboost, ridge, neuralnet.'.format(algo))
    
    numeric_columns, categoric_columns, low_cardinality_categoric_columns, high_cardinality_categoric_columns = \
        _ExtractColumnLists(dfX, max_low_cardinality, max_high_cardinality)

    high_cardinality_cat_encoder_pipe = Pipeline([
        ('imputer', SimpleImputer(strategy='constant', fill_value='NA')),
        ('high_cardinality_encoding', TargetEncoder()),
        ('high_cardinality_scaling', StandardScaler())
    ])

    low_cardinality_cat_encoder_pipe = Pipeline([
        ('imputer', SimpleImputer(strategy='constant', fill_value='NA')),
        ('low_cardinality_encoding', OneHotEncoder(handle_unknown='ignore'))
    ])

    cat_encoder_pipe = ColumnTransformer([
        ('high_cardinality', high_cardinality_cat_encoder_pipe, high_cardinality_categoric_columns),
        ('low_cardinality', low_cardinality_cat_encoder_pipe, low_cardinality_categoric_columns)    
    ])

    # categoric preprocessing
    categoric_pipe = Pipeline([
        #('imputer', SimpleImputer(strategy='constant', fill_value='NA')),
        ('encoder', cat_encoder_pipe)
    ])

    # numeric preprocessing
    numeric_pipe = Pipeline([
        ('imputer', SimpleImputer()),
        ('scaler', StandardScaler())
    ])

    # this allows for separate processing of categoric and numeric
    preprocessing = ColumnTransformer(
        [('cat', categoric_pipe, categoric_columns),
         ('num', numeric_pipe, numeric_columns)])

    # final random forest pipeline
    regressor_pipeline = Pipeline([
        ('preprocess', preprocessing),
        ('regressor', regressor)               
    ])
    
    return regressor_pipeline


def TrainXGBRegressor(pipeline, dfX_train, dfy_train, dfX_test=None, dfy_test=None, regressor_args={}):

    """
    Dedicate train function for pipelines with an XGB regressor, supporting early_stopping_rounds

    """


    from sklearn.pipeline import Pipeline
    from xgboost import XGBRegressor

    if 'early_stopping_rounds' in regressor_args.keys() and dfX_test is not None and dfy_test is not None:

        fitted_preprocessor = pipeline['preprocess'].fit(dfX_train, dfy_train)
        dfX_test_trans = fitted_preprocessor.transform(dfX_test)
        fit_params = {'regressor__eval_set':[(dfX_test_trans, dfy_test)],
                      'regressor__verbose':True
                     }
    else:
        fit_params = {}

    model = pipeline.fit(dfX_train, dfy_train, **fit_params)

    return model


def TrainRegressor(pipeline, dfX_train, dfy_train, dfX_test=None, dfy_test=None, regressor_args={}):

    """
    Dedicate train function for regression pipelines

    """

    from sklearn.pipeline import Pipeline

    algo = str(pipeline.named_steps['regressor']).split('(')[0]

    if algo != 'XGBRegressor':

        model = pipeline.fit(dfX_train, dfy_train)

    else:

        if 'early_stopping_rounds' in regressor_args.keys() and dfX_test is not None and dfy_test is not None:

            fitted_preprocessor = pipeline['preprocess'].fit(dfX_train, dfy_train)
            dfX_test_trans = fitted_preprocessor.transform(dfX_test)
            fit_params = {'regressor__eval_set':[(dfX_test_trans, dfy_test)],
                          'regressor__verbose':True
                         }
        else:
            fit_params = {}

        model = pipeline.fit(dfX_train, dfy_train, **fit_params)

    return model


def RegressionGridSearchCV(pipeline,
                           dfX_train, dfy_train,
                           dfX_test=None, dfy_test=None,
                           cv=4,
                           scoring='neg_root_mean_squared_error',
                           regressor_grid_args={}):
    
 
    '''
    Performs a grid search to train the pipeline 
    scoring: 'neg_root_mean_squared_error', 'neg_mean_absolute_error', ...

    input: pipeline, pipeline to be trained using grid search
           dfX_train, dfy_train are dataframes
           dfX_test, dfy_test are only needed for xgb pipelines, dataframes
           scoring = 'neg_root_mean_squared_error' or 'neg_mean_absolute_error'

    output: trained regressor pipeline
    
    '''

    import pandas as pd  
    from sklearn.model_selection import GridSearchCV
    
    
    algo = str(pipeline.named_steps['regressor']).split('(')[0]
    
    if algo == 'RandomForestRegressor':
        
        print('Grid search with RandomForestRegressor')
        
        if not regressor_grid_args:
            pipeline_params = {
                           'preprocess__num__imputer__strategy':['mean','median'],
                           'regressor__n_estimators':[100],
                           'regressor__min_samples_leaf':[1,2,3]
                     }
        else:
            pipeline_params = {
                           'preprocess__num__imputer__strategy':['mean'],
            }
            for k,v in regressor_grid_args.items():
                           pipeline_params['regressor__' + k] = v             
        fit_params = {         
                     }

    elif algo == 'XGBRegressor':
        
        print('Grid search with XGBRegressor')
        
        if not regressor_grid_args:
            pipeline_params = {
                           'regressor__n_estimators':[100],
                           'regressor__min_child_weight':[1,1.5,2],
                           'regressor__learning_rate':[0.3,0.1,0.03],
                           'regressor__max_depth':[5,6],
                           'regressor__use_label_encoder':[False],
                         }
        else:
            pipeline_params = {
                           'preprocess__num__imputer__strategy':['mean'],
            }

            for k,v in regressor_grid_args.items():
                           pipeline_params['regressor__' + k] = v   
            
        fit_params = {         
        #              'classifier__early_stopping_rounds':10,
        #              'classifier__eval_metric':['logloss'],
        #              'classifier__eval_set':[[X_test, y_test]]
                     }
    elif algo == 'Ridge':
        
        print('Grid search with Ridge')
        
        if not regressor_grid_args:
            pipeline_params = {
                           'regressor__alpha':[0.01, 0.1, 1, 10, 100],
                          }
        else:
            pipeline_params = {
                           
            }
            
            for k,v in regressor_grid_args.items():
                           pipeline_params['regressor__' + k] = v   
        fit_params = {
                     }
    elif algo == 'Lasso':
        
        print('Grid search with Lasso')
        
        if not regressor_grid_args:
            pipeline_params = {
                           'regressor__alpha':[0.01, 0.1, 1, 10, 100],
                          }
        else:
            pipeline_params = {
                           
            }
            
            for k,v in regressor_grid_args.items():
                           pipeline_params['regressor__' + k] = v  
        fit_params = {
                     }

    elif algo == 'KerasRegressor':

        print('Grid search with KerasRegressor')
        
        if not regressor_grid_args:
            
            param_grid = {'regressor__model__n_in':[dfX_train.shape[1]],
                          'regressor__model__hidden_layers_sizes':[(1000,),(500,500,),(333,334,333,)],
                          'regressor__optimizer__learning_rate':[0.003,0.01],
                          'regressor__batch_size':[100,1000],
                          'regressor__epochs':[200]
                         }

        else:

            param_grid = {'regressor__model__n_in':[dfX_train.shape[1]]
                         }

            for k,v in regressor_grid_args.items():
                if k in ('hidden_layers_sizes','dropout'):
                    param_grid['regressor__model__' + k] = v
                elif k in ('learning_rate'):
                    param_grid['regressor__optimizer__' + k] = v
                else:
                    param_grid['regressor__' + k] = v
        
    
    if algo != 'KerasRegressor':
        
        grid = GridSearchCV(estimator=pipeline, 
                            param_grid=pipeline_params, 
                            cv=cv,
                            scoring=scoring, 
                            refit=True,
                            verbose=1,
                            n_jobs=1)
    else:

        ####pipeline = CreateClassificationPipeline(dfX_train, max_low_cardinality=0, max_high_cardinality=100000, algo='neuralnet')  
        grid = GridSearchCV(pipeline, param_grid=param_grid, scoring='neg_mean_squared_error')

    import time
    start = time.time()
    trained_regressor = grid.fit(dfX_train, dfy_train) #, **fit_params)
    print("Running time =", time.time() - start, "seconds")

    df_grid_search = _ExtractGridSearchData(grid.cv_results_, regressor_grid_args, 'regression')
        
    return trained_regressor
    


def EvaluateClassifier(model, dfX_test, dfy_test):

    '''
    Computes auc, average precision, accuracy, precision, recall, f1-score
    f1-optimal decision threshold, and accuracy, precision and recall based on
    the f1-optimal decision threshold.
    Returns data for: roc curve, precision-recall curve, f1 v threshold curve, confusion matrix.
    and histogram of predictions.
    
    '''
    
    from sklearn.metrics import confusion_matrix, \
                                precision_score, recall_score, accuracy_score, f1_score, \
                                roc_auc_score, average_precision_score, precision_recall_curve, roc_curve
    
    import pandas as pd
    import numpy as np

    import matplotlib.pyplot as plt
    import seaborn as sns

    y_pred = model.predict_proba(dfX_test)
    auc_score_ = np.round(roc_auc_score(dfy_test, y_pred[:,1]),4)
    average_precision_score_ = np.round(average_precision_score(dfy_test, y_pred[:,1]),4)

    p, r, t = precision_recall_curve(dfy_test, y_pred[:,1])

    p_ratio = dfy_test.mean()
    noskill = p_ratio * np.ones(len(t))

    if PLOTS:
        fig = plt.figure(figsize=(5,5))
        plt.title('Precision-recall curve')
        plt.plot(r,p)
        plt.hlines(p_ratio,0,1,colors='r', linestyles='--', label='no-skill classifier')
        plt.xlim([0,1])
        plt.ylim([0,1])
        plt.ylabel('Precision')
        plt.xlabel('Recall')
        plt.legend()
        plt.show()
    
    df_precision_recall = pd.DataFrame(np.concatenate([t.reshape(-1,1),p[:-1].reshape(-1,1),r[:-1].reshape(-1,1), noskill.reshape(-1,1)], axis=1), 
                                       columns=['threshold','precision','recall','noskill'])

    fpr, tpr, thr = roc_curve(dfy_test, y_pred[:,1])

    if PLOTS:
        fig = plt.figure(figsize=(5,5))
        plt.title('ROC curve')
        plt.plot(fpr, tpr)
        plt.plot([0,1],[0,1], 'r--', label='no-skill classifier')
        plt.xlim([0,1])
        plt.ylim([0,1])
        plt.xlabel('False Positive Rate')
        plt.ylabel('True Positive Rate')
        plt.legend()
        plt.show()
    
    df_roc = pd.DataFrame(np.concatenate([thr.reshape(-1,1), fpr.reshape(-1,1), tpr.reshape(-1,1), fpr.reshape(-1,1)], axis=1), columns=['threshold','fpr','tpr','noskill'])

    y_pred = model.predict(dfX_test)
    precision_score_ = np.round(precision_score(dfy_test, y_pred),4)
    recall_score_ = np.round(recall_score(dfy_test, y_pred),4)
    f1_score_ = np.round(f1_score(dfy_test, y_pred),4)
    accuracy_score_ = np.round(accuracy_score(dfy_test, y_pred),4)

    # compute f1-optimal threshold
    y_pred = model.predict_proba(dfX_test)[:,1]
    df_y_pred = pd.DataFrame(y_pred.reshape(-1,1),columns=['prediction']).astype(float)
    p, r, t = precision_recall_curve(dfy_test, y_pred)
    f1 = np.array([2*x*y/(x+y) for x,y in zip(p,r)])
    f1_optimal_threshold_ = t[np.argmax(f1)]

    if PLOTS:
        fig = plt.figure(figsize=(5,5))
        plt.title('Histogram of y_pred')
        sns.histplot(y_pred, bins=20, edgecolor=None)
        plt.show()

    y_pred[y_pred > f1_optimal_threshold_] = 1
    y_pred[y_pred != 1] = 0

    df_f1_threshold = pd.DataFrame(np.concatenate([t.reshape(-1,1), f1[:-1].reshape(-1,1)], axis=1), columns=['threshold','f1'])
    cm = confusion_matrix(dfy_test.values.reshape(-1,1), y_pred)
    df_confusion_matrix = pd.DataFrame(np.concatenate([np.array(['actual 0','actual 1']).reshape(-1,1), cm], axis=1),
                                       columns=['class', 'predicted 0','predicted 1'])

    if PLOTS:
        fig = plt.figure(figsize=(5,5))
        plt.title('decision-threshold dependence of f1-score')
        plt.plot(t, f1[:-1])
        plt.xlabel('decision-threshold')
        plt.ylabel('f1-score')
        plt.show()
    
    f1_opt_precision_score_ = np.round(precision_score(dfy_test, y_pred),4)
    f1_opt_recall_score_ = np.round(recall_score(dfy_test, y_pred),4)
    f1_opt_f1_score_ = np.round(f1_score(dfy_test, y_pred),4)
    f1_opt_accuracy_score_ = np.round(accuracy_score(dfy_test, y_pred),4)
    
    scores_dict = {}
    scores_dict['auc'] = auc_score_
    scores_dict['average precision'] = average_precision_score_
    scores_dict['precision'] = precision_score_
    scores_dict['recall'] = recall_score_
    scores_dict['accuracy'] = accuracy_score_
    scores_dict['f1'] = f1_score_
    scores_dict['f1-optimal threshold'] = f1_optimal_threshold_
    scores_dict['f1-optimal f1'] = f1_opt_f1_score_
    scores_dict['f1-optimal precision'] = f1_opt_precision_score_
    scores_dict['f1-optimal recall'] = f1_opt_recall_score_
    scores_dict['f1-optimal accuracy'] = f1_opt_accuracy_score_

    df_scores = pd.DataFrame.from_dict(scores_dict, orient='index').reset_index()
    df_scores.columns = ['metric', 'value']
      
    return df_precision_recall, df_roc, df_f1_threshold, df_y_pred, df_confusion_matrix, df_scores


def EvaluateRegressor(model, dfX_test, dfy_test):
    
    '''
    Computes root mean squared error, mean absolute error, explained variance, r-squared,
    and maximum error.

    '''
    
    import numpy as np
    import pandas as pd
    
    from sklearn.metrics import mean_squared_error, mean_absolute_error, \
                                explained_variance_score, r2_score, max_error
    import matplotlib.pyplot as plt
    
    y_pred = model.predict(dfX_test)
    rmse = np.round(mean_squared_error(dfy_test, y_pred, squared=False),4)
    mae = np.round(mean_absolute_error(dfy_test, y_pred),4)
    ev = np.round(explained_variance_score(dfy_test, y_pred),4)
    r2 = np.round(r2_score(dfy_test, y_pred),4)
    me = np.round(max_error(dfy_test, y_pred),4)
    #print('RMSE    = ', rmse)
    
    x_min = min(min(dfy_test),min(y_pred))
    x_max = max(max(dfy_test),max(y_pred))

    # regression evaluation plot and saving the data
    if PLOTS:
        fig = plt.figure(figsize=(8,8))
        plt.scatter(dfy_test, y_pred)
        plt.plot([x_min,x_max],[x_min,x_max], 'r--')
        plt.title('Regression-evaluation plot\nRMSE = ' + str(rmse))
        plt.ylabel('Predicted')
        plt.xlabel('Actual')
        plt.xlim([x_min,x_max])
        plt.ylim([x_min,x_max])
        plt.show()

    data = np.concatenate([dfy_test.values.reshape(-1,1),y_pred.reshape(-1,1)], axis=1)
    df_regression_evaluation = pd.DataFrame(data, columns=['Actual','Predicted'])

    scores_dict = {}
    scores_dict['root mean squared error'] = rmse
    scores_dict['mean absolute error'] = mae
    scores_dict['explained variance'] = ev
    scores_dict['r-squared'] = r2
    scores_dict['max error'] = me

    df_scores = pd.DataFrame.from_dict(scores_dict, orient='index').reset_index()
    df_scores.columns = ['metric', 'value']

    return df_regression_evaluation, df_scores


def ComputeFeatureImportances(estimator, dfX_test, dfy_test, scoring=None):
    
    ''' Computes permutation importances for the estimator using dfX_test and dfy_test
        Computation of the importances is based on the scoring method (default None)
        that is supplied. When the default is used, the estimator's default is used.
        For classifiers that is 'accuracy', for regressors that is 'r2_score'.
    '''
    
    import pandas as pd
    import numpy as np
    from sklearn.inspection import permutation_importance
    
    result = permutation_importance(estimator, dfX_test, dfy_test,
                                    scoring=scoring,
                                    n_repeats=5, random_state=59,
                                    n_jobs=1)
    result.importances_mean[result.importances_mean < 0] = 0

    normalized_importances = np.array(result.importances_mean / np.max(result.importances_mean))
    features = np.array(dfX_test.columns)

    df_importances = pd.DataFrame(np.concatenate([features.reshape(-1,1), normalized_importances.reshape(-1,1)], axis=1),
                                  columns=['feature', 'importance']).sort_values(by='importance', ascending=False)
    df_importances['order'] = np.arange(1, 1+len(features))

    if PLOTS:

        import seaborn as sns
        import matplotlib.pyplot as plt
        
        sns.barplot(x='importance', y='feature',   
                    data=df_importances, 
                    color='red')
        plt.show()

    return df_importances


def ComputeLearningCurve(pipeline, dfX, dfy, mode):

    from sklearn.model_selection import train_test_split
    from sklearn.metrics import roc_auc_score, mean_squared_error
    import pandas as pd

    scores = []
    fractions = (0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9)

    for train_size in fractions:

        if mode == 'classification':
            dfX_train, dfX_test, dfy_train, dfy_test = train_test_split(dfX, dfy, stratify=dfy, train_size=train_size, random_state = 59)
        else:
            dfX_train, dfX_test, dfy_train, dfy_test = train_test_split(dfX, dfy, train_size=train_size, random_state = 59)

        model = pipeline.fit(dfX_train, dfy_train)

        if mode == 'classification':
            scores.append(roc_auc_score(dfy_test, model.predict_proba(dfX_test)[:,1]))
        else:
            scores.append(mean_squared_error(dfy_test, model.predict(dfX_test), squared=False))

    df_learning_curve = pd.DataFrame({'fraction':fractions, 'score':scores})

    print(df_learning_curve)

    if PLOTS:

        import matplotlib.pyplot as plt

        fig = plt.figure(figsize=(5,5))
        plt.plot(df_learning_curve['fraction'].values, df_learning_curve['score'])
        plt.title('Learning curve')
        plt.ylabel('Test score')
        plt.xlabel('Fraction of data used for training')
        plt.show()     
            
    return df_learning_curve


def SaveModel(model, modelname=''):

    import cloudpickle

    with open(modelname, 'wb') as fw:
        cloudpickle.dump(model, fw)

    return


def LoadModel(modelname):

    import cloudpickle

    with open(modelname, 'rb') as fr:
        model = cloudpickle.load(fr)

    return model


# ===================================================================================
# EXAMPLE OF HOW TO USE THE FUNCTIONS DEFINED IN THIS SOURCE (simply run the source!)
# ===================================================================================

if __name__ == "__main__":

    import pandas as pd
    from sklearn.model_selection import train_test_split

    PLOTS = False

    import warnings
    warnings.filterwarnings('ignore')

    # =============================
    # BINARY CLASSIFICATION EXAMPLE
    # =============================

    import sklearn
    print('scikit-learn      :', sklearn.__version__)
    print('pandas            :', pd.__version__)
    import xgboost
    print('xgboost           :', xgboost.__version__)
    import numpy as np
    print('numpy             :', np.__version__)
    import category_encoders as ce
    print('category_encoders :', ce.__version__)
    import tensorflow as tf
    print('tensorflow        :', tf.__version__)
    import scikeras
    print('scikeras          :', scikeras.__version__)


    df = pd.read_csv('C:\\Users\\mhorbach\\Datasets\\bankchurners12mar.csv')
    target = 'Attrition_Flag'
      
    dfX = df.drop([target,'CLIENTNUM','Gender'], axis=1)
    dfy = df[target]

    # For now, we require 0/1 labels in the functions, pos_label is set to 1
    dfy_aux = dfy.copy()
    dfy_aux[dfy=='Existing Customer'] = 0
    dfy_aux[dfy=='Attrited Customer'] = 1
    dfy = dfy_aux.astype(int)

    dfX_train, dfX_test, dfy_train, dfy_test = train_test_split(dfX, dfy, stratify=dfy, random_state=59)
   
    MAX_LOW_CARDINALITY = 4
    MAX_HIGH_CARDINALITY = 50


    # define the pipeline . . .
    print('\nXGBOOST:\n')
    classifier_args = {'n_estimators':1000, 'early_stopping_rounds':10,'n_jobs':1}
    pipeline = CreateClassificationPipeline(dfX_train, 
                                            max_low_cardinality=MAX_LOW_CARDINALITY, 
                                            max_high_cardinality=MAX_HIGH_CARDINALITY,
                                            algo='xgboost',
                                            classifier_args=classifier_args)



    # . . . and train it the simple way, and evaluate the result
    print('\nSIMPLE TRAINING WITH EARLY STOPPING...\n')
    model11 = TrainXGBClassifier(pipeline, dfX_train, dfy_train, dfX_test=dfX_test, dfy_test=dfy_test, classifier_args=classifier_args)
    print(model11.named_steps)
    df_precision_recall, df_roc, df_f1_threshold, df_y_pred, df_confusion_matrix, df_scores = EvaluateClassifier(model11, dfX_test, dfy_test)
    df_importances = ComputeFeatureImportances(model11, dfX_test, dfy_test)
    print('\nEVALUATION SCORES:\n')
    print(df_scores)

    # ==================
    # SAVE AND LOAD MODEL
    # ===================

    import cloudpickle
    with open('C:\\Users\\mhorbach\\Desktop\\XGB_saved_model.pkl','wb') as fw:
        cloudpickle.dump(model11,fw)
    with open('C:\\Users\\mhorbach\\Desktop\\XGB_saved_model.pkl','rb') as fr:
        loaded_model = cloudpickle.load(fr)

    y_pred = loaded_model.predict_proba(dfX_train)

    print('First 24 predictions:')
    print(y_pred[:24,1])

    # redo evaluation
    df_precision_recall, df_roc, df_f1_threshold, df_y_pred, df_confusion_matrix, df_scores = EvaluateClassifier(loaded_model, dfX_test, dfy_test)
    df_importances = ComputeFeatureImportances(loaded_model, dfX_test, dfy_test)
    print('\nEVALUATION SCORES:\n')
    print(df_scores)


    # ==================
    # SAVE AND LOAD MODEL
    # ===================

    SaveModel(model11,'C:\\Users\\mhorbach\\Desktop\\XGB_saved_model_SaveModel.pkl')
    loaded_model_2 = LoadModel('C:\\Users\\mhorbach\\Desktop\\XGB_saved_model_SaveModel.pkl')
    
    y_pred = loaded_model_2.predict_proba(dfX_train)

    print('First 24 predictions:')
    print(y_pred[:24,1])

    # redo evaluation
    df_precision_recall, df_roc, df_f1_threshold, df_y_pred, df_confusion_matrix, df_scores = EvaluateClassifier(loaded_model, dfX_test, dfy_test)
    df_importances = ComputeFeatureImportances(loaded_model, dfX_test, dfy_test)
    print('\nEVALUATION SCORES:\n')
    print(df_scores)

    input('WAITING')
    
    
    # ==================
    # REGRESSION EXAMPLE
    # ==================

    df = pd.read_csv('C:\\Users\\mhorbach\\Datasets\\ENB2012.csv')
    target = 'Cooling Load'

    df = df.dropna(subset=[target])
    dfX = df.drop([target, 'Heating Load'], axis=1)
    dfy = df[target]
    

    dfX_train, dfX_test, dfy_train, dfy_test = train_test_split(dfX, dfy, random_state=59)
   
    MAX_LOW_CARDINALITY = 4
    MAX_HIGH_CARDINALITY = 50

    # define the pipeline . . .
    print('\nXGB REGRESSION WITH EARLY STOPPING:\n')
    regressor_args = {'n_estimators':1000, 'early_stopping_rounds':10}
    pipeline = CreateRegressionPipeline(dfX_train, 
                                        max_low_cardinality=MAX_LOW_CARDINALITY, 
                                        max_high_cardinality=MAX_HIGH_CARDINALITY,
                                        algo='xgboost',
                                        regressor_args=regressor_args)

    
    print('\nSIMPLE TRAINING...\n')
    model12 = TrainXGBRegressor(pipeline, dfX_train, dfy_train, dfX_test=dfX_test, dfy_test=dfy_test, regressor_args=regressor_args)
    df_evaluation, scores = EvaluateRegressor(model12, dfX_test, dfy_test)
    df_importances = ComputeFeatureImportances(model12, dfX_test, dfy_test)
    print('\nFEATURE IMPORTANCES:\n')
    print(df_importances)


    # =============================
    # BINARY CLASSIFICATION EXAMPLE
    # =============================

    import sklearn
    print('scikit-learn      :', sklearn.__version__)
    print('pandas            :', pd.__version__)
    import xgboost
    print('xgboost           :', xgboost.__version__)
    import numpy as np
    print('numpy             :', np.__version__)
    import category_encoders as ce
    print('category_encoders :', ce.__version__)
    import tensorflow as tf
    print('tensorflow        :', tf.__version__)
    import scikeras
    print('scikeras          :', scikeras.__version__)


    df = pd.read_csv('C:\\Users\\mhorbach\\Datasets\\bankchurners12mar.csv')
    target = 'Attrition_Flag'
      
    dfX = df.drop(target, axis=1)
    dfy = df[target]

    # For now, we require 0/1 labels in the functions, pos_label is set to 1
    dfy_aux = dfy.copy()
    dfy_aux[dfy=='Existing Customer'] = 0
    dfy_aux[dfy=='Attrited Customer'] = 1
    dfy = dfy_aux.astype(int)

    dfX_train, dfX_test, dfy_train, dfy_test = train_test_split(dfX, dfy, stratify=dfy, random_state=59)
   
    MAX_LOW_CARDINALITY = 4
    MAX_HIGH_CARDINALITY = 50


    # define the pipeline . . .
    print('\nXGBOOST:\n')
    classifier_args = {'n_estimators':1000, 'early_stopping_rounds':10,'n_jobs':1}
    pipeline = CreateClassificationPipeline(dfX_train, 
                                            max_low_cardinality=MAX_LOW_CARDINALITY, 
                                            max_high_cardinality=MAX_HIGH_CARDINALITY,
                                            algo='xgboost',
                                            classifier_args=classifier_args)



    # . . . and train it the simple way, and evaluate the result
    print('\nSIMPLE TRAINING WITH EARLY STOPPING...\n')
    model11 = TrainClassifier(pipeline, dfX_train, dfy_train, dfX_test=dfX_test, dfy_test=dfy_test, classifier_args=classifier_args)
    print(model11.named_steps)
    df_precision_recall, df_roc, df_f1_threshold, df_y_pred, df_confusion_matrix, df_scores = EvaluateClassifier(model11, dfX_test, dfy_test)
    df_importances = ComputeFeatureImportances(model11, dfX_test, dfy_test)
    print('\nEVALUATION SCORES:\n')
    print(df_scores)
    
    # ==================
    # REGRESSION EXAMPLE
    # ==================

    df = pd.read_csv('C:\\Users\\mhorbach\\Datasets\\ENB2012.csv')
    target = 'Cooling Load'

    df = df.dropna(subset=[target])
    dfX = df.drop([target, 'Heating Load'], axis=1)
    dfy = df[target]
    

    dfX_train, dfX_test, dfy_train, dfy_test = train_test_split(dfX, dfy, random_state=59)
   
    MAX_LOW_CARDINALITY = 4
    MAX_HIGH_CARDINALITY = 50

    # define the pipeline . . .
    print('\nXGB REGRESSION WITH EARLY STOPPING:\n')
    regressor_args = {'n_estimators':1000, 'early_stopping_rounds':10}
    pipeline = CreateRegressionPipeline(dfX_train, 
                                        max_low_cardinality=MAX_LOW_CARDINALITY, 
                                        max_high_cardinality=MAX_HIGH_CARDINALITY,
                                        algo='xgboost',
                                        regressor_args=regressor_args)

    
    print('\nSIMPLE TRAINING...\n')
    model12 = TrainRegressor(pipeline, dfX_train, dfy_train, dfX_test=dfX_test, dfy_test=dfy_test, regressor_args=regressor_args)
    df_evaluation, scores = EvaluateRegressor(model12, dfX_test, dfy_test)
    df_importances = ComputeFeatureImportances(model12, dfX_test, dfy_test)
    print('\nFEATURE IMPORTANCES:\n')
    print(df_importances)


    # =============================
    # BINARY CLASSIFICATION EXAMPLE
    # =============================

    import sklearn
    print('scikit-learn      :', sklearn.__version__)
    print('pandas            :', pd.__version__)
    import xgboost
    print('xgboost           :', xgboost.__version__)
    import numpy as np
    print('numpy             :', np.__version__)
    import category_encoders as ce
    print('category_encoders :', ce.__version__)
    import tensorflow as tf
    print('tensorflow        :', tf.__version__)
    import scikeras
    print('scikeras          :', scikeras.__version__)


    df = pd.read_csv('C:\\Users\\mhorbach\\Datasets\\bankchurners12mar.csv')
    target = 'Attrition_Flag'
      
    dfX = df.drop(target, axis=1)
    dfy = df[target]

    # For now, we require 0/1 labels in the functions, pos_label is set to 1
    dfy_aux = dfy.copy()
    dfy_aux[dfy=='Existing Customer'] = 0
    dfy_aux[dfy=='Attrited Customer'] = 1
    dfy = dfy_aux.astype(int)

    dfX_train, dfX_test, dfy_train, dfy_test = train_test_split(dfX, dfy, stratify=dfy, random_state=59)
   
    MAX_LOW_CARDINALITY = 4
    MAX_HIGH_CARDINALITY = 50


    # define the pipeline . . .
    print('\nXGBOOST:\n')
    classifier_args = {'n_jobs':1}
    pipeline = CreateClassificationPipeline(dfX_train, 
                                            max_low_cardinality=MAX_LOW_CARDINALITY, 
                                            max_high_cardinality=MAX_HIGH_CARDINALITY,
                                            algo='randomforest',
                                            classifier_args=classifier_args)



    # . . . and train it the simple way, and evaluate the result
    print('\nSIMPLE TRAINING WITH EARLY STOPPING...\n')
    model11 = TrainClassifier(pipeline, dfX_train, dfy_train, dfX_test=dfX_test, dfy_test=dfy_test, classifier_args=classifier_args)
    print(model11.named_steps)
    df_precision_recall, df_roc, df_f1_threshold, df_y_pred, df_confusion_matrix, df_scores = EvaluateClassifier(model11, dfX_test, dfy_test)
    df_importances = ComputeFeatureImportances(model11, dfX_test, dfy_test)
    print('\nEVALUATION SCORES:\n')
    print(df_scores)
    
    # ==================
    # REGRESSION EXAMPLE
    # ==================

    df = pd.read_csv('C:\\Users\\mhorbach\\Datasets\\ENB2012.csv')
    target = 'Cooling Load'

    df = df.dropna(subset=[target])
    dfX = df.drop([target, 'Heating Load'], axis=1)
    dfy = df[target]
    

    dfX_train, dfX_test, dfy_train, dfy_test = train_test_split(dfX, dfy, random_state=59)
   
    MAX_LOW_CARDINALITY = 4
    MAX_HIGH_CARDINALITY = 50

    # define the pipeline . . .
    print('\nXGB REGRESSION WITH EARLY STOPPING:\n')
    regressor_args = {}
    pipeline = CreateRegressionPipeline(dfX_train, 
                                        max_low_cardinality=MAX_LOW_CARDINALITY, 
                                        max_high_cardinality=MAX_HIGH_CARDINALITY,
                                        algo='randomforest',
                                        regressor_args=regressor_args)

    
    print('\nSIMPLE TRAINING...\n')
    model12 = TrainRegressor(pipeline, dfX_train, dfy_train, dfX_test=dfX_test, dfy_test=dfy_test, regressor_args=regressor_args)
    df_evaluation, scores = EvaluateRegressor(model12, dfX_test, dfy_test)
    df_importances = ComputeFeatureImportances(model12, dfX_test, dfy_test)
    print('\nFEATURE IMPORTANCES:\n')
    print(df_importances)


    input('WAITTTTTTTTTTTTTTTTTTTTTTTTTTTTT')




    # ============================================================
    # BINARY CLASSIFICATION EXAMPLE WITH NEURAL NET + GRIDSEARCHCV
    # ============================================================

    df = pd.read_csv('C:\\Users\\mhorbach\\Datasets\\creditcard.csv')
    target = 'Class'
      
    dfX = df.drop(target, axis=1)
    dfy = df[target]

    # For now, we require 0/1 labels in the functions, pos_label is set to 1
    dfy_aux = dfy.copy()
    #dfy_aux[dfy=='Existing Customer'] = 0
    #dfy_aux[dfy=='Attrited Customer'] = 1
    dfy = dfy_aux.astype(int)

    dfX_train, dfX_test, dfy_train, dfy_test = train_test_split(dfX, dfy, stratify=dfy, random_state=59)
   
    MAX_LOW_CARDINALITY = 4
    MAX_HIGH_CARDINALITY = 50

    # define the pipeline . . . 
    print('\nNEURAL NET:\n')
    pipeline = CreateClassificationPipeline(dfX_train, 
                                            max_low_cardinality=MAX_LOW_CARDINALITY, 
                                            max_high_cardinality=MAX_HIGH_CARDINALITY,
                                            algo='neuralnet',
                                            ) 

    model2 = ClassificationGridSearchCV(pipeline, dfX_train, dfy_train, dfX_test, dfy_test, scoring='roc_auc',
                                        classifier_grid_args={'batch_size':[100],'hidden_layers_sizes':[(50,50,),(25,25,)],
                                                                     'dropout':[0.0],'learning_rate':[0.001]})

    df_precision_recall, df_roc, df_f1_threshold, df_y_pred, df_confusion_matrix, df_scores = EvaluateClassifier(model2, dfX_test, dfy_test)
 
    
  
    # define the pipeline . . .
    print('\nRANDOM FOREST:\n')
    pipeline = CreateClassificationPipeline(dfX_train, 
                                            max_low_cardinality=MAX_LOW_CARDINALITY, 
                                            max_high_cardinality=MAX_HIGH_CARDINALITY,
                                            algo='randomforest',
                                            classifier_args={'n_estimators':5,'min_samples_leaf':2,'n_jobs':1})


    df_learning_curve = ComputeLearningCurve(pipeline, dfX, dfy, 'classification')

    # . . . and train it the simple way, and evaluate the result
    print('\nSIMPLE TRAINING...\n')
    model1 = pipeline.fit(dfX_train, dfy_train)
    print(model1.named_steps)
    df_precision_recall, df_roc, df_f1_threshold, df_y_pred, df_confusion_matrix, df_scores = EvaluateClassifier(model1, dfX_test, dfy_test)
    df_importances = ComputeFeatureImportances(model1, dfX_test, dfy_test)
    print('\nEVALUATION SCORES:\n')
    print(df_scores)
    print('\nTOP OF PRECISION-RECALL CURVE DATA:\n')
    print(df_precision_recall.head(12))
    print('\nTOP OF ROC CURVE DATA:\n')
    print(df_roc.head(12))
    print('\nFEATURE IMPORTANCES:\n')
    print(df_importances)
    print(model1.named_steps)
    
    # . . . or train it using a grid search, and evaluate the result
    print('\nGRID SEARCH...\n')
    model2 = ClassificationGridSearchCV(pipeline, dfX_train, dfy_train, dfX_test, dfy_test, scoring='roc_auc')
    df_precision_recall, df_roc, df_f1_threshold, df_y_pred, df_confusion_matrix, df_scores = EvaluateClassifier(model2, dfX_test, dfy_test)
    df_importances = ComputeFeatureImportances(model2, dfX_test, dfy_test)
    print('\nEVALUATION SCORES:\n')
    print(df_scores)
    print('\nTOP OF PRECISION-RECALL CURVE DATA:\n')
    print(df_precision_recall.head(12))
    print('\nTOP OF ROC CURVE DATA:\n')
    print(df_roc.head(12))
    print('\nFEATURE IMPORTANCES:\n')
    print(df_importances)

    # . . . or train it using a grid search, and evaluate the result
    print('\nGRID SEARCH WITH USER-SPECIFIED GRID...\n')
    model3 = ClassificationGridSearchCV(pipeline, dfX_train, dfy_train, dfX_test, dfy_test, scoring='roc_auc',
                                        classifier_grid_args={'n_estimators':[20,40,60,80,100],'min_samples_leaf':[1,2,3,4,5],'n_jobs':[1]})
    df_precision_recall, df_roc, df_f1_threshold, df_y_pred, df_confusion_matrix, df_scores = EvaluateClassifier(model3, dfX_test, dfy_test)
    df_importances = ComputeFeatureImportances(model3, dfX_test, dfy_test)
    print('\nEVALUATION SCORES:\n')
    print(df_scores)
    print('\nTOP OF PRECISION-RECALL CURVE DATA:\n')
    print(df_precision_recall.head(12))
    print('\nTOP OF ROC CURVE DATA:\n')
    print(df_roc.head(12))
    print('\nFEATURE IMPORTANCES:\n')
    print(df_importances)

    print('\nXGBOOST:\n')
    # define the pipeline . . .
    pipeline = CreateClassificationPipeline(dfX_train, 
                                            max_low_cardinality=MAX_LOW_CARDINALITY, 
                                            max_high_cardinality=MAX_HIGH_CARDINALITY,
                                            algo='xgboost',
                                            classifier_args={'n_estimators':5,'eval_metric':'nonsense','n_jobs':1})

    # . . . and train it the simple way, and evaluate the result
    print('\nSIMPLE TRAINING...\n')
    model1 = pipeline.fit(dfX_train, dfy_train)
    print(model1.named_steps)
    df_precision_recall, df_roc, df_f1_threshold, df_y_pred, df_confusion_matrix, df_scores = EvaluateClassifier(model1, dfX_test, dfy_test)
    df_importances = ComputeFeatureImportances(model1, dfX_test, dfy_test)
    print('\nEVALUATION SCORES:\n')
    print(df_scores)
    print('\nTOP OF PRECISION-RECALL CURVE DATA:\n')
    print(df_precision_recall.head(12))
    print('\nTOP OF ROC CURVE DATA:\n')
    print(df_roc.head(12))
    print('\nFEATURE IMPORTANCES:\n')
    print(df_importances)
    print(model1.named_steps)

    # . . . or train it using a grid search, and evaluate the result
    print('\nGRID SEARCH...\n')
    model2 = ClassificationGridSearchCV(pipeline, dfX_train, dfy_train, dfX_test, dfy_test, scoring='roc_auc')
    df_precision_recall, df_roc, df_f1_threshold, df_y_pred, df_confusion_matrix, df_scores = EvaluateClassifier(model2, dfX_test, dfy_test)
    df_importances = ComputeFeatureImportances(model2, dfX_test, dfy_test)
    print('\nEVALUATION SCORES:\n')
    print(df_scores)
    print('\nTOP OF PRECISION-RECALL CURVE DATA:\n')
    print(df_precision_recall.head(12))
    print('\nTOP OF ROC CURVE DATA:\n')
    print(df_roc.head(12))
    print('\nFEATURE IMPORTANCES:\n')
    print(df_importances)

    # . . . or train it using a grid search, and evaluate the result
    print('\nGRID SEARCH WITH USER-SPECIFIED GRID...\n')
    model3 = ClassificationGridSearchCV(pipeline, dfX_train, dfy_train, dfX_test, dfy_test, scoring='roc_auc',
                                        classifier_grid_args={'n_estimators':[2,100,400]})
    df_precision_recall, df_roc, df_f1_threshold, df_y_pred, df_confusion_matrix, df_scores = EvaluateClassifier(model3, dfX_test, dfy_test)
    df_importances = ComputeFeatureImportances(model3, dfX_test, dfy_test)
    print('\nEVALUATION SCORES:\n')
    print(df_scores)
    print('\nTOP OF PRECISION-RECALL CURVE DATA:\n')
    print(df_precision_recall.head(12))
    print('\nTOP OF ROC CURVE DATA:\n')
    print(df_roc.head(12))
    print('\nFEATURE IMPORTANCES:\n')
    print(df_importances)

    print('\nLOGISTIC REGRESSION:\n')
    # define the pipeline . . .
    pipeline = CreateClassificationPipeline(dfX_train, 
                                            max_low_cardinality=MAX_LOW_CARDINALITY, 
                                            max_high_cardinality=MAX_HIGH_CARDINALITY,
                                            algo='logisticregression',
                                            classifier_args={'C':1,'n_jobs':1})

    # . . . and train it the simple way, and evaluate the result
    print('\nSIMPLE TRAINING...\n')
    model1 = pipeline.fit(dfX_train, dfy_train)
    print(model1.named_steps)
    df_precision_recall, df_roc, df_f1_threshold, df_y_pred, df_confusion_matrix, df_scores = EvaluateClassifier(model1, dfX_test, dfy_test)
    df_importances = ComputeFeatureImportances(model1, dfX_test, dfy_test)
    print('\nEVALUATION SCORES:\n')
    print(df_scores)
    print('\nTOP OF PRECISION-RECALL CURVE DATA:\n')
    print(df_precision_recall.head(12))
    print('\nTOP OF ROC CURVE DATA:\n')
    print(df_roc.head(12))
    print('\nFEATURE IMPORTANCES:\n')
    print(df_importances)
    print(model1.named_steps)

    # . . . or train it using a grid search, and evaluate the result
    print('\nGRID SEARCH...\n')
    model2 = ClassificationGridSearchCV(pipeline, dfX_train, dfy_train, dfX_test, dfy_test, scoring='roc_auc')
    df_precision_recall, df_roc, df_f1_threshold, df_y_pred, df_confusion_matrix, df_scores = EvaluateClassifier(model2, dfX_test, dfy_test)
    df_importances = ComputeFeatureImportances(model2, dfX_test, dfy_test)
    print('\nEVALUATION SCORES:\n')
    print(df_scores)
    print('\nTOP OF PRECISION-RECALL CURVE DATA:\n')
    print(df_precision_recall.head(12))
    print('\nTOP OF ROC CURVE DATA:\n')
    print(df_roc.head(12))
    print('\nFEATURE IMPORTANCES:\n')
    print(df_importances)

   # . . . or train it using a grid search, and evaluate the result
    print('\nGRID SEARCH WITH USER-SPECIFIED GRID...\n')
    model3 = ClassificationGridSearchCV(pipeline, dfX_train, dfy_train, dfX_test, dfy_test, scoring='roc_auc',
                                        classifier_grid_args={'C':[0.1,1,0000000.1],'n_jobs':[1]})
    df_precision_recall, df_roc, df_f1_threshold, df_y_pred, df_confusion_matrix, df_scores = EvaluateClassifier(model3, dfX_test, dfy_test)
    df_importances = ComputeFeatureImportances(model3, dfX_test, dfy_test)
    print('\nEVALUATION SCORES:\n')
    print(df_scores)
    print('\nTOP OF PRECISION-RECALL CURVE DATA:\n')
    print(df_precision_recall.head(12))
    print('\nTOP OF ROC CURVE DATA:\n')
    print(df_roc.head(12))
    print('\nFEATURE IMPORTANCES:\n')
    print(df_importances)
    

    # ==================
    # REGRESSION EXAMPLE
    # ==================

    df = pd.read_csv('C:\\Users\\mhorbach\\Datasets\\ENB2012.csv')
    target = 'Cooling Load'

    df = df.dropna(subset=[target])
    dfX = df.drop([target, 'Heating Load'], axis=1)
    dfy = df[target]
    

    dfX_train, dfX_test, dfy_train, dfy_test = train_test_split(dfX, dfy, random_state=59)
   
    MAX_LOW_CARDINALITY = 4
    MAX_HIGH_CARDINALITY = 50

    # define the pipeline . . .
    print('\nRANDOM FOREST:\n')
    pipeline = CreateRegressionPipeline(dfX_train, 
                                        max_low_cardinality=MAX_LOW_CARDINALITY, 
                                        max_high_cardinality=MAX_HIGH_CARDINALITY,
                                        algo='randomforest',
                                        regressor_args={'n_estimators':10,'n_jobs':1})

    ComputeLearningCurve(pipeline, dfX, dfy, 'regression')

    # . . . and train it using a grid search, and evaluate the result
    print('\nGRID SEARCH...\n')
    model1 = RegressionGridSearchCV(pipeline, dfX_train, dfy_train, dfX_test, dfy_test,
                                    scoring='neg_mean_squared_error')
    df_evaluation, scores = EvaluateRegressor(model1, dfX_test, dfy_test)
    df_importances = ComputeFeatureImportances(model1, dfX_test, dfy_test)
    print('\nEVALUATION SCORES:\n')
    print(scores)
    print('\nTOP OF EVALUATION PLOT DATA:\n')
    print(df_evaluation.head(12))
    print('\nFEATURE IMPORTANCES:\n')
    print(df_importances)

    # define the pipeline . . .
    print('\nXGBOOST:\n')
    pipeline = CreateRegressionPipeline(dfX_train, 
                                        max_low_cardinality=MAX_LOW_CARDINALITY, 
                                        max_high_cardinality=MAX_HIGH_CARDINALITY,
                                        algo='xgboost',
                                        regressor_args={'n_estimators':10})

    # . . . and train it using a grid search, and evaluate the result
    print('\nGRID SEARCH...\n')
    model1 = RegressionGridSearchCV(pipeline, dfX_train, dfy_train, dfX_test, dfy_test,
                                    scoring='neg_mean_squared_error')
    df_evaluation, scores = EvaluateRegressor(model1, dfX_test, dfy_test)
    df_importances = ComputeFeatureImportances(model1, dfX_test, dfy_test)
    print('\nEVALUATION SCORES:\n')
    print(scores)
    print('\nTOP OF EVALUATION PLOT DATA:\n')
    print(df_evaluation.head(12))
    print('\nFEATURE IMPORTANCES:\n')
    print(df_importances)

    # define the pipeline . . .
    print('\nRIDGE:\n')
    pipeline = CreateRegressionPipeline(dfX_train, 
                                        max_low_cardinality=MAX_LOW_CARDINALITY, 
                                        max_high_cardinality=MAX_HIGH_CARDINALITY,
                                        algo='ridge',
                                        regressor_args={'alpha':10})

    # . . . and train it using a grid search, and evaluate the result
    print('\nGRID SEARCH...\n')
    model1 = RegressionGridSearchCV(pipeline, dfX_train, dfy_train, dfX_test, dfy_test,
                                    scoring='neg_mean_squared_error')
    df_evaluation, scores = EvaluateRegressor(model1, dfX_test, dfy_test)
    df_importances = ComputeFeatureImportances(model1, dfX_test, dfy_test)
    print('\nEVALUATION SCORES:\n')
    print(scores)
    print('\nTOP OF EVALUATION PLOT DATA:\n')
    print(df_evaluation.head(12))
    print('\nFEATURE IMPORTANCES:\n')
    print(df_importances)

    # define the pipeline . . .
    print('\nLASSO:\n')
    pipeline = CreateRegressionPipeline(dfX_train, 
                                        max_low_cardinality=MAX_LOW_CARDINALITY, 
                                        max_high_cardinality=MAX_HIGH_CARDINALITY,
                                        algo='lasso',
                                        regressor_args={'alpha':10})

    # . . . and train it using a grid search, and evaluate the result
    print('\nGRID SEARCH...\n')
    model1 = RegressionGridSearchCV(pipeline, dfX_train, dfy_train, dfX_test, dfy_test,
                                    scoring='neg_mean_squared_error')
    df_evaluation, scores = EvaluateRegressor(model1, dfX_test, dfy_test)
    df_importances = ComputeFeatureImportances(model1, dfX_test, dfy_test)
    print('\nEVALUATION SCORES:\n')
    print(scores)
    print('\nTOP OF EVALUATION PLOT DATA:\n')
    print(df_evaluation.head(12))
    print('\nFEATURE IMPORTANCES:\n')
    print(df_importances)


    df = pd.read_csv('C:\\Users\\mhorbach\\Datasets\\bankchurners12mar.csv')
    target = 'Attrition_Flag'
      
    dfX = df.drop(target, axis=1)
    dfy = df[target]

    # For now, we require 0/1 labels in the functions, pos_label is set to 1
    dfy_aux = dfy.copy()
    dfy_aux[dfy=='Existing Customer'] = 0
    dfy_aux[dfy=='Attrited Customer'] = 1
    dfy = dfy_aux.astype(int)

    dfX_train, dfX_test, dfy_train, dfy_test = train_test_split(dfX, dfy, stratify=dfy, random_state=59)


    # define the pipeline . . .
    print('\nCARDINALITY BOUNDARY CASES - NO ENCODING AT ALL:\n')
    pipeline = CreateClassificationPipeline(dfX_train, 
                                            max_low_cardinality=1, 
                                            max_high_cardinality=1,
                                            algo='randomforest',
                                            classifier_args={'n_estimators':5,'min_samples_leaf':2,'n_jobs':1})

    # . . . and train it the simple way, and evaluate the result
    print('\nSIMPLE TRAINING...\n')
    model1 = pipeline.fit(dfX_train, dfy_train)
    print(model1.named_steps)
    df_precision_recall, df_roc, df_f1_threshold, df_y_pred, df_confusion_matrix, df_scores = EvaluateClassifier(model1, dfX_test, dfy_test)
    df_importances = ComputeFeatureImportances(model1, dfX_test, dfy_test)
    print('\nEVALUATION SCORES:\n')
    print(df_scores)
    print('\nTOP OF PRECISION-RECALL CURVE DATA:\n')
    print(df_precision_recall.head(12))
    print('\nTOP OF ROC CURVE DATA:\n')
    print(df_roc.head(12))
    print('\nFEATURE IMPORTANCES:\n')
    print(df_importances)
    print(model1.named_steps)
    
    # . . . or train it using a grid search, and evaluate the result
    print('\nGRID SEARCH...\n')
    model2 = ClassificationGridSearchCV(pipeline, dfX_train, dfy_train, dfX_test, dfy_test, scoring='roc_auc')
    df_precision_recall, df_roc, df_f1_threshold, df_y_pred, df_confusion_matrix, df_scores = EvaluateClassifier(model2, dfX_test, dfy_test)
    df_importances = ComputeFeatureImportances(model2, dfX_test, dfy_test)
    print('\nEVALUATION SCORES:\n')
    print(df_scores)
    print('\nTOP OF PRECISION-RECALL CURVE DATA:\n')
    print(df_precision_recall.head(12))
    print('\nTOP OF ROC CURVE DATA:\n')
    print(df_roc.head(12))
    print('\nFEATURE IMPORTANCES:\n')
    print(df_importances)


    # ==================================================
    # REGRESSION EXAMPLE TO TEST HIGH CARDINALITY SCALER
    # ==================================================

    df = pd.read_csv('C:\\Users\\mhorbach\\Datasets\\bankchurners.csv')
    target = 'Total_Trans_Ct'

    df = df.dropna(subset=[target])
    dfX = df.drop([target], axis=1)
    dfy = df[target]
    

    dfX_train, dfX_test, dfy_train, dfy_test = train_test_split(dfX, dfy, random_state=59)
   
    MAX_LOW_CARDINALITY = 4
    MAX_HIGH_CARDINALITY = 50

    # define the pipeline . . .
    print('\nRANDOM FOREST:\n')
    pipeline = CreateRegressionPipeline(dfX_train, 
                                        max_low_cardinality=MAX_LOW_CARDINALITY, 
                                        max_high_cardinality=MAX_HIGH_CARDINALITY,
                                        algo='randomforest',
                                        regressor_args={'n_estimators':10,'n_jobs':1})

    # . . . and train it using a grid search, and evaluate the result
    print('\nGRID SEARCH...\n')
    model1 = RegressionGridSearchCV(pipeline, dfX_train, dfy_train, dfX_test, dfy_test,
                                    scoring='neg_mean_squared_error')
    df_evaluation, scores = EvaluateRegressor(model1, dfX_test, dfy_test)
    df_importances = ComputeFeatureImportances(model1, dfX_test, dfy_test)
    print('\nEVALUATION SCORES:\n')
    print(scores)
    print('\nTOP OF EVALUATION PLOT DATA:\n')
    print(df_evaluation.head(12))
    print('\nFEATURE IMPORTANCES:\n')
    print(df_importances)


    # ==================================
    # REGRESSION EXAMPLE WITH NEURAL NET
    # ==================================

    #df = pd.read_csv('C:\\Users\\mhorbach\\Datasets\\ENB2012.csv')
    #target = 'Cooling Load'

    #df = df.dropna(subset=[target])
    #dfX = df.drop([target, 'Heating Load'], axis=1)
    #dfy = df[target]

    df = pd.read_csv('C:\\Users\\mhorbach\\Datasets\\kaggle_cars.csv')
    target = 'price'

    #df = df.dropna(subset=[target])
    dfX = df.drop([target, 'tax'], axis=1)
    dfy = df[target]
    

    dfX_train, dfX_test, dfy_train, dfy_test = train_test_split(dfX, dfy, random_state=59)
   
    MAX_LOW_CARDINALITY = 4
    MAX_HIGH_CARDINALITY = 50

    # define the pipeline . . .
    print('\nNEURALNET WITH DEFAULT PARMS:\n')
    pipeline = CreateRegressionPipeline(dfX_train, 
                                        max_low_cardinality=MAX_LOW_CARDINALITY, 
                                        max_high_cardinality=MAX_HIGH_CARDINALITY,
                                        algo='neuralnet', regressor_args={'epochs':100})

    df_learning_curve = ComputeLearningCurve(pipeline, dfX, dfy, 'regression')

    # straight fit
    model0 = pipeline.fit(dfX_train, dfy_train)
    df_evaluation, scores = EvaluateRegressor(model0, dfX_test, dfy_test)

    # define the pipeline . . .
    print('\nNEURALNET WITH USER-PARMS:\n')
    pipeline = CreateRegressionPipeline(dfX_train, 
                                        max_low_cardinality=MAX_LOW_CARDINALITY, 
                                        max_high_cardinality=MAX_HIGH_CARDINALITY,
                                        algo='neuralnet',
                                        regressor_args={'hidden_layers_sizes':(50,50,),'learning_rate':0.002,'epochs':100})


    # straight fit
    model0 = pipeline.fit(dfX_train, dfy_train)
    df_evaluation, scores = EvaluateRegressor(model0, dfX_test, dfy_test)


    # ==================================
    # REGRESSION EXAMPLE WITH NEURAL NET DEFAULT GRID
    # ==================================

    df = pd.read_csv('C:\\Users\\mhorbach\\Datasets\\ENB2012.csv')
    target = 'Cooling Load'

    df = df.dropna(subset=[target])
    dfX = df.drop([target, 'Heating Load'], axis=1)
    dfy = df[target]

    dfX_train, dfX_test, dfy_train, dfy_test = train_test_split(dfX, dfy, random_state=59)
   
    MAX_LOW_CARDINALITY = 4
    MAX_HIGH_CARDINALITY = 50

    # define the pipeline . . .
    print('\nNEURALNET:\n')
    pipeline = CreateRegressionPipeline(dfX_train, 
                                        max_low_cardinality=MAX_LOW_CARDINALITY, 
                                        max_high_cardinality=MAX_HIGH_CARDINALITY,
                                        algo='neuralnet')#, #,
                                        #regressor_args={'n_hidden':3,'n_neurons':200})

    # . . . and train it using a grid search, and evaluate the result
    print('\nGRID SEARCH...\n')
    model1 = RegressionGridSearchCV(pipeline,
                                    dfX_train, dfy_train,
                                    dfX_test, dfy_test,
                                    scoring='neg_mean_squared_error',
                                    #regressor_grid_args={'model__n_hidden':[3,4],'model__n_neurons':[100,400]}
                                    )
    
    df_evaluation, scores = EvaluateRegressor(model1, dfX_test, dfy_test)


    # ==================================
    # REGRESSION EXAMPLE WITH NEURAL NET USER GRID
    # ==================================

    df = pd.read_csv('C:\\Users\\mhorbach\\Datasets\\ENB2012.csv')
    target = 'Cooling Load'

    df = df.dropna(subset=[target])
    dfX = df.drop([target, 'Heating Load'], axis=1)
    dfy = df[target]

    dfX_train, dfX_test, dfy_train, dfy_test = train_test_split(dfX, dfy, random_state=59)
   
    MAX_LOW_CARDINALITY = 4
    MAX_HIGH_CARDINALITY = 50

    # define the pipeline . . .
    print('\nNEURALNET:\n')
    pipeline = CreateRegressionPipeline(dfX_train, 
                                        max_low_cardinality=MAX_LOW_CARDINALITY, 
                                        max_high_cardinality=MAX_HIGH_CARDINALITY,
                                        algo='neuralnet') #,
                                        #regressor_args={'n_hidden':3,'n_neurons':200})

    # . . . and train it using a grid search, and evaluate the result
    print('\nGRID SEARCH...\n')
    model1 = RegressionGridSearchCV(pipeline,
                                    dfX_train, dfy_train,
                                    dfX_test, dfy_test,
                                    scoring='neg_mean_squared_error',
                                    regressor_grid_args={'model__hidden_layers_sizes':[(1,),(50,50,),(100,100,)], 'optimizer__learning_rate':[0.0012, 0.00000001], 'epochs':[201], 'batch_size':[64]},
                                    )
    
    df_evaluation, scores = EvaluateRegressor(model1, dfX_test, dfy_test)

    
    # =============================================
    # BINARY CLASSIFICATION EXAMPLE WITH NEURAL NET
    # =============================================

    df = pd.read_csv('C:\\Users\\mhorbach\\Datasets\\bankchurners12mar.csv')
    target = 'Attrition_Flag'
      
    dfX = df.drop(target, axis=1)
    dfy = df[target]

    # For now, we require 0/1 labels in the functions, pos_label is set to 1
    dfy_aux = dfy.copy()
    dfy_aux[dfy=='Existing Customer'] = 0
    dfy_aux[dfy=='Attrited Customer'] = 1
    dfy = dfy_aux.astype(int)

    dfX_train, dfX_test, dfy_train, dfy_test = train_test_split(dfX, dfy, stratify=dfy, random_state=59)
   
    MAX_LOW_CARDINALITY = 4
    MAX_HIGH_CARDINALITY = 50

    # define the pipeline . . . 
    print('\nNEURAL NET:\n')
    pipeline = CreateClassificationPipeline(dfX_train, 
                                            max_low_cardinality=MAX_LOW_CARDINALITY, 
                                            max_high_cardinality=MAX_HIGH_CARDINALITY,
                                            algo='neuralnet',
                                            classifier_args={'patience':7,'epochs':88,'batch_size':22,'hidden_layers_sizes':(25,25,25,),'dropout':0,'learning_rate':0.002}
                                            ) # . . . and train it the simple way, and evaluate the result
    print('\nSIMPLE TRAINING...\n')
    model1 = pipeline.fit(dfX_train, dfy_train)
    print(model1.named_steps)
    df_precision_recall, df_roc, df_f1_threshold, df_y_pred, df_confusion_matrix, df_scores = EvaluateClassifier(model1, dfX_test, dfy_test)

    if False:
        df_importances = ComputeFeatureImportances(model1, dfX_test, dfy_test)
        print('\nFEATURE IMPORTANCES:\n')
        print(df_importances)

    print('\nEVALUATION SCORES:\n')   
    print(df_scores)
    print('\nTOP OF PRECISION-RECALL CURVE DATA:\n')
    print(df_precision_recall.head(12))
    print('\nTOP OF ROC CURVE DATA:\n')
    print(df_roc.head(12))

    

     # . . . and train it using a grid search, and evaluate the result
    print('\nGRID SEARCH WITH DEFAULT GRID ...\n')
    model1 = ClassificationGridSearchCV(pipeline,
                                    dfX_train, dfy_train,
                                    dfX_test, dfy_test,
                                    scoring='roc_auc',
                                    #classifier_grid_args={'model__n_hidden':[2],'model__n_neurons':[40,401], 'optimizer__learning_rate':[0.0015]},
                                    cv=10
                                    )

    print('CHECK THE GRID PARAMS NOW:', model1.best_estimator_) ##############???
    print('RESULTS:', model1.cv_results_)
    df_precision_recall, df_roc, df_f1_threshold, df_y_pred, df_confusion_matrix, df_scores = EvaluateClassifier(model1, dfX_test, dfy_test)
    print('\nEVALUATION SCORES:\n')   
    print(df_scores)


    print('\nGRID SEARCH WITH USER-SPECIFIED GRID ...\n')
    model1 = ClassificationGridSearchCV(pipeline,
                                    dfX_train, dfy_train,
                                    dfX_test, dfy_test,
                                    scoring='roc_auc',
                                    classifier_grid_args={'model__hidden_layers_sizes':[(1,),(50,50,),(100,100,)], 'optimizer__learning_rate':[0.0012, 0.00000001]},
                                    cv=10
                                    )

    print('CHECK THE GRID PARAMS NOW:', model1.best_estimator_) 
    print('RESULTS:', model1.cv_results_)
    df_precision_recall, df_roc, df_f1_threshold, df_y_pred, df_confusion_matrix, df_scores = EvaluateClassifier(model1, dfX_test, dfy_test)
    print('\nEVALUATION SCORES:\n')   
    print(df_scores)

    # =============================================
    # BINARY CLASSIFICATION EXAMPLE WITH NEURAL NET
    # =============================================

    df = pd.read_csv('C:\\Users\\mhorbach\\Datasets\\creditcard.csv')
    target = 'Class'
      
    dfX = df.drop(target, axis=1)
    dfy = df[target]

    # For now, we require 0/1 labels in the functions, pos_label is set to 1
    dfy_aux = dfy.copy()
    #dfy_aux[dfy=='Existing Customer'] = 0
    #dfy_aux[dfy=='Attrited Customer'] = 1
    dfy = dfy_aux.astype(int)

    dfX_train, dfX_test, dfy_train, dfy_test = train_test_split(dfX, dfy, stratify=dfy, random_state=59)
   
    MAX_LOW_CARDINALITY = 4
    MAX_HIGH_CARDINALITY = 50

    # define the pipeline . . . 
    print('\nNEURAL NET:\n')
    pipeline = CreateClassificationPipeline(dfX_train, 
                                            max_low_cardinality=MAX_LOW_CARDINALITY, 
                                            max_high_cardinality=MAX_HIGH_CARDINALITY,
                                            algo='neuralnet',
                                            classifier_args={'patience':5,'epochs':100,'batch_size':1000,'hidden_layers_sizes':(50,50,50,),'dropout':0.0,'learning_rate':0.001}
                                            ) # . . . and train it the simple way, and evaluate the result
    print('\nSIMPLE TRAINING...\n')
    model1 = pipeline.fit(dfX_train, dfy_train)
    print(model1.named_steps)
    df_precision_recall, df_roc, df_f1_threshold, df_y_pred, df_confusion_matrix, df_scores = EvaluateClassifier(model1, dfX_test, dfy_test)
 
    PLOTS = False


 
    
    






    
    

  

    

    
