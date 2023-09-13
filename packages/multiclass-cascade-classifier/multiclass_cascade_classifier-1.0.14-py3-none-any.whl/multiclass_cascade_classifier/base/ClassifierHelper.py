"""
Module ClassifierHelper

Classifier files related function

@author: ThomasAujoux
"""

import os
import joblib
import hashlib
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
# from xgboost import XGBClassifier

import multiclass_cascade_classifier.base.variables.Variables as var

classifiers = {
    var.SVM: SVC,
    var.RF: RandomForestClassifier,
    # var.XGBoost: XGBClassifier,
}




def hashing(a):
    """
    Hash a string.

    Parameters
    ----------
    a : String
        String to hash.

    Returns
    -------
    String
        Hashed string.

    """
    return hashlib.md5(a.encode()).hexdigest()

def dehashing(hashed, rawList):
    """
    Check in rawList if it contains the hashed version of the hashed string.

    Parameters
    ----------
    hashed : String
        String to dehash.
    rawList : List
        List of raw strings.

    Raises
    ------
    ValueError
        If no item in the list is equal to the hashed string once hashed itself.

    Returns
    -------
    raw : String
        Raw string.

    """
    for raw in rawList:
        if hashed == hashing(raw):
                return raw
    raise ValueError("No hashed value of the list matched with the value you're looking to de-hash.")

def get_sector_classifier(models_folder):
    """
    Load the sector classifier contained in models_folder.

    Parameters
    ----------
    models_folder : String
        Path to the models folder.

    Returns
    -------
    clf : Classifier
        Classifier.

    """
    clf = joblib.load(models_folder + "secteurs.joblib")
    return clf
    
def get_all_families_classifier(models_folder, sectors):
    """
    Load all the family classifier (one for each sector).

    Parameters
    ----------
    models_folder : String
        Path to the models folder.
    sectors : List
        List of sectors.

    Returns
    -------
    clfs : Dict
        {
            "sector 1": classifier 1,
            "sector 2": classifier 2,
        }.

    """
    clfs = { }
    for sector in sectors:
        joblib_path = models_folder + hashing(sector) + ".joblib"
        if os.path.exists(joblib_path):
            clfs[sector] = joblib.load(joblib_path)
        else:
            print("Warning: sector %s doesn't have a classifier." % sector)
    return clfs

def save_sector_classifier(clf, models_folder):
    """
    Save the sector classifier inside the models folder.

    Parameters
    ----------
    clf : Classifier
        To save.
    models_folder : String
        Path to the models folder.

    Returns
    -------
    None.

    """
    joblib_out = models_folder + "secteurs.joblib"
    saveClassifier(clf, joblib_out)
    
def save_family_classifier(clf, models_folder, sector):
    """
    Save the family classifier (for a sector) inside the models folder.

    Parameters
    ----------
    clf : Classifier
        To save.
    models_folder : String
        Path to the models folder.
    sector : String
        Sector name (hashed string will be the .joblib file's name).

    Returns
    -------
    None.

    """
    joblib_out = models_folder + hashing(sector) + ".joblib"
    saveClassifier(clf, joblib_out)

def save_all_family_classifier(clfs, models_folder):
    """
    Save all family classifiers (one for each sector) inside the models folder.

    Parameters
    ----------
    clfs : Dict
        {
            "sector 1": classifier 1,
            "sector 2": classifier 2,
        }.
    models_folder : String
        Path to the models folder.

    Returns
    -------
    None.

    """
    for sector in clfs.keys():
        clf = clfs[sector]
        save_family_classifier(clf, models_folder, sector)
        
def saveClassifier(clf, joblib_out):
    """
    Save the classifier.

    Parameters
    ----------
    clf : Classifier
        To save.
    joblib_out : String
        Path to the .joblib file where to save the classifier.

    Returns
    -------
    None.

    """
    joblib.dump(clf, joblib_out)

def get_nb_classes(models_folder):
    """
    Returns the number of sectors and families that can be predicted

    Parameters
    ----------
    models_folder : String
        Path to model folder.

    Returns
    -------
    nb_sectors : Integer
        Number of sectors.
    nb_families : Integer
        Number of families.

    """
    
    # Sector classifier
    clf_sector = get_sector_classifier(models_folder)
    sectors = clf_sector.classes_ # Classes of sector classifier
    nb_sectors = len(sectors) # Number of classes in sector classifier
    
    # Family classifiers
    nb_families = 0
    clfs_families = get_all_families_classifier(models_folder, sectors)
    for family in clfs_families:
        clf_family = clfs_families[family] # Classes of this family classifier
        families = clf_family.classes_ # Number of classes in this family classifier
        nb_families += len(families) # Number of classes in family classifiers
    
    return nb_sectors, nb_families
