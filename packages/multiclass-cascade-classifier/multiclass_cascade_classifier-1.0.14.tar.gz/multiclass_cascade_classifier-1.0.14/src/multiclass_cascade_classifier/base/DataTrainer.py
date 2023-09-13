"""
Module DataTrainer

Data training related functions

@author: ThomasAujoux
"""


from pathlib import Path

import multiclass_cascade_classifier.base.variables.Variables as var
from multiclass_cascade_classifier.base.FeaturesManipulator import features_truncate



def train_sector_classifier(X, y, clf, logjournal=None):
    """
    Initializes and trains the sector classifier.
    Selects hyperparameters if necessary (no yaml_sector_in file given).
    Saves the classifier into a .joblib file.

    Parameters
    ----------
    X : pd.DataFrame
        Data train set.
    y : pd.DataFrame
        Labels (sector and family).
    clf : Classifier
        Initialized classifier to train.
        
    Returns 
    -------
    clf : Classifier
        Trained classifier.

    """
    
    y_sector = y[var.id_secteur]
    
    if logjournal:
        logjournal.write_text("\tSector classifier training.")
    
    ## Training
    clf.fit(X, y_sector)
    print(clf)
    return clf
    
def train_families_per_sector_classifier(X, y, clfs, logjournal=None):
    """
    Initaliazes and trains one family classifier per sector.
    Selectes hyperparameters if necessary.
    Saves the classifiers into .joblib files.

    Parameters
    ----------
    X : pd.DataFrame
        Data train set.
    y : pd.DataFrame
        Labels (sector and family).
    clfs : Dict<Classifier>
        Initialized classifiers to train.
        
    Returns
    -------
    clf : Dict<Classifier>
        Trained classifiers.

    """
    
    # Going through each sector of the data training set
    sectors = sorted(y[var.id_secteur].unique())
    for sector in sectors:

        if logjournal:
            logjournal.write_text("\tFamily classifier training: %s." % sector)
        
        y_res = y[y[var.id_secteur] == sector][var.id_famille]
        X_res = X.loc[y_res.index]

        ## Retrieving only interesting features

        X_res_vect = features_truncate(X_res)
        
        # Checking if the family classifier was initialized
        # Selecting hyperparameters if not the case
        if sector in clfs.keys():
            clf = clfs[sector]
        else:
            continue
        
        ## Training
        clf.fit(X_res_vect, y_res)
        
        # Replacing the untrained classifier by the trained one
        clfs[sector] = clf
    print(clfs)
    return clfs

