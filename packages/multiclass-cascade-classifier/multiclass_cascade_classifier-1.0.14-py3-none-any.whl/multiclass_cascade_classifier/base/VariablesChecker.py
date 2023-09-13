"""
Module VariablesChecker

Variables checker related functions

@author: ThomasAujoux
"""



import os
import glob
import yaml

import multiclass_cascade_classifier.base.variables.Variables as var
from multiclass_cascade_classifier.base.HyperSelector import get_sectors_from_family_yaml
from multiclass_cascade_classifier.base.ClassifierHelper import hashing, get_sector_classifier, get_all_families_classifier



def check_exists(path):
    """
    Checks if the path exists.

    Parameters
    ----------
    path : String
        Folder/File path.

    Raises
    ------
    FileNotFoundError
        If the path doesn't exist.

    Returns
    -------
    None.

    """
    if not os.path.exists(path):
        raise FileNotFoundError("This path leads no where: %s" % path)

def check_csv(csv_path, check_existence=False):
    """
    Checks csv file path.

    Parameters
    ----------
    csv_path : String
        Path to csv file.
    check_existence : Boolean, optional
        Checks existence of path if True. The default is False.

    Raises
    ------
    FileNotFoundError
        If path is not valid.

    Returns
    -------
    csv_path : String
        Valid path.

    """
    
    if not csv_path or csv_path == "":
        raise FileNotFoundError("Csv file path should not be None.")
    
    if not csv_path.endswith(".csv"):
        raise FileNotFoundError("Wrong file extention: please use csv.")
        
    if check_existence:
        check_exists(csv_path)
        
    return csv_path

def check_yaml(yaml_path, check_existence=False):
    """
    Checks yaml file path.

    Parameters
    ----------
    yaml_path : String
        Path to yaml file.
    check_existence : Boolean, optional
        Checks existence of path if True. The default is False.

    Raises
    ------
    FileNotFoundError
        If path is not valid.

    Returns
    -------
    yaml_path : String
        Valid path.

    """
    
    if yaml_path == None or yaml_path == "":
        return
    
    if not yaml_path.endswith(".yaml") and not yaml_path.endswith(".yml"):
        raise FileNotFoundError("Wrong file extention: please use yaml.")
        
    check_exists(yaml_path)
    
    return yaml_path
        
def check_folder(folder_path, check_existence=False):
    """
    Checks folder path.

    Parameters
    ----------
    folder_path : String
        Path to folder.
    check_existence : Boolean, optional
        Checks existence of path if True. The default is False.

    Raises
    ------
    FileNotFoundError
        If path is not valid.

    Returns
    -------
    folder_path : String
        Valid path.

    """
    
    if not folder_path or folder_path == "":
        raise FileNotFoundError("Folder path should not be None.")
    
    if not folder_path.endswith("/"):
        folder_path += "/"
    
    if check_existence:
        check_exists(folder_path)
        
    return folder_path
        
def create_folder(folder_path):
    """
    Create folder path.

    Parameters
    ----------
    folder_path : String
        Path to folder.

    Returns
    -------
    folder_path : String
        Valid path.

    """
    
    if not folder_path.endswith("/"):
        folder_path += "/"
    
    folder_exists = os.path.exists(folder_path)
    
    if folder_exists:
        files = glob.glob("%s*" % folder_path)
        for f in files:
            os.remove(f)
    else:
        check_folder(folder_path, False)
            
        path_split = folder_path.split("/")
        
        for index in range(len(path_split)):
            path = "/".join(path_split[:index + 1])
            if not os.path.exists(path):
                os.mkdir(path)
    
    return folder_path

def check_test_size(test_size):
    """
    Checks test size.

    Parameters
    ----------
    test_size : Integer
        Size of test set (for the split).

    Raises
    ------
    ValueError
        If test size value isn't valid.

    Returns
    -------
    test_size : Integer
        Valid value.

    """
    
    if not test_size:
        raise ValueError("Test size cannot be None.")
    
    if not 0 <= test_size <= 1:
        raise ValueError("Test size is out of bound: %f" % test_size)
        
    return test_size

def checks_nFamilies(n_families):
    """
    Checks number of families to predict.

    Parameters
    ----------
    n_families : Integer
        Number of families to predict.

    Raises
    ------
    ValueError
        If n_families value isn't valid.

    Returns
    -------
    n_families : Integer
        Valid number of families.

    """
    
    if not n_families:
        raise ValueError("Number of families to predict cannot be None.")
    
    if not isinstance(n_families, int):
        raise ValueError("Number of families to predict should be an integer : %s." % n_families)
        
    if not n_families > 0:
        raise ValueError("Number of families to predict should not be zero: %i." % n_families)
        
    return n_families

def check_trained_classifiers(models_folder):
    """
    Checks classifiers in the folder model.
    Checks that the sectors predicted by the sector classifier all have a family classifier.
    (Checks that the sector classifier correspond to the family classifiers.)

    Parameters
    ----------
    models_folder : String
        Path to models folder.

    Raises
    ------
    FileNotFoundError
        If classifiers aren't valid.

    Returns
    -------
    models_folder : String
        Path to valid models folder.

    """
    
    if not models_folder.endswith("/"):
        models_folder += "/"
    
    clf_sector = get_sector_classifier(models_folder)
    
    sectors_clf = clf_sector.classes_
    
    sectors_diff = []
    for sector in sectors_clf:
        joblib_path = models_folder + hashing(sector) + ".joblib"
        if not os.path.exists(joblib_path):
            sectors_diff.append(sector)
            
    if sectors_diff:
        raise FileNotFoundError("Some sectors don't have a classifier: %s." % sectors_diff)
        
    return models_folder

def check_yaml_sector(yaml_sector_in):
    """
    Checks the content of the yaml file for the sector classifier.

    Parameters
    ----------
    yaml_sector_in : String
        Path to yaml file.

    Raises
    ------
    ValueError
        If the classifier's type is unknown.

    Returns
    -------
    yaml_sector_in: String
        Valid path.

    """
    if yaml_sector_in:
        with open(yaml_sector_in) as f:
            clf_yaml = yaml.load(f, Loader=yaml.FullLoader)
            ## Case: the classifier filled in the yaml isn't known
            clf_type = clf_yaml[var.classifierType]
            if clf_type not in [var.SVM, var.RF]:
                raise ValueError("Classifier type should be " + " or ".join([var.SVM, var.RF]))
            
    return yaml_sector_in

def check_yaml_families(yaml_families_in):
    """
    Checks the content of the yaml file for the family classifiers.

    Parameters
    ----------
    yaml_families_in : String
        Path to yaml file.

    Raises
    ------
    ValueError
        If one classifier's type is unknown.

    Returns
    -------
    yaml_families_in: String
        Valid path.

    """
    if yaml_families_in:
        with open(yaml_families_in) as f:
            clf_list_yaml = yaml.load(f, Loader=yaml.FullLoader)
            for clf_yaml in clf_list_yaml:
                ## Case: the classifier filled in the yaml isn't known
                clf_type = clf_yaml[var.classifierType]
                if clf_type not in [var.SVM, var.RF]:
                    raise ValueError("Classifier type should be " + " or ".join([var.SVM, var.RF]))
                
    return yaml_families_in
        

def check_classifiers_train_sectors(y, yaml_families_in):
    """
    Checks if all sectors in the train set appears in the yaml file.

    Parameters
    ----------
    y : pd.DataFrame
        Labels.
    yaml_families_in : String
        Path to yaml file.

    Returns
    -------
    sectors_diff : List<String>
        List of sectors that are in the training set but do not appear in the yaml file.

    """
    
    y_sector = sorted(y[var.id_secteur].unique())
    yaml_sector = get_sectors_from_family_yaml(yaml_families_in)
    
    sectors_diff = [sector if sector not in yaml_sector else None for sector in y_sector]
    sectors_diff = list(filter(None, sectors_diff))
    
    return sectors_diff

def check_classifiers_test_diff(y, models_folder):
    """
    Checks if all the sector and family in the test set can be predicted.

    Parameters
    ----------
    y : pd.DataFrame
        Labels.
    models_folder : String
        Path to models folder.

    Returns
    -------
    sectors_diff : List<String>
        List of sectors that are in the test set but cannot be predicted by the classifiers..
    families_diff : List<String>
        List of families that are in the test set but cannot be predicted by the classifiers..

    """
    sectors_diff = check_classifers_test_sector(y, models_folder)
    families_diff = check_classifers_test_family(y, models_folder)
    
    return sectors_diff, families_diff                                                 
    
def check_classifers_test_sector(y, models_folder):
    """
    Checks if all the sector in the test set can be predicted.

    Parameters
    ----------
    y : pd.DataFrame
        Labels.
    models_folder : String
        Path to models folder.

    Returns
    -------
    sectors_diff : List<String>
        List of sectors that are in the test set but cannot be predicted by the classifiers.

    """
    
    sectors = sorted(y[var.id_secteur].unique())

    sectors_diff = []
    for sector in sectors:
        joblib_path = models_folder + hashing(sector) + ".joblib"
        if not os.path.exists(joblib_path):
            sectors_diff.append(sector)
            
    return sectors_diff

def check_classifers_test_family(y, models_folder):
    """
    Checks if all the sector in the test set can be predicted.

    Parameters
    ----------
    y : pd.DataFrame
        Labels.
    models_folder : String
        Path to models folder.

    Returns
    -------
    sectors_diff : List<String>
        List of families that are in the test set but cannot be predicted by the classifiers.

    """
    
    sectors = sorted(y[var.id_secteur].unique())
    families = { }
    for sector in sectors:
        families[sector] = sorted(y[y[var.id_secteur] == sector][var.id_famille].unique())
        
    clfs_family = get_all_families_classifier(models_folder, sectors)

    families_diff = []
    for sector in sectors:
        if not clfs_family[sector]:
            for family in families[sector]:
                families_diff.append(family)
        else:
            families_pred = clfs_family[sector].classes_
            families_diff_res = [family if family not in families_pred else None for family in families[sector]]
            families_diff_res = list(filter(None, families_diff_res))
            families_diff += families_diff_res
            
    return families_diff