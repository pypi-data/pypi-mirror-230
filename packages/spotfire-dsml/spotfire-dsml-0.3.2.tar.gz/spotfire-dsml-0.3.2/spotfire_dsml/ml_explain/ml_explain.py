def XWIN_single_instance(model, model_type, mode, df, metadata_json,  predictors_list=None, use_imputer=False, DEBUG=False):

    '''
    XWIN_single_instance

    inputs:
    - model, whose predictions are to be explained
    - model_type: 'sklearn' or 'model_ops'
    - mode ('classification' or 'regression', to select predict_proba or predict)
    - df, instance for which a prediction is made
    - predictors (not all columns in df need to be predictors, maybe default should be df.columns)
    - metadata_json
    - use_imputer = False [default] or True. If True, the trained imputer imputes the withheld information, rather than using the metadata.
      Note: in the True case metadata_json is still used to determine which columns are numeric
    - DEBUG = True for print statements

    output:
    - XWIN_impact_table, table whose columns are: Feature,
                                                  XWIN Impact Value,
                                                  Order,
                                                  Relative Feature Value,
                                                  Explanation In Words
      XWIN_impact_table is sorted by key=Order

   '''


    # Imports
    # =======

    import cloudpickle
    import json
    import numpy as np
    import pandas as pd
    from spotfire_dsml.ml_metadata import metadata_data as mdd
    from spotfire_dsml.ml_metadata import metadata_model as mdm


    # Initializations
    # ===============


    #predictors_list = predictors.split(',')  # <<<<<<<<<<<<<<<< depends on format in which 'predictors' is passed in
    #dfX = df[predictors_list]
    if predictors_list is None:
        predictors_list = df.columns
    dfX = df[predictors_list]
    features = dfX.columns


    # Pick up mean and std and dtypes from the metadata
    # =================================================

    # assuming the metadata is passed as dict, first convert to string here
    # NOTE the new function uses a dict so I am commenting this
    # metadata_json = json.dumps(metadata_json) # dict to str

    received_desc_worker, df_meta = mdd.DescribeWorker.unpack_json(metadata_json, return_df=True)
    stats_df = received_desc_worker.get_metric(['mean', 'std', 'dtype']).set_index('variable')

    if DEBUG:
        print('Metadata:\n', stats_df, flush=True)

    all_numeric_columns = stats_df[stats_df['dtype'] != 'object'].index.values

    if DEBUG:
        print('All numeric columns:\n', all_numeric_columns, flush=True)

    numeric_columns = []
    for col in all_numeric_columns:
        if col in predictors_list:
            numeric_columns.append(col)

    if DEBUG:
        print('All numeric predictors:\n', numeric_columns, flush=True)


    # Create the auxiliary instances in one matrix with the actual instance
    # =====================================================================

    dfX = dfX.reset_index(drop=True)
    K = dfX.shape[1]

    # Initialize dfX_auxiliary in its correct shape, with all numeric columns in float64.
    # The reason for float64 is that by sending in NaNs the type would change to float64, and
    # potentially the memory for the matrix would have to be reallocated if the type is smaller than 64 bits.


    dfX_original_plus_auxiliary = dfX.loc[dfX.index.repeat(K+1)].reset_index(drop=True)

    for col in numeric_columns:
        dfX_original_plus_auxiliary[col] = dfX_original_plus_auxiliary[col].astype('float64')

    # Now we have the memory, we assign the rows in dfX_auxiliary one at a time.
    # First row is the original instances, the next K rows are instances in which
    # one of the K features is modified. We here modify by substitution
    # with the mean values, but substituting with NaN is an option for later.

    dfX_original_plus_auxiliary.iloc[0] = dfX.iloc[0].copy()

    # Loop over all features and do the substitution
    j = 0
    for feature in features:
        if DEBUG:
            print(feature, flush=True)
        if feature in numeric_columns:
            if not use_imputer:
                dfX_original_plus_auxiliary.loc[j + 1,feature] = stats_df.loc[feature,'mean']
            else:
                dfX_original_plus_auxiliary.loc[j + 1,feature] = np.nan
        else:
            dfX_original_plus_auxiliary.loc[j + 1,feature] = '__UNKNOWN_CATEGORY__'
        j += 1

    # Compute the predictions for the entire group of auxiliary instances and the original instance
    # =============================================================================================

    scorer = mdm.init_scorer(model_type, model, mode)

    if mode =='classification':
        predictions = scorer.predict_probability(dfX_original_plus_auxiliary)[:,1]
    elif mode == 'regression':
        predictions = scorer.predict(dfX_original_plus_auxiliary)

    # Compute the impact values
    # =========================
    values = (predictions[0] - predictions)[1:]
    shifts = dict(zip(features, values))
    sorted_shifts_dict = dict(sorted(shifts.items(), key=lambda x: np.abs(x[1]), reverse=True))
    keys = list(sorted_shifts_dict.keys())
    values = list(sorted_shifts_dict.values())


    # Compute the relative feature values
    # ===================================

    relative_feature_values = []
    for key,val in zip(keys,values):
        if key not in numeric_columns:
            relative_feature_values.append(0.0)
            continue
        mean_key = stats_df.loc[key,'mean']
        std_key = stats_df.loc[key,'std']
        if np.isnan(dfX.loc[0,key]):
            relative_feature_value = 0.0
        else:
            relative_feature_value = (dfX.loc[0,key] - mean_key)/std_key
        if relative_feature_value > 2.0:
            relative_feature_value = 2.0
        elif relative_feature_value < -2.0:
            relative_feature_value = -2.0
        relative_feature_value /= 2.0
        relative_feature_values.append(relative_feature_value)


    # Create the XWIN impact table
    # ============================

    XWIN_impact_table = pd.DataFrame.from_dict({'Feature':keys, 'XWIN Impact Value':values})
    XWIN_impact_table['Relative Feature Value'] = relative_feature_values
    XWIN_impact_table['Importance Order'] = np.arange(1, XWIN_impact_table.shape[0] + 1)


    # Add explanations_in_words
    # =========================

    explanations_in_words = []
    for i, feature in enumerate(XWIN_impact_table['Feature'].values):
        relative_value_in_words = 'near-average'
        if XWIN_impact_table.loc[len(explanations_in_words), 'Relative Feature Value'] > 0.99:
            relative_value_in_words = 'very high'
        elif XWIN_impact_table.loc[len(explanations_in_words), 'Relative Feature Value'] > 0.5:
            relative_value_in_words = 'high'
        elif XWIN_impact_table.loc[len(explanations_in_words), 'Relative Feature Value'] > 0.25:
            relative_value_in_words = 'moderately high'
        elif XWIN_impact_table.loc[len(explanations_in_words), 'Relative Feature Value'] > 0.05:
            relative_value_in_words = 'somewhat elevated'
        elif XWIN_impact_table.loc[len(explanations_in_words), 'Relative Feature Value'] < -0.99:
            relative_value_in_words = 'very low'
        elif XWIN_impact_table.loc[len(explanations_in_words), 'Relative Feature Value'] < -0.5:
            relative_value_in_words = 'low'
        elif XWIN_impact_table.loc[len(explanations_in_words), 'Relative Feature Value'] < -0.25:
            relative_value_in_words = 'moderately low'
        elif XWIN_impact_table.loc[len(explanations_in_words), 'Relative Feature Value'] < -0.05:
            relative_value_in_words = 'somewhat depressed'

        amount = XWIN_impact_table.loc[len(explanations_in_words), 'XWIN Impact Value']
        if amount >= 0:
            direction = 'increases'
        elif amount < 0:
            direction = 'decreases'
        amount = str(round(amount,2))
        explanations_in_words.append('The ' + relative_value_in_words + ' value of ' + feature + ' ' + direction + ' the model-prediction by ' + amount)

    XWIN_impact_table['Explanation In Words'] = explanations_in_words

    if DEBUG:
        print('XWIN_impact_table:\n', XWIN_impact_table, flush=True)

    return XWIN_impact_table


def XWIN_batch(model, model_type, mode, df, metadata_json, predictors_list=None, use_imputer=False, DEBUG=False):

    '''
    XWIN_batch

    inputs:
    - model, whose predictions are to be explained
    - model_type: 'sklearn' or 'model_ops'
    - mode (classification or regression, to select predict_proba or predict)
    - df, batch of instances for which a predictions are made
    - predictors (not all columns in df need to be predictors, maybe default should be df.columns)
    - metadata_json
    - use_imputer = False [default] or True. If True, the trained imputer imputes the withheld information, rather than using the metadata.
      Note: in the True case metadata_json is still used to determine which columns are numeric, and for computing Relative Feature Value
    - DEBUG = True for print statements

    output:
    - XWIN_batch_impact_table, dataframe whose columns are: Feature,
                                                      XWIN Impact Value,
                                                      Order,
                                                      Relative Feature Value,
                                                      Explanation In Words
      XWIN_batch_impact_table is sorted by key=Order

    '''


    # Imports
    # =======

    import cloudpickle
    import numpy as np
    import pandas as pd
    import json
    from spotfire_dsml.ml_metadata import metadata_data as mdd
    from spotfire_dsml.ml_metadata import metadata_model as mdm


    # Initializations
    # ===============

    #GAIA17May: This should go too as the scorer does the job now
    #model = cloudpickle.loads(model) # <<<<<<<<<<<<<<<< depends on how the model is passed in


    # Randomly select a batch of 'batch_size' instances
    # =================================================

    batch_size = 100
    #predictors_list = predictors.split(',')   # <<<<<<<<<<<<<<<< depends on format in which 'predictors' is passed in
    #dfX = df[predictors_list]
    if predictors_list is None:
        predictors_list = df.columns
    dfX = df[predictors_list]

    if dfX.shape[0] > batch_size:
        n_explanation_instances = batch_size
        scorer = mdm.init_scorer('sklearn', model, mode)
        half_batch_size = int(batch_size/2)
        if mode == 'regression':
            preds = scorer.predict(dfX)
            # take equal sample of small and large predictions, say two outer quartiles
            Q1 = np.quantile(preds, 0.25)
            Q3 = np.quantile(preds, 0.75)
            large_preds_idx = np.where(preds > Q3)
            small_preds_idx = np.where(preds < Q1)
            np.random.seed(59)        
            if len(large_preds_idx) > half_batch_size:
                large_preds_idx_half_batch_size = np.random.choice(large_preds_idx, half_batch_size, replace=False)
            else:
                large_preds_idx_half_batch_size = large_preds_idx
            if len(small_preds_idx) > half_batch_size:
                small_preds_idx_half_batch_size = np.random.choice(small_preds_idx, half_batch_size, replace=False)
            else:
                small_preds_idx_half_batch_size = small_preds_idx
            idx = np.concatenate((large_preds_idx_half_batch_size, small_preds_idx_half_batch_size), axis=1)[0]
            dfX_batch = dfX.iloc[idx,:]      
        elif mode == 'classification':
            probs = scorer.predict_probability(dfX)[:,1]
            # take equal sample of small and large probabilities:
            large_probs_idx = np.where(probs > 0.8)[0]
            small_probs_idx = np.where(probs < 0.2)[0]
            np.random.seed(59)
            if len(large_probs_idx) > half_batch_size:
                large_probs_idx_half_batch_size = np.random.choice(large_probs_idx, half_batch_size, replace=False)
            else:
                large_probs_idx_half_batch_size = large_probs_idx
            if len(small_probs_idx) > half_batch_size:
                small_probs_idx_half_batch_size = np.random.choice(small_probs_idx, half_batch_size, replace=False)
            else:
                small_probs_idx_half_batch_size = small_probs_idx    
            idx = np.concatenate((large_probs_idx_half_batch_size, small_probs_idx_half_batch_size))
            dfX_batch = dfX.iloc[idx,:] 
    else:
        n_explanation_instances = dfX.shape[0]
        dfX_batch = dfX
        
    batch_size = dfX_batch.shape[0]

    if DEBUG:
        print('Batch info:\n', dfX_batch.info(), flush=True)


    # Pick up mean and std and dtypes from the metadata
    # =================================================

    # assuming the metadata is passed as dict, first convert to string here
    # NOTE the new function uses a dict so I am commenting this
    # metadata_json = json.dumps(metadata_json) # dict to str

    received_desc_worker, df_meta = mdd.DescribeWorker.unpack_json(metadata_json, return_df=True)
    stats_df = received_desc_worker.get_metric(['mean', 'std', 'dtype']).set_index('variable')

    if DEBUG:
        print('Metadata:\n', stats_df, flush=True)

    all_numeric_columns = stats_df[stats_df['dtype'] != 'object'].index.values

    if DEBUG:
        print('All numeric columns:\n', all_numeric_columns, flush=True)

    numeric_columns = []
    for col in all_numeric_columns:
        if col in predictors_list:
            numeric_columns.append(col)

    if DEBUG:
        print('All numeric predictors:\n', numeric_columns, flush=True)


    # Compute data for additional information: relative feature values
    # (the colors of the datapoints in the scatter plot)
    # ================================================================

    color_matrix = np.zeros(dfX_batch.shape)
    for i in range(color_matrix.shape[0]):
        for j in range(color_matrix.shape[1]):
            if dfX.columns[j] in numeric_columns:
                #if DEBUG:
                #    print('Numeric feature = ', dfX.columns[j], ' with value ', dfX_batch.iloc[i,j], flush=True)
                if np.isnan(dfX_batch.iloc[i,j]):
                    color_matrix[i,j] = 0
                else:
                    color_matrix[i,j] = (dfX_batch.iloc[i,j] - stats_df.loc[dfX.columns[j],'mean'])/stats_df.loc[dfX.columns[j],'std']
            else:
                #if DEBUG:
                #    print('Categoric feature = ', dfX.columns[j], ' with value ', dfX_batch.iloc[i,j], flush=True)
                color_matrix[i,j] = 0
            # Do truncation for meaningful colors that are not determined by the outliers
            if color_matrix[i,j] > 2.0:
                color_matrix[i,j] = 2.0
            if color_matrix[i,j] < -2.0:
                color_matrix[i,j] = -2.0
            color_matrix[i,j] /= 2.0


    # Compute the impact values for all features of all instances in the batch
    # Implementation: use only one call to the predict service, anticipating
    # a call to the ModelOps API for scoring.
    # ========================================================================

    features = dfX.columns
    impact_matrix = np.zeros(dfX_batch.shape)
    numeric_columns = dfX_batch.select_dtypes(exclude='object').columns
    categoric_columns = dfX_batch.select_dtypes(include='object').columns
    if DEBUG:
        print('impact matrix shape:', impact_matrix.shape, flush=True)

    # Create dfX_batch_auxiliary that will be sent to the predict service to get all auxiliary predictions
    # ----------------------------------------------------------------------------------------------------

    K = dfX_batch.shape[1]

    # Initialize dfX_batch_auxiliary in its correct shape, with all numeric columns in float64.
    # The reason for float64 is that by sending in NaNs the type would change to float64, and
    # potentially the memory for the matrix would have to be reallocated if the type is smaller than 64 bits.

    dfX_batch_auxiliary = dfX_batch.loc[dfX_batch.index.repeat(K+1)].reset_index(drop=True)
    for col in numeric_columns:
        dfX_batch_auxiliary[col] = dfX_batch_auxiliary[col].astype('float64')

    # Now we have the memory, we assign the rows in dfX_batch_auxiliary one at a time.
    # Layout: 'batch_size' instances give 'batch_size' groups, each group consisting of K + 1
    # rows where K is the number of features. Each group first has the original row, followed
    # by the K rows that are the modified versions of that row. We here modify by substitution
    # with the mean values, but substituting with NaN is an option for later.

    # Loop over the original rows in the batch
    for i in range(dfX_batch.shape[0]):

        # The first row in each group in dfX_batch_auxiliary is the original row
        dfX_batch_auxiliary.iloc[i * (K + 1)] = dfX_batch.iloc[i].copy()

        # For each original row loop over all features and do the sunstitution
        j = 0
        for feature in features:
            if feature in numeric_columns:
                if not use_imputer:
                    dfX_batch_auxiliary.loc[i * (K + 1) + (j + 1),feature] = stats_df.loc[feature,'mean']
                else:
                    dfX_batch_auxiliary.loc[i * (K + 1) + (j + 1),feature] = np.nan
            else:
                dfX_batch_auxiliary.loc[i * (K + 1) + (j + 1),feature] = '__UNKNOWN_CATEGORY__'

            j += 1

    # Send dfX_batch_auxiliary for scoring
    # ------------------------------------

    scorer = mdm.init_scorer(model_type, model, mode)
    if mode =='classification':
        auxiliary_predictions = scorer.predict_probability(dfX_batch_auxiliary)[:,1]
    elif mode == 'regression':
        auxiliary_predictions = scorer.predict(dfX_batch_auxiliary)

    # Construct the impact matrix itself
    # ----------------------------------

    impact_matrix = np.zeros((batch_size, K))

    # For every row in the original batch ...
    for i in range(batch_size):
        # ... compute the impact values from the relevant auxiliary_predictions components
        impact_values = auxiliary_predictions[i * (K + 1)] - auxiliary_predictions[i * (K + 1) + 1: (i + 1) * (K + 1)]
        impact_matrix[i,:] = impact_values

    # Combine the impact values and the relative feature values in one dataframe
    # ==========================================================================

    df_out_xwin = pd.DataFrame(data=impact_matrix.transpose(), index=dfX_batch.columns)
    df_out_xwin['sortkey'] = np.sum(np.abs(df_out_xwin), axis=1)
    df_colors = pd.DataFrame(color_matrix.transpose(), index=df_out_xwin.index)
    df_out_xwin = pd.concat([df_out_xwin, df_colors], axis=1)


    # Create output in a format that is digestible for Spotfire (or other visualization tools)
    # ========================================================================================

    # sort
    df_out_xwin = df_out_xwin.sort_values(by='sortkey', ascending=False).drop('sortkey', axis=1)
    df_out_xwin.insert(0, 'Feature order', np.arange(1, df_out_xwin.shape[0] + 1))
    df_out_xwin.reset_index(inplace=True)
    df_out_xwin.rename(columns={'index':'Feature'}, inplace=True)

    # output digestible by Spotfire
    df_1 = df_out_xwin.iloc[:,:2+n_explanation_instances].copy()
    df_1_unpivot = df_1.melt(id_vars=['Feature','Feature order'], value_vars=df_1.columns[2:], var_name='Instance', value_name='Impact')
    df_2 = df_out_xwin.iloc[:,2+n_explanation_instances:].copy()
    df_2.insert(0, 'Feature', df_out_xwin['Feature'].copy())
    df_2_unpivot = df_2.melt(id_vars=['Feature'], value_vars=df_2.columns[1:], var_name='Instance', value_name='Relative FEATURE-value')
    df_xwin_batch_impact_table = df_1_unpivot
    df_xwin_batch_impact_table['Relative FEATURE-value'] = df_2_unpivot['Relative FEATURE-value']

    if DEBUG:
        print('df_xwin_batch_impact_table:\n', df_xwin_batch_impact_table, flush=True)

    return df_xwin_batch_impact_table

