"""
Module FeaturesManipulator

Features related functions

@author: ThomasAujoux
"""



import pandas as pd

import multiclass_cascade_classifier.base.variables.Variables as var



def features_truncate(X_res):
    """
    Truncates non relevant features.

    Parameters
    ----------
    X_res : pd.DataFrame
        Vectorized data.

    Returns
    -------
    X_res_vect : TYPE
        DESCRIPTION.

    """
    X_res_txt = X_res[X_res.columns.to_list()[:-var.nb_bin_features]]
    X_res_txt = [row[:-var.nb_bin_features] for row in X_res.values.tolist()]
    X_res_txt = pd.DataFrame(X_res_txt, columns=X_res.columns.to_list()[:-var.nb_bin_features], index=X_res.index)

    # Removing columns with only zeros
    X_res_txt = X_res_txt.loc[:, (X_res_txt != 0).any(axis=0)]
    # Removing columns with only ones
    X_res_txt = X_res_txt.loc[:, (X_res_txt != 1).any(axis=0)]

    # Concatenation with binary data
    X_res_bin = [row[-var.nb_bin_features:] for row in X_res.values.tolist()]
    X_res_bin = pd.DataFrame(X_res_bin, columns=X_res.columns.to_list()[-var.nb_bin_features:], index=X_res.index)

    X_res_data = []
    for index, row in X_res_txt.iterrows():
        X_res_data.append(X_res_txt.loc[index].values.tolist() + X_res_bin.loc[index].values.tolist())
    X_res_vect = pd.DataFrame(X_res_data, columns=X_res_txt.columns.to_list() + X_res_bin.columns.to_list(), index=X_res.index)
    
    return X_res_vect

def features_intersection(X, features):
    
    features_text = features[:-var.nb_bin_features]
    
    X_columns_text = X.columns.to_list()[:-var.nb_bin_features]
    X_columns_bin = X.columns.to_list()[-var.nb_bin_features:]
    
    X_text = [row[:-var.nb_bin_features] for row in X.values.tolist()]
    X_text = pd.DataFrame(X_text, columns=X_columns_text, index=X.index)
    X_bin = [row[-var.nb_bin_features:] for row in X.values.tolist()]
    X_bin = pd.DataFrame(X_bin, columns=X_columns_bin, index=X.index)
    
    features_to_drop = [(feature if feature not in features_text else None) for feature in X_text.columns.to_list()]
    features_to_drop = list(filter(None, features_to_drop))
    
    X_text = X_text.drop(columns=features_to_drop)
    
    for feature in features_text:
        if feature not in X_text.columns.to_list():
            # feature_column = pd.DataFrame(0, columns=[feature], index=X_text.index)
            # X_text = pd.concat([X_text, feature_column], axis=1)
            X_text[feature] = 0

    X_text = X_text[features_text]
    
    X_vect = pd.concat([X_text, X_bin], axis=1)

    return X_vect