"""
Module DataPredicter

Data prediction related functions

@author: ThomasAujoux
"""



import pandas as pd

import multiclass_cascade_classifier.base.variables.Variables as var
from multiclass_cascade_classifier.base.ClassifierHelper import get_sector_classifier, get_all_families_classifier
from multiclass_cascade_classifier.base.FeaturesManipulator import features_truncate, features_intersection



def predict_sectors(X, models_folder):
    """
    Predicts sectors

    Parameters
    ----------
    X : pd.DataFrame
        Data set.
    models_folder : String
        Path to models folder.

    Returns
    -------
    y_pred : pd.DataFrame
        Predicted data.

    """
    
    # Load sector classifier
    clf = get_sector_classifier(models_folder)
    
    # Features the classifier was trained on
    features = clf.feature_names_in_
    X = features_intersection(X, features)
    
    # Predicting sector
    y_pred = clf.predict(X)
    y_pred = pd.DataFrame(y_pred, columns=["%s %s" % (var.prediction, var.secteur)], index=X.index)
    
    # Probability
    y_pred_probas = clf.predict_proba(X)
    y_pred_probas = pd.DataFrame(y_pred_probas, columns=clf.classes_, index=X.index)
    y_pred[var.proba] = 0
    for index, row in y_pred_probas.iterrows():
        y_pred.loc[index, var.proba] = round(sorted(row, reverse=True)[0]*100, 2)
    
    return y_pred

def predict_families_simple(X, y_pred_sector, clfs):
    """
    Predicts families (only one)

    Parameters
    ----------
    X : pd.DataFrame
        Data set.
    y_pred_sector : pd.DataFrame
        Predicted sectors.
    clfs : Dict<Classifiers>
        Classifiers.

    Raises
    ------
    ValueError
        If there is no classifier saved for a sector.

    Returns
    -------
    df_y_pred : pd.DataFrame
        Predicted families.

    """
    
    # List of sectors in data set
    sectors = sorted(y_pred_sector["%s %s" % (var.prediction, var.secteur)].unique())
    
    data_pred = []
    data_index = []
    
    for sector in sectors:
        
        if not sector in clfs.keys():
            raise ValueError("There is no classifier saved for sector " + sector)
            
        print(sector)
        
        ## Set of products that were predicted to belong to this sector
        y_res = y_pred_sector[y_pred_sector["%s %s" % (var.prediction, var.secteur)] == sector]
        X_res = X.loc[y_res.index]

        ## Retrieving only interesting features
        X_res_vect = features_truncate(X_res)
        clf = clfs[sector]
        features = clf.feature_names_in_
        X_res_vect = features_intersection(X_res_vect, features)
        
        ## Predicting
        y_pred = clf.predict(X_res_vect)
        index_res = y_res.index.to_list()
        for index in range(len(index_res)):
            data_index.append(index_res[index])
            data_pred.append([sector, round(y_pred[index], 2)])
            
    columns_names = [var.predicted_secteur, var.predicted_famille]
        
    df_y_pred = pd.DataFrame(data_pred, columns=columns_names, index=data_index)
    df_y_pred = df_y_pred.reindex(X.index)
    
    return df_y_pred
            
def predict_families_multi(X, y_pred_sector, clfs, n_families):
    """
    Predicts multiple families (+ probas)

    Parameters
    ----------
    X : pd.DataFrame
        Data set.
    y_pred_sector : pd.Dataframe
        Predicted sectors.
    clfs : List<Classifier>
        List of family classifiers.
    n_families : Integer
        Number of families to predict.

    Raises
    ------
    ValueError
        If there is no classifier saved for a sector.

    Returns
    -------
    df_y_pred : pd.DataFrame
        Predicted families.

    """
    
    # List of sectors in data set
    sectors = sorted(y_pred_sector["%s %s" % (var.prediction, var.secteur)].unique())

    data_pred = []
    data_index = []
    
    for sector in sectors:
        
        if not sector in clfs.keys():
            raise ValueError("There is no classifier saved for sector " + sector)
            
        print(sector)
        
        ## Set of products that were predicted to belong to this sector
        y_res = y_pred_sector[y_pred_sector["%s %s" % (var.prediction, var.secteur)] == sector]
        X_res = X.loc[y_res.index]
        index_res = y_res.index.to_list()

        ## Retrieving only interesting features
        X_res_vect = features_truncate(X_res)
        clf = clfs[sector]
        features = clf.feature_names_in_
        X_res_vect = features_intersection(X_res_vect, features)
        
        ## Predicting
        # Probabilities
        y_pred_probas = clf.predict_proba(X_res_vect)
        y_pred_probas = pd.DataFrame(y_pred_probas, columns=clf.classes_, index=index_res)
        # For each products, retrieving nth highest probability
        # to find the nth more probable family
        for index, row in y_pred_probas.iterrows():
            values = sorted(row, reverse=True)[:n_families]
            for n in range(len(values), n_families):
                values.append(0)
            columns = []
            for n in range(n_families):
                if values[n] != 0:
                    sub_probas = y_pred_probas.columns[row == values[n]].to_list()
                    columns.append(','.join(sub_probas))
                    columns.append(round(values[n] * 100, 3))
                else:
                    columns.append(None)
                    columns.append(None)
            
            data_index.append(index)
            data_pred.append([sector, y_pred_sector[var.proba].loc[index]] + columns)
    
    columns_names = ["%s %s" % (var.prediction, var.secteur), var.proba]
    for n in range(1, n_families + 1):
        columns_names.append("%s %s %i" % (var.prediction, var.famille,  n))
        columns_names.append("%s %s" % (var.proba, n))
        
    df_y_pred = pd.DataFrame(data_pred, columns=columns_names, index=data_index)
    df_y_pred = df_y_pred.reindex(X.index)
    
    return df_y_pred

def predict_families_per_sector_classifier(X, y_pred_sector, models_folder, n_families):
    """
    Calls family predicting functions.

    Parameters
    ----------
    X : pd.DataFrame
        Data set.
    y_pred_sector : pd.Dataframe
        Predicted sectors of data set.
    models_folder : String
        Path to models folder.
    n_families : Integer
        Number of families to predict.

    Returns
    -------
    df_y_pred : pd.DataFrame
        predicted families.

    """
    
    ## Retrieving family classifiers
    sectors = sorted(y_pred_sector["%s %s" % (var.prediction, var.secteur)].unique())
    clfs = get_all_families_classifier(models_folder, sectors)
    
    ## If multiple prediction
    if n_families:
        df_y_pred = predict_families_multi(X, y_pred_sector, clfs, n_families)
    ## If single prediction
    else:
        df_y_pred = predict_families_simple(X, y_pred_sector, clfs)
        
    return df_y_pred