"""
Module Scripts

Scripts functions

Handles pd.DataFrame

@author: ThomasAujoux
"""



### Imports ###

from sklearn.model_selection import train_test_split

import time
import sys

import multiclass_cascade_classifier.base.variables.Variables as var

from multiclass_cascade_classifier.base.VariablesChecker import check_csv, check_yaml, check_folder, create_folder, check_yaml_sector, check_yaml_families
from multiclass_cascade_classifier.base.VariablesChecker import check_test_size, checks_nFamilies, check_trained_classifiers, check_classifiers_train_sectors, check_classifiers_test_diff
from multiclass_cascade_classifier.base.DataHelper import get_dataframe
from multiclass_cascade_classifier.base.PreProcessing import PreProcessing

from multiclass_cascade_classifier.base.DataFrameNormalizer import DataFrameNormalizer
from multiclass_cascade_classifier.base.DataVectorizer import DataVectorizer

from multiclass_cascade_classifier.base.HyperSelector import select_hyperparameters_sector, select_hyperparameters_family
from multiclass_cascade_classifier.base.DataTrainer import train_sector_classifier, train_families_per_sector_classifier
from multiclass_cascade_classifier.base.HyperSelector import write_sector_hyperparam, write_family_per_sector_hyperparams
from multiclass_cascade_classifier.base.ClassifierHelper import save_sector_classifier, save_all_family_classifier
from multiclass_cascade_classifier.base.DataPredicter import predict_sectors, predict_families_per_sector_classifier

from multiclass_cascade_classifier.base.MetricsGenerator import generate_general_stats
from multiclass_cascade_classifier.base.MetricsGenerator import generate_confusion_matrix_sector, generate_confusion_matrixes_family
from multiclass_cascade_classifier.base.MetricsGenerator import generate_classification_report_sector, generate_classification_reports_family



### Check functions ###

def check_split(csv_in, csv_out_train, csv_out_test, test_size):
    """
    Checks if the arguments given by the user for the split are valid.

    Parameters
    ----------
    csv_in : String
        Path to the file that contains the data set.
    csv_out_train : String
        Path to the file that contains the train set.
    csv_out_test : String
        Path to the file that contains the test set.
    test_size : Float
        Size of test set.

    Returns
    -------
    csv_in : String
        Updated path to the file that contains the data set.
    csv_out_train : String
        Updated path to the file that contains the train set.
    csv_out_test : String
        Updated path to the file that contains the test set.
    test_size : Float
        Updated size of test set.

    """
    print("Initialization...")
    csv_in = check_csv(csv_in, True)
    csv_out_train = check_csv(csv_out_train, False)
    csv_out_test = check_csv(csv_out_test, False)
    test_size = check_test_size(test_size)
    
    return csv_in, csv_out_train, csv_out_test, test_size


def check_train(csv_train_in, models_folder, hyper_sector_file, hyper_family_per_sector_file, log_folder):
    """
    Checks if the arguments given by the user for the training are valid.

    Parameters
    ----------
    csv_train_in : String
        Path to the file that contains the train data set.
    models_folder : String
        Path to the folder that will contain the trained classifiers and the selected hyperparameters.
    hyper_sector_file : String
        Path to the file that contains the hyperparameters for the sector classifier.
    hyper_family_per_sector_file : String
        Path to the file that contains the hyperparameters for the family classifiers.

    Returns
    -------
    csv_train_in : String
        Updated path to the file that contains the train data set.
    models_folder : String
        Updated path to the folder that will contain the trained classifiers and the selected hyperparameters.
    hyper_sector_file : String
        Updated path to the file that contains the hyperparameters for the sector classifier.
    hyper_family_per_sector_file : String
        Updated path to the file that contains the hyperparameters for the family classifiers.

    """
    print("Initialization...")
    csv_train_in = check_csv(csv_train_in, True)
    models_folder = create_folder(models_folder)
    if log_folder:
        log_folder = create_folder(log_folder)
    hyper_sector_file = check_yaml(hyper_sector_file, False)
    hyper_family_per_sector_file = check_yaml(hyper_family_per_sector_file, False)
    hyper_sector_file = check_yaml_sector(hyper_sector_file)
    hyper_family_per_sector_file = check_yaml_families(hyper_family_per_sector_file)
    
    return csv_train_in, models_folder, hyper_sector_file, hyper_family_per_sector_file, log_folder


def check_test(csv_test_in, models_folder, metrics_folder, n_families):
    """
    Checks if the arguments given by the user for the testing are valid.

    Parameters
    ----------
    csv_test_in : String
        Path to the file that contains the test data set.
    models_folder : String
        Path to the folder that contains the trained classifiers.
    metrics_folder : String
        Path to the folder that will contain the generated statistics.
    n_families : Int
        Number of families to predict.

    Returns
    -------
    csv_test_in : String
        Updated path to the file that contains the test data set.
    models_folder : String
        Updated path to the folder that contains the trained classifiers.
    metrics_folder : String
        Updated path to the folder that will contain the generated statistics.
    n_families : Int
        Updated number of families to predict.

    """
    print("Initialization...")
    csv_test_in = check_csv(csv_test_in, True)
    models_folder = check_folder(models_folder)
    metrics_folder = create_folder(metrics_folder)
    models_folder = check_trained_classifiers(models_folder)
    n_families = checks_nFamilies(n_families)
    
    return csv_test_in, models_folder, metrics_folder, n_families


def check_predict(csv_predict_in, models_folder, csv_predict_out, n_families):
    """
    Checks if the arguments given by the user for the predicting are valid.

    Parameters
    ----------
    csv_predict_in : String
        Path to the file that contains the prediction data set.
    models_folder : String
        Path to the folder that contains the trained classifiers.
    csv_predict_out : String
        Path to the file that will contain the predicted data set.
    n_families : Int
        Number of families to predict.

    Returns
    -------
    csv_predict_in : String
        Updated path to the file that contains the prediction data set.
    models_folder : String
        Updated path to the folder that contains the trained classifiers.
    csv_predict_out : String
        Updated path to the file that will contain the predicted data set.
    n_families : Int
        Updated number of families to predict.

    """
    print("Initialization...")
    csv_predict_in = check_csv(csv_predict_in, True)
    models_folder = check_folder(models_folder)
    csv_predict_out = check_csv(csv_predict_out, False)
    models_folder = check_trained_classifiers(models_folder)
    n_families = checks_nFamilies(n_families)
    
    return csv_predict_in, models_folder, csv_predict_out, n_families

def check_predict_minus_out(csv_predict_in, models_folder, n_families):
    """
    Checks if the arguments given by the user for the predicting are valid.

    Parameters
    ----------
    csv_predict_in : String
        Path to the file that contains the prediction data set.
    models_folder : String
        Path to the folder that contains the trained classifiers.
    csv_predict_out : String
        Path to the file that will contain the predicted data set.
    n_families : Int
        Number of families to predict.

    Returns
    -------
    csv_predict_in : String
        Updated path to the file that contains the prediction data set.
    models_folder : String
        Updated path to the folder that contains the trained classifiers.
    csv_predict_out : String
        Updated path to the file that will contain the predicted data set.
    n_families : Int
        Updated number of families to predict.

    """
    csv_predict_in = check_csv(csv_predict_in, True)
    models_folder = check_folder(models_folder)
    models_folder = check_trained_classifiers(models_folder)
    n_families = checks_nFamilies(n_families)
    
    return csv_predict_in, models_folder, n_families


def check_classifiers_train(y, hyper_family_per_sector_file, force):
    """
    Checks yaml for training.

    Parameters
    ----------
    y : pd.DataFrame
        Labels.
    hyper_family_per_sector_file : String
        Path to yaml file containing hyperparameters.
    force : Boolean
        If True, forces training when a sector is missing from the yaml file (it will select the hyperparamters for this sector).

    Returns
    -------
    sectors_diff : List<String>
        List of sectors that are missing from the yaml file.

    """
    if hyper_family_per_sector_file:
        sectors_diff = check_classifiers_train_sectors(y, hyper_family_per_sector_file)
        
        if sectors_diff:
            print("Warning: Some sectors aren't present inside the hyperparameters yaml file for the family classification: %s" % str(sectors_diff))
            if not force:
                print("Use option --force to force training.")
                sys.exit("Exit")
        
        return sectors_diff


def check_classifiers_test(y, models_folder, force):
    """
    Checks if all labels in test set can be predicted.

    Parameters
    ----------
    y : pd.DataFrame
        Labels.
    models_folder : String
        Path to models folder.
    force : Boolean
        If True, forces testing when some labels cannot be predicted.

    Returns
    -------
    sectors_diff : List<String>
        List of sectors that cannot be predicted.
    families_diff : List<String>
        List of families that cannot be predicted.

    """
    sectors_diff, families_diff = check_classifiers_test_diff(y, models_folder)
    
    if sectors_diff:
        print("Warning: Some sectors cannot be predicted : %s" % str(sectors_diff))
            
    if families_diff:
        print("Warning: Some families cannot be predicted : %s" % str(families_diff))
            
    if not force and not (sectors_diff and families_diff):
        print("Use option --force to force testing.")
        sys.exit("Exit")
        
    return sectors_diff, families_diff

### data ###

def load_data(csv_in, index_column=None, columns=None, logjournal=None):
    """
    Load raw data

    Parameters
    ----------
    csv_in : String
        Path to data file (csv).
    index_column : List<String>, optional
        Index columns of DataFrame. The default is var.column_index.
    columns : List<String>, optional
        Columns of DataFrame. The default is var.columns.

    Returns
    -------
    df_produit : pd.DataFrame
        Données.

    """

    if logjournal:
        logjournal.write_text("Loading data.")
    
    df_produit = get_dataframe(csv_in)

    if index_column:
        if any(item in df_produit.columns.tolist() for item in index_column):
            df_produit.set_index(index_column, inplace=True)
        else:
            if len(index_column) == 1:
                df_produit[index_column] = df_produit.index
            else:
                index = df_produit.index.tolist()
                index_values = [[i for j in index_column] for i in index]
                df_produit[index_column] = index_values
            df_produit.set_index(index_column, inplace=True)
    
    if columns:
        df_produit = df_produit[columns]
        
    return df_produit


def save_data(csv_out, df_produit, logjournal=None):
    """
    Saves the DataFrame into csv_out.

    Parameters
    ----------
    csv_out : String
        Path to data file (csv) where the data will be saved.
    df_produit : pd.DataFrame
        Data to save.

    Returns
    -------
    None.

    """

    if logjournal:
        logjournal.write_text("Saving data.")
    
    df_produit.to_csv(csv_out, index=True, sep=';')

def prepro(df_data, logjournal):
    """
    Prepares data.
    Pretreatment and vectorization

    Parameters
    ----------
    df_data : pd.DataFrame
        Data set.

    Returns
    -------
    X_vect : pd.DataFrame
        Pretreated and vectorized data set.

    """
    
    # Pre-Processing
    print("PreProcessing...")
    if logjournal:
        logjournal.write_text("PreProcessing.")
    start_time = time.time()
    df_preprocessing=PreProcessing(columns_text=var.columns_text_pre)
    df_produit = df_preprocessing.fit_transform(df_data)
    preprocessing_time = var.time_ % (divmod(time.time() - start_time, 60))
    print(preprocessing_time)
    
    return df_produit

def prepare_data(df_data, logjournal):
    """
    Prepares data.
    Pretreatment and vectorization

    Parameters
    ----------
    df_data : pd.DataFrame
        Data set.

    Returns
    -------
    X_vect : pd.DataFrame
        Pretreated and vectorized data set.

    """
    
    # Pre-treatment
    print("Pretreatment...")
    if logjournal:
        logjournal.write_text("Pretreatment.")
    start_time = time.time()
    df_normalizer=DataFrameNormalizer(lowercase=var.lowercase, removestopwords=var.removestopwords, removedigit=var.removedigit, getstemmer=var.getstemmer, getlemmatisation=var.getlemmatisation, columns_text=var.columns_text, columns_binary=var.columns_bin, columns_frozen=var.columns_frozen)
    X_train = df_normalizer.fit_transform(df_data)
    pretreatment_time = var.time_ % (divmod(time.time() - start_time, 60))
    print(pretreatment_time)
    
    ## Vectorization
    print("Vectorization...")
    if logjournal:
        logjournal.write_text("Vectorization.")
    start_time = time.time()
    df_vectorizer = DataVectorizer(columns_text=var.columns_text, columns_binary=var.columns_bin)
    X_vect = df_vectorizer.fit_transform(X_train)
    vectorization_time = var.time_ % (divmod(time.time() - start_time, 60))
    print(vectorization_time)
    
    return X_vect

### Split ###

def split_train_test(df_produit, test_size):
    """
    Splits data from csv_in into a training set and a test set with size of test set being predict_size%

    Parameters
    ----------
    df_produit : pandas.DataFrame
        Data.
    predict_size : Float
        Size of test set.

    Returns
    -------
    X_train : pd.DataFrame
        Train set.
    X_test : pd.DataFrame
        Test set.

    """
    
    X = df_produit[var.columns_X_id]
    y = df_produit[var.id_famille]
    
    ## Splitting
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=42)
    
    ## Retrieving indexes
    # Train
    index_train = X_train.index.to_list()
    # Test
    index_test = X_test.index.to_list()
    
    ## Concatenating train and test
    # Train
    X_train[var.id_famille] = y_train
    # Test
    X_test[var.id_famille] = y_test
    
    # Retrieving other columns
    columns_rest = []
    for column in var.columns_all:
        if column not in X_train.columns.values.ravel():
            columns_rest.append(column)
        
    X_train[columns_rest] = df_produit.loc[index_train][columns_rest]
    X_test[columns_rest] = df_produit.loc[index_test][columns_rest]
    
    return X_train, X_test

### Modele ###

def select_hyperparameters(X, y, hyper_sector_file=None, hyper_family_per_sector_file=None, sectors_diff=None, n_jobs=var.n_jobs, logjournal=None):
    """
    Selects hyperparameters (or load them if yaml files are filled).

    Parameters
    ----------
    X : pd.DataFrame
        Data train set.
    y : pd.DataFrame
        Labels of data trained set.
    hyper_sector_file : String, optional
        Path to yaml file that contains the sector classifier's hyperparameters. The default is None.
    hyper_family_per_sector_file : String, optional
        Path to yaml file that contains the family classifiers' hyperparameters. The default is None.
    sectors_diff : List<String>, optional
        List of sectors that don't have their hyperparameters filled in the yaml file. The default is None.
    n_jobs : Integer, optional
        Number of jobs created during cross-validation (hyperparameters selection). The default is var.n_jobs.

    Returns
    -------
    clf_sector : Classifier
        Initialized sector classifier.
    clfs_family : Dict<Classifier>
        Initialiazed family classifiers.

    """
    
    print("Hyperparameters selection...")
    if logjournal:
        logjournal.write_text("Hyperparameters selection.")
    
    ## Sector
    print("Sectors...")
    if logjournal:
        logjournal.write_text("\tHyperparameters selection: dectors")
    start_time = time.time()
    clf_sector = select_hyperparameters_sector(X, y, hyper_sector_file, n_jobs, logjournal)
    sector_selection_time = var.time_ % (divmod(time.time() - start_time, 60))
    print(sector_selection_time)

    ## Families
    print("Families...")
    if logjournal:
        logjournal.write_text("\tHyperparameters selection: families")
    start_time = time.time()
    clfs_family = select_hyperparameters_family(X, y, hyper_family_per_sector_file, sectors_diff, n_jobs, logjournal)
    family_selection_time = var.time_ % (divmod(time.time() - start_time, 60))
    print(family_selection_time)
    
    return clf_sector, clfs_family

def train_data(X, y, clf_sector, clfs_family, logjournal=None):
    """
    Trains classifiers on train set.

    Parameters
    ----------
    X : pd.DataFrame
        Data train set.
    y : pd.DataFrame
        Labels of data trained set.
    clf_sector : Classifier
        Initialized sector classifier.
    clfs_family : Dict<Classifier>
        Initialiazed family classifiers.

    Returns
    -------
    clf_sector_trained : Classifier
        Trained sector classifier.
    clfs_family_trained : Dict<Classifier>
        Trained family classifiers.

    """
    
    print("Training...")
    if logjournal:
        logjournal.write_text("Training")
    
    ## Sector
    print("Sectors...")
    if logjournal:
        logjournal.write_text("\tTraining: sectors")
    start_time = time.time()
    clf_sector_trained = train_sector_classifier(X, y, clf_sector, logjournal)
    sector_training_time = var.time_ % (divmod(time.time() - start_time, 60))
    print(sector_training_time)
    
    ## Families
    print("Families...")
    if logjournal:
        logjournal.write_text("\tTraining: families")
    start_time = time.time()
    clfs_family_trained = train_families_per_sector_classifier(X, y, clfs_family, logjournal)
    family_training_time = var.time_ % (divmod(time.time() - start_time, 60))
    print(family_training_time)
    
    return clf_sector_trained, clfs_family_trained

def save_hyperparameters(models_folder, clf_sector, clfs_family, training_size, logjournal=None):
    """
    Save selected hyperparameters into yaml files.

    Parameters
    ----------
    models_folder : String
        Path to models folder.
    clf_sector : Classifier
        Initialiazed sector classifier.
    clfs_family : Dict<Classifier>
        Initialiazed family classifiers
    training_size : Integer
        Number of products in training data set.

    Returns
    -------
    None.

    """

    if logjournal:
        logjournal.write_text("Saving hyperparameters files (yaml)")

    yaml_sector_out = models_folder + var.hyper_sector_yaml
    yaml_families_out = models_folder + var.hyper_families_yaml
    
    write_sector_hyperparam(yaml_sector_out, clf_sector, training_size)
    write_family_per_sector_hyperparams(yaml_families_out, clfs_family)

def save_classifiers(models_folder, clf_sector, clfs_family, logjournal=None):
    """
    Saves trained classifiers into models folder.

    Parameters
    ----------
    models_folder : String
        Path to models folder.
    clf_sector : Classifier
        Trained sector classifier.
    clfs_family : Dict<Classifier>
        Trained family classifiers

    Returns
    -------
    None.

    """
    
    if logjournal:
        logjournal.write_text("Saving classifiers")

    save_sector_classifier(clf_sector, models_folder)
    save_all_family_classifier(clfs_family, models_folder)

def test_data(X_test, y_test, models_folder, n_families):
    """
    Tests classifiers in models_folder on data test set.

    Parameters
    ----------
    X_test : pd.DataFrame
        Test set.
    y_test : pd.DataFrame
        Labels of test set.
    models_folder : String
        Path to models folder.
    n_families : Integer
        Number of family to predict.

    Returns
    -------
    df_tested : pd.DataFrame
        Data test set with predicted labels.

    """
    
    ## Testing
    print("Testing...")
    
    # Sector
    print("Sectors...")
    start_time = time.time()
    y_sector_pred = predict_sectors(X_test, models_folder)
    print(y_sector_pred)
    sector_testing_time = var.time_ % (divmod(time.time() - start_time, 60))
    
    print("Families...")
    start_time = time.time()
    df_tested = predict_families_per_sector_classifier(X_test, y_sector_pred, models_folder, n_families)
    family_testing_time = var.time_ % (divmod(time.time() - start_time, 60))
    print(family_testing_time)
    
    # Concatenation with true values
    print("Concatenation...")
    start_time = time.time()
    df_tested.insert(0, var.id_secteur, y_test[var.id_secteur])
    df_tested.insert(3, var.id_famille, y_test[var.id_famille])
    df_tested.insert(3, "%s %s" % (var.comparaison, var.secteur), df_tested["%s %s" % (var.prediction, var.secteur)] == y_test[var.id_secteur])
    for n in range(1, n_families + 1):
        res = []
        for index, row in df_tested.iterrows():
            if row["%s %s %i" % (var.prediction, var.famille,  n)]:
                res.append(y_test[var.id_famille].loc[index] in row["%s %s %i" % (var.prediction, var.famille,  n)].split(","))
            else:
                res.append(None)
        df_tested.insert(7 + 2 * (n - 1), "%s %i" % (var.comparaison, n), res)
    concatenation_time = var.time_ % (divmod(time.time() - start_time, 60))
    print(concatenation_time)
    
    
    return df_tested

def test_metrics(df_pred, metrics_folder, n_families):
    """
    Generates metrics for data test set and its predicted labels.
    Saves metrics into a metrics folder.
    
    WARNING: No matter the number of predicted families, it will generate metrics for the first one.

    Parameters
    ----------
    df_pred : pd.DataFrame
        Predicted data set.
    metrics_folder : String
        Path to metrics folder.
    n_families : Integer
        Number of predicted families.

    Returns
    -------
    None.

    """
    
    if n_families:
        df_pred = df_pred.rename(columns={
            "%s %s" % (var.prediction, var.secteur): var.predicted_secteur,
            "%s %s %d" % (var.prediction, var.famille, 1): var.predicted_famille,
            })
        y_pred = df_pred[var.columns_label_all]
            
    else:
        y_pred = df_pred[var.columns_label_all]
        
    # General stats
    generate_general_stats(df_pred, metrics_folder)
    
    # Confusion matrixes
    generate_confusion_matrix_sector(y_pred, metrics_folder)
    generate_confusion_matrixes_family(y_pred, metrics_folder)
    
    # Classification reports
    generate_classification_report_sector(y_pred, metrics_folder)
    generate_classification_reports_family(y_pred, metrics_folder)

def predict_data(X_pred, models_folder, n_families):
    """
    Predicts labels of data set.

    Parameters
    ----------
    X_pred : pd.DataFrame
        Data set.
    models_folder : String
        Path to model folder.
    n_families : Integer
        Number of families to predict.

    Returns
    -------
    df_predicted : pd.DataFrame
        Data set and its predicted labels.

    """
    
    ## Testing
    print("Predicting...")
    
    # Sector
    print("Sectors...")
    start_time = time.time()
    y_sector_pred = predict_sectors(X_pred, models_folder)
    sector_predicting_time = var.time_ % (divmod(time.time() - start_time, 60))
    print(sector_predicting_time)
    
    print("Families...")
    start_time = time.time()
    df_predicted = predict_families_per_sector_classifier(X_pred, y_sector_pred, models_folder, n_families)
    family_predicting_time = var.time_ % (divmod(time.time() - start_time, 60))
    print(family_predicting_time)
    
    return df_predicted

def add_flags(X, n_families):
    """
    Adds flags to warn the user (based on probability)

    Parameters
    ----------
    X : pd.DataFrame
        Data set and its predicted labels (and probas !).
    n_families : Integer
        Number of predicted families.

    Returns
    -------
    X : pd.DataFrame
        Data set + flags.

    """
    
    X[var.proba] = [float(proba) for proba in X[var.proba].tolist()]
    X["%s %i" % (var.proba, 1)] = [float(proba) for proba in X["%s %i" % (var.proba, 1)].tolist()]
        
    sector_alert = X[var.proba] < var.sector_threshold
    X["%s %s" % (var.secteur, var.alert)] = ""
    X.loc[sector_alert, "%s %s" % (var.secteur, var.alert)] = "A verifier"
    family_alert = X["%s %i" % (var.proba, 1)] < var.family_threshold
    X["%s %s" % (var.famille, var.alert)] = ""
    X.loc[family_alert, "%s %s" % (var.famille, var.alert)] = "A verifier"

    return X