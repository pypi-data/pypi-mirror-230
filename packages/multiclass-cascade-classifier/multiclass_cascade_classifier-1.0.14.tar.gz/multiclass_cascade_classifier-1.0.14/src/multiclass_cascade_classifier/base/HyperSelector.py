"""
Module HyperParameters

HyperParameters selection related functions

@author: ThomasAujoux
"""



import yaml
import pandas as pd
from datetime import date
import os

from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
# from xgboost import XGBClassifier
from sklearn.model_selection import GridSearchCV

import multiclass_cascade_classifier.base.variables.Variables as var

classifiers = {
    var.SVM: SVC,
    var.RF: RandomForestClassifier,
    # var.XGBoost: XGBClassifier,
}



def read_clf_yaml(clf_yaml):
    """
    Reads the yaml content and initializes a classifier accordingly.

    Parameters
    ----------
    clf_yaml : Dict
        YAML content.
        {
            "type": type,
            "hyperparameters": {
                "param1": param1,
                "param2": param2,
                etc
            },
        }

    Raises
    ------
    ValueError
        If classifier type is unknown.

    Returns
    -------
    clf : Classifier
        Classifier initialized with the hyperparameters contained in clf_yaml.
        SVC or RandomForest.

    """
    # Type : SVM or RF
    clf_type = clf_yaml[var.classifierType]
    
    # Hyperparameters
    clf_hyperparams = clf_yaml[var.classifierHyperParams]
    
    # Classifier
    clf = classifiers[clf_type](**clf_hyperparams)
    
    if clf_type == var.SVM:
        clf.set_params(probability=var.probabilityValue)
    
    return clf

def write_clf_yaml(clf):
    """
    Returns the type and hyperparameters of clf into a dict

    Parameters
    ----------
    clf : Classifier (SVC or RandomForest)
        Classifier.

    Returns
    -------
    clf_dict : Dict
        {
            "type": type,
            "hyperparameters": {
                "param1": param1,
                "param2": param2,
                etc
            },
        }.

    """
    clf_type = [k for k, v in classifiers.items() if v == type(clf)]
    clf_type = clf_type[0]
    clf_hyperparams = clf.get_params()
    
    clf_dict = {
        var.classifierType: clf_type,
        var.classifierHyperParams: clf_hyperparams,
        }
    
    return clf_dict

def read_sector_hyperparams(yaml_sector_in):
    """
    Reads the yaml file containing the classifier's hyperparameters.
    Initialize the classifier.
    
    Classifier's type: SVM or RandomForest

    Parameters
    ----------
    yaml_sector_in : String
        Path to the yaml file.

    Raises
    ------
    TypeError
        Raised when the yaml file isn't in the right format.

    Returns
    -------
    clf_sector : Classifier
        Classifier initalized with the hyperparameters contained in the yaml file.

    """
    with open(yaml_sector_in) as f:
        # YAML content
        clf_yaml = yaml.load(f, Loader=yaml.FullLoader)
        
        # Classifier
        clf_sector = read_clf_yaml(clf_yaml)
        
        return clf_sector

def read_family_per_sector_hyperparams(yaml_families_in):
    """
    Reads the yaml file containing the classifiers' hyperparameters.
    Initialize the classifiers.
    
    Classifier's type: SVM or RandomForest

    Parameters
    ----------
    yaml_families_in : String
        File containing the type and hyperparameters of the classifiers.

    Returns
    -------
    clf_families : List
        Classifiers initialized with the hyperparameters contained in the yaml file.

    """
    
    clf_families = { }
    
    with open(yaml_families_in) as f:
        # YAML content
        clf_list_yaml = yaml.load(f, Loader=yaml.FullLoader)
        
        for clf_yaml in clf_list_yaml:
            sector = clf_yaml[var.secteur]
            clf_families[sector] = read_clf_yaml(clf_yaml)
        
    return clf_families

def get_sectors_from_family_yaml(yaml_families_in):
    """
    

    Parameters
    ----------
    yaml_families_in : String
        File containing the type and hyperparameters of the classifiers.

    Returns
    -------
    sectors : List<String>
        List of sectors in yaml.

    """
    
    sectors = []
    
    with open(yaml_families_in) as f:
        # YAML content
        clf_list_yaml = yaml.load(f, Loader=yaml.FullLoader)
        
        for clf_yaml in clf_list_yaml:
            sector = clf_yaml[var.secteur]
            sectors.append(sector)
            
    return sectors

def write_sector_hyperparam(yaml_sector_out, clf_sector, training_size=None):
    """
    Writes the type and the hyperparameters of the clf into a yaml file.

    Parameters
    ----------
    yaml_sector_out : String
        Path to yaml file.
    clf_sector : Classifier
        Classifier.

    Returns
    -------
    None.

    """
    
    clf_dict = write_clf_yaml(clf_sector)
    clf_dict[var.training_date] = date.today()
    clf_dict[var.training_size] = training_size if training_size else "NA"
        
    
    with open(yaml_sector_out, 'w') as file:
        yaml.dump(clf_dict, file)

def write_family_per_sector_hyperparams(yaml_families_out, clfs_families):
    """
    Writes the sector, the type and the hyperparameters of the clfs into a yaml file.

    Parameters
    ----------
    yaml_families_out : String
        Path to file where the list of classifiers and hyperparameters will be written.
    clfs_families : Dict
        Contains one classifier for eachs sector.
        {
            "sector 1": classifier 1,
            "sector 2": classifier 2,
        }

    Returns
    -------
    None.

    """
    clf_list_out = []
    
    for sector in clfs_families.keys():
        clf_dict = write_clf_yaml(clfs_families[sector])
        clf_dict[var.secteur] = sector
        clf_list_out.append(clf_dict)
    with open(yaml_families_out, 'w') as file:
        yaml.dump(clf_list_out, file)
        
def hyper_cross_val(X, y, n_jobs, logjournal=None):
    """
    Call the function selecting the best hyperparameters based on X and y.

    Parameters
    ----------
    X : pd.DataFrame
        Training set.
    y : pd.Series
        Labels.

    Returns
    -------
    clf_out : Classifier
        Classifier initialized with best hyperparameters (not trained).

    """
    clf_best = select_hyperparams(X, y, n_jobs)
    clf_type = clf_best[var.classifierType]
    clf_hyperparams = clf_best[var.classifierHyperParams]
    clf_out = classifiers[clf_type](**clf_hyperparams)
    if logjournal:
        logjournal.write_text("\t\t%s." % str(clf_type))
        logjournal.write_text("\t\t%s." % str(clf_hyperparams))
        logjournal.write_text("\t\t%s." % str(clf_best[var.classifierCVMean]))
    return clf_out

def hyper_cross_val_sector(X, y, n_jobs, logjournal=None):
    """
    Call the function selecting the best hyperparameters based on X and y.

    Parameters
    ----------
    X : pd.DataFrame
        Data set.
    y : pd.Series
        Labels.

    Returns
    -------
    clf_sector : TYPE
        DESCRIPTION.

    """
    if logjournal:
        logjournal.write_text("\tHyperparameters selection for sector classifier.")
    y_sector = y[var.id_secteur]
    clf_sector = hyper_cross_val(X, y_sector, n_jobs, logjournal)

    return clf_sector

def hyper_cross_val_family(X, y, n_jobs, logjournal=None):
    """
    Call the function selecting the best hyperparameters based on X and y.

    Parameters
    ----------
    X : pd.DataFrame
        Data set.
    y : pd.Series
        Labels.

    Returns
    -------
    clf_family : Classifier
        Classifier (not trained).

    """
    clf_family = hyper_cross_val(X, y, n_jobs, logjournal)
    return clf_family

def hyper_cross_val_family_per_sector(X, y, n_jobs, logjournal=None):
    """
    For each sector, select hyperparameters via cross validation.
    For each sector, only uses the features that appears in the products of this sector.

    Parameters
    ----------
    X : pd.DataFrame
        Train data set.
    y : pd.DataFrame
        Labels.

    Returns
    -------
    clfs_families : Dict
        {
            "sector 1": classifier 1,
            "sector 2": classifier 2,
        }.

    """
    clfs_families = { }
    
    sectors = sorted(y[var.id_secteur].unique())
    for sector in sectors:
        
        print(sector)
        if logjournal:
            logjournal.write_text("\t Hyperparameters for family classifier selection: %s." % sector)
        
        y_res = y[y[var.id_secteur] == sector][var.id_famille]
        X_res = X.loc[y_res.index]

        ## Retrieving only interesting features

        # Retrieving the text data
        X_res_txt = X_res[X_res.columns.to_list()[:-var.nb_bin_features]]
        X_res_txt = [row[:-var.nb_bin_features] for row in X_res.values.tolist()]
        X_res_txt = pd.DataFrame(X_res_txt, columns=X_res.columns.to_list()[:-var.nb_bin_features], index=X_res.index)


        # Removing columns with only zeros
        X_res_txt = X_res_txt.loc[:, (X_res_txt != 0).any(axis=0)]

        # Concatenation with binary data
        X_res_bin = [row[-var.nb_bin_features:] for row in X_res.values.tolist()]
        X_res_bin = pd.DataFrame(X_res_bin, columns=X_res.columns.to_list()[-var.nb_bin_features:], index=X_res.index)

        X_res_data = []
        for index, row in X_res_txt.iterrows():
            X_res_data.append(X_res_txt.loc[index].values.tolist() + X_res_bin.loc[index].values.tolist())
        X_res_vect = pd.DataFrame(X_res_data, columns=X_res_txt.columns.to_list() + X_res_bin.columns.to_list(), index=X_res.index)
        
        clf = hyper_cross_val_family(X_res_vect, y_res, n_jobs, logjournal)
        
        clfs_families[sector] = clf
    
    return clfs_families

def select_hyperparams(X, y, n_jobs=var.n_jobs, cv=var.cv, logjournal=None):
    """
    Select hyperparameters based on the data set X and the labels y.

    Parameters
    ----------
    X : pd.DataFrame
        Data set.
    y : pd.Series
        Labels.
    cv : Int, optional
        Number of split in the cross validation. The default is var.cv (5).

    Returns
    -------
    best_clf : Dict
        {
            var.classifierCVMean: score,
            var.classifierType: clf_type,
            var.classifierHyperParams: clf_hyperparams,
        }.

    """
    # GridSearch for SVM
    svm = SVC()
    clf_svm = GridSearchCV(svm, var.hyperParamsGrid[var.SVM], verbose=3, cv=cv, n_jobs=n_jobs)
    clf_svm.fit(X, y)
    
    # GridSearch for Random Forest
    rf = RandomForestClassifier()
    clf_rf = GridSearchCV(rf, var.hyperParamsGrid[var.RF], verbose=3, cv=cv, n_jobs=n_jobs)
    clf_rf.fit(X, y)

    # y_xgbc = pd.Series(y, dtype="category")
    # # GridSearch for XGBoost
    # xgbc = XGBClassifier()
    # clf_xgbc = GridSearchCV(xgbc, var.hyperParamsGrid[var.XGBoost], verbose=3, cv=cv, n_jobs=n_jobs)
    # clf_xgbc.fit(X, y_xgbc)
    
    # Comparing best classifiers for both SVM and RF
    # If SVM has a better score
    if clf_svm.best_score_ > clf_rf.best_score_:
        best_clf = {
            var.classifierCVMean: clf_svm.best_score_,
            var.classifierType: var.SVM,
            var.classifierHyperParams: clf_svm.best_params_,
        }
        best_clf[var.classifierHyperParams][var.probability] = var.probabilityValue
    # If RandomForest has a better score
    else:
        best_clf = {
            var.classifierCVMean: clf_rf.best_score_,
            var.classifierType: var.RF,
            var.classifierHyperParams: clf_rf.best_params_,
        }
    
    
    # Old code
    # hyperParams = { }
    # for clf_type in classifiers.keys():
    #     hyperParams[clf_type] = []
    #     classifier_combination = list(itertools.product(*var.hyperParamsGrid[clf_type].values()))
    #     for svm in classifier_combination:
    #         clf_hyperparams = dict(zip(list(var.hyperParamsGrid[clf_type].keys()), svm))
    #         hyperParams[clf_type].append(clf_hyperparams)
            
    # best_clf = None
    # for clf_type in classifiers.keys():
    #     for clf_hyperparams in hyperParams[clf_type]:
    #         clf = classifiers[clf_type](**clf_hyperparams)
    #         scores = cross_val_score(clf, X, y, cv=cv)
    #         score = scores.mean()
    #         if not best_clf:
    #             best_clf = {
    #                 var.classifierCVMean: score,
    #                 var.classifierType: clf_type,
    #                 var.classifierHyperParams: clf_hyperparams,
    #             }
    #         else:
    #             if best_clf[var.classifierCVMean] < score:
    #                 best_clf = {
    #                     var.classifierCVMean: score,
    #                     var.classifierType: clf_type,
    #                     var.classifierHyperParams: clf_hyperparams,
    #                 }
                
    return best_clf

def select_hyperparameters_sector(X, y, yaml_sector_in=None, n_jobs=var.n_jobs, logjournal=None):
    """
    Selects hyperparameters of the sector classifier.
    Either by using the ones stored inside the yaml file or by selecting new ones.

    Parameters
    ----------
    X : pd.DataFrame
        Data.
    y : pd.DataFrame
        Labels.
    yaml_sector_in : String, optional
        Path to yaml file. The default is None.
    n_jobs : Int, optional
        Number of jobs. The default is var.n_jobs.

    Returns
    -------
    clf : Classifier
        Initialized classifier (not trained).

    """
    
    # If there's a yaml file containing the hyperparameters
    # The alforithm reads it
    if yaml_sector_in:
        if logjournal:
            logjournal.write_text("Reading parameters for sector classifier in yaml file.")
        clf = read_sector_hyperparams(yaml_sector_in)
    # If not, it searches for new hyperparameters
    else:
        if logjournal:
            logjournal.write_text("Selecting parameters for sector classifier.")
        clf = hyper_cross_val_sector(X, y, n_jobs, logjournal)
       
    return clf

def select_hyperparameters_family(X, y, yaml_families_in=None, sectors_diff=None, n_jobs=var.n_jobs, logjournal=None):
    """
    Selects hyperparameters of the family classifiers.
    Either by using the ones stored inside the yaml file or by selecting new ones.

    Parameters
    ----------
    X : pd.DataFrame
        Data.
    y : pd.DataFrame
        Labels.
    yaml_families_in : String, optional
        DESCRIPTION. The default is None.
    sectors_diff : List<String>, optional
        List of sectors that aren't present in the yaml file. The default is None.
    n_jobs : Int, optional
        Number of jobs. The default is var.n_jobs.

    Returns
    -------
    clfs : Dict<Classifier>
        Initialized classifier (not trained).

    """
    
    # If there's a yaml file containing the hyperparameters
    # The alforithm reads it
    if yaml_families_in:
        if logjournal:
            logjournal.write_text("Reading parameters for family classifiers in yaml file.")
        clfs = read_family_per_sector_hyperparams(yaml_families_in)
        # If there are sectors that do not have a family classifier
        # It searches for new hyperparameters for those specific sectors
        if sectors_diff:
            if logjournal:
                logjournal.write_text("Some sectors need parameters selection for family classifier.")
            y_res = y[y[var.id_secteur].isin(sectors_diff)]
            X_res = X.loc[y_res.index]
            clfs_diff = hyper_cross_val_family_per_sector(X_res, y_res, n_jobs, logjournal)
            
            clfs.update(clfs_diff)
    # If not, it searches for new hyperparameters
    else:
        if logjournal:
            logjournal.write_text("Selecting parameters for family classifiers.")
        clfs = hyper_cross_val_family_per_sector(X, y, n_jobs, logjournal)
        
    return clfs
    
def get_training_date(models_folder):
    """
    Returns the training date stored in the sector yaml file.
    Returns None if training date cannot be retrieved.

    Parameters
    ----------
    models_folder : String
        Path to models folder.

    Returns
    -------
    training_date : String
        Training date.

    """
    
    # Path to sector classifier yaml file
    sector_yaml = models_folder + var.hyper_sector_yaml
    # Checking if the yaml file exists
    if os.path.exists(sector_yaml) and os.stat(sector_yaml).st_size > 0:
        with open(sector_yaml) as f:
            clf_sector = yaml.load(f, Loader=yaml.FullLoader)
            training_date = clf_sector[var.training_date]
            return training_date
    else:
        return None
        
def get_training_size(models_folder):
    """
    Returns the training size stored in the sector yaml file.
    Returns None if training size cannot be retrieved.

    Parameters
    ----------
    models_folder : String
        Path to models folder.

    Returns
    -------
    training_date : String
        Training size.

    """
    # Path to sector classifier yaml file
    sector_yaml = models_folder + var.hyper_sector_yaml
    # Checking if the yaml file exists
    if os.path.exists(sector_yaml) and os.stat(sector_yaml).st_size > 0:
        with open(sector_yaml) as f:
            clf_sector = yaml.load(f, Loader=yaml.FullLoader)
            training_size = clf_sector[var.training_size]
            return training_size
    else:
        return None