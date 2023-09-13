"""
Module Skeleton

Skeleton functions

Handles CSV files

@author: ThomasAujoux
"""



### Imports ###
import pandas as pd

import multiclass_cascade_classifier.base.variables.Variables as var
from multiclass_cascade_classifier.Scripts import check_split, check_train, check_test, check_predict, check_classifiers_train, check_classifiers_test
from multiclass_cascade_classifier.Scripts import load_data, prepare_data, save_data, save_classifiers
from multiclass_cascade_classifier.Scripts import prepro
from multiclass_cascade_classifier.Scripts import select_hyperparameters, save_hyperparameters
from multiclass_cascade_classifier.Scripts import split_train_test, train_data, test_data, test_metrics, predict_data, add_flags

from multiclass_cascade_classifier.base.LogJournal import LogJournal

from warnings import simplefilter
simplefilter(action="ignore", category=pd.errors.PerformanceWarning)



### Split ###

def split(csv_in, csv_out_train="train_split.csv", csv_out_test="test_split.csv", test_size=0.20):
    """
    Splits data from csv_in into a training set and a test set with size of test set being test_size%
    Saves the new sets at train_out and test_out.

    Parameters
    ----------
    csv_in : String
        File where raw data are stored.
    test_size : Int, optional
        Size of the test set. The default is 80%.
    csv_out_train : String, optional
        File where the training set will be stored. The default is "train_split.csv".
    csv_out_test : String, optional
        File where the test set will be stored. The default is "test_split.csv".

    Returns
    -------
    None.

    """

    ## Checking variables
    csv_in, csv_out_train, csv_out_test, test_size = check_split(csv_in, csv_out_train, csv_out_test, test_size)
    
    ## Loading data
    df_produit = load_data(csv_in, index_column=None, columns=var.columns, logjournal=None)
    df_produit = prepro(df_produit, logjournal=None)
    X_train, X_test = split_train_test(df_produit, test_size)
    print(X_train.head(), X_test.head())
    # Saving data sets
    save_data(csv_out_train, X_train)
    save_data(csv_out_test, X_test)

################## Tests ####################
# csv_in = "./data2/merged_final.csv"
# split(csv_in)
################## Tests ####################

### Modele ###

def train(csv_train_in, models_folder, hyper_sector_file=None, hyper_family_per_sector_file=None, force=True, n_jobs=var.n_jobs, log_folder=None):
    """
    Trains classifiers on data train set (csv_train_in) and saves trained classifier into models_folder.

    Parameters
    ----------
    csv_train_in : String
        Path to data train set.
    models_folder : String
        Path to models folder (where the joblib files will be saved).
    hyper_sector_file : String, optional
        Path to yaml file where the hyperparameters for the sector classifier are stored. The default is None.
    hyper_family_per_sector_file : String, optional
        Path to yaml file where the hyperparameters for the family classifier are stored. The default is None.

    Returns
    -------
    None.

    """

    ## Checking variables
    csv_train_in, models_folder, hyper_sector_file, hyper_family_per_sector_file, log_folder = check_train(csv_train_in, models_folder, hyper_sector_file, hyper_family_per_sector_file, log_folder)
    # Log Journal
    log_journal = LogJournal(log_folder, "log") if log_folder else None

    if log_journal:
        log_journal.write_texts([
            "%s: %s" % (v_i, str(v_j)) for v_i, v_j in [
                ("csv_train_in", csv_train_in),
                ("models_folder", models_folder),
                ("hyper_sector_file", hyper_sector_file),
                ("hyper_family_per_sector_file", hyper_family_per_sector_file),
                ("log_folder", log_folder),
                ("n_jobs", n_jobs),
                ("force", force),
                ("var.hyperParamsGrid", var.hyperParamsGrid),
            ]
        ])

    ## Loading data
    df_train = load_data(csv_train_in, index_column=None, columns=var.columns, logjournal=log_folder)
    training_size = df_train.shape[0]
    ## Preparing data
    y_train = df_train[var.columns_label]
    sectors_diff = check_classifiers_train(y_train, hyper_family_per_sector_file, force)
    X_train = prepare_data(df_train, log_journal)
    print(X_train)
    print(y_train)
    ## Select hyperparameters
    clf_sector, clfs_family = select_hyperparameters(X_train, y_train, hyper_sector_file, hyper_family_per_sector_file, sectors_diff, n_jobs, log_journal)
    save_hyperparameters(models_folder, clf_sector, clfs_family, training_size, log_journal)
    
    ## Train Data
    clf_sector_trained, clfs_family_trained = train_data(X_train, y_train, clf_sector, clfs_family, log_journal)
    save_classifiers(models_folder, clf_sector_trained, clfs_family_trained, log_journal)

    if log_journal:
        log_journal.close()

################## Tests ####################
# csv_train_in = "./train_test/train_split.csv"
# models_folder = "./models"
# hyper_sector_file = "./hyper/hyper_sector.yaml"
# hyper_family_per_sector_file = "./hyper/hyper_family.yaml"
# hyper_sector_file = None
# hyper_family_per_sector_file = None
# train(csv_train_in, models_folder, hyper_sector_file, hyper_family_per_sector_file, force=True, n_jobs=var.n_jobs, log_folder=None)
################## Tests ####################

def test(csv_test_in, models_folder, metrics_folder, n_families=None, force=True):
    """
    Tests classifiers on data test set (csv_test_in) and saves metrics into metrics_folder.

    Parameters
    ----------
    csv_test_in : String
        Path to data test set.
    models_folder : String
        Path to models folder (where the joblib files are saved).
    metrics_folder : String
        Path to metrics folder (where the metrics files will be saved).
    n_families : Integer, optional
        Number of families to predict. The default is None.
    force : Boolean, optional
        If True, continues if there are labels in the data set that cannot be predicted. The default is True.

    Returns
    -------
    None.

    """
    
    ## Checking variables
    csv_test_in, models_folder, metrics_folder, n_families = check_test(csv_test_in, models_folder, metrics_folder, n_families)
    
    ## Loading data
    df_test = load_data(csv_test_in, index_column=None, columns=var.columns)

    # Log Journal
    log_journal = None

    ## Preparing data
    y_test = df_test[var.columns_label]
    sectors_diff, families_diff = check_classifiers_test(y_test, models_folder, force)
    # Log Journal
    log_journal = None
    X_test = prepare_data(df_test, log_journal)
    
    
    df_tested = test_data(X_test, y_test, models_folder, n_families)
    for c_index in range(len(var.columns_X)):
        df_tested.insert(c_index, var.columns_X[c_index], df_test[var.columns_X[c_index]])

    test_metrics(df_tested, metrics_folder, n_families)
    
    # Saving data
    csv_predict_out = metrics_folder + "predictions.csv"
    save_data(csv_predict_out, df_tested)

################## Tests ####################
# csv_test_in = "./train_test/test_split.csv"
# models_folder = "./models"
# metrics_folder = "./metrics"
# n_families = 3 # Question quoi mettre ici ????
# test(csv_test_in, models_folder, metrics_folder, n_families, force=True)
################## Tests ####################

def predict(csv_predict_in, models_folder, csv_predict_out, n_families=None):
    """
    Predicts families and sectors of test set.

    Parameters
    ----------
    csv_predict_in : String
        Path to data prediction set.
    models_folder : String
        Path to models folder (where the joblib files are saved).
    csv_predict_out : String
        Path to data predicted set (where it will be saved).
    n_families : Boolean, optional
        If True, continues if there are labels in the data set that cannot be predicted. The default is True.

    Returns
    -------
    None.

    """
    
    ## Checking variables
    csv_predict_in, models_folder, csv_predict_out, n_families = check_predict(csv_predict_in, models_folder, csv_predict_out, n_families)
    
    # Loading data
    df_pred = load_data(csv_predict_in, index_column=var.column_index, columns=var.columns_all)
    
    X_pred = prepare_data(df_pred, logjournal=False)
    
    # Predi
    df_predicted = predict_data(X_pred, models_folder, n_families)
    
    for c_index in range(len(var.columns_X)):
        df_predicted.insert(c_index, var.columns_X[c_index], df_pred[var.columns_X[c_index]])
        
    add_flags(df_predicted, n_families)
    
    # Saving data
    save_data(csv_predict_out, df_predicted)

################## Tests ####################
# csv_predict_in = "./train_test/test_split.csv"
# models_folder = "./models"
# csv_predict_out = "./predict_out/predict_out.csv"
# #n_families = 3 # Question quoi mettre ici ????
# predict(csv_predict_in, models_folder, csv_predict_out, n_families=True)
################## Tests ####################