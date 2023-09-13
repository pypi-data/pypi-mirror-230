"""
MetricsGenerator

Data testing related functions

@author: ThomasAujoux
"""


import pandas as pd

from sklearn.metrics import confusion_matrix
from sklearn.metrics import classification_report
from sklearn import metrics

import multiclass_cascade_classifier.base.variables.Variables as var
from multiclass_cascade_classifier.base.LogJournal import LogJournal




def generate_general_stats(df_pred, metrics_folder):
    """
    Generates general stats and saves them in a log journal in a metrics folder.

    Parameters
    ----------
    df_pred : pd.DataFrame
        True and predicted labels.
    metrics_folder : String
        Path to metrics folder.

    Returns
    -------
    None.

    """
    
    ## Opening the log journal (text file)
    log_journal = LogJournal(metrics_folder, "general_stats")

    log_journal.write_text("-- General stats --")
    
    y_true_sector = df_pred[var.id_secteur]
    y_pred_sector = df_pred[var.predicted_secteur]
    y_true_family = df_pred[var.id_famille]
    y_pred_family = df_pred[var.predicted_famille]
    
    ## Accuracy for sectors prediction
    log_journal.write_text("accuracy sector: %f" % metrics.accuracy_score(y_true_sector, y_pred_sector))
    ## Accuracy for families prediction
    log_journal.write_text("accuracy family: %f" % metrics.accuracy_score(y_true_family, y_pred_family))
    
    log_journal.close()

def generate_confusion_matrix_sector(df_pred, metrics_folder):
    """
    Generates confusion matrix for sector prediction and saves it into a metrics folder.

    Parameters
    ----------
    df_pred : pd.DataFrame
        True and predicted labels.
    metrics_folder : String
        Path to metrics folder.

    Returns
    -------
    None.

    """
    
    # Predicted labels
    y_pred_sector = df_pred[var.predicted_secteur]
    # True labels
    y_true_sector = df_pred[var.id_secteur]
    
    # Confusion matrix
    matrix = confusion_matrix(y_true=y_true_sector, y_pred=y_pred_sector)
    df_matrix = pd.DataFrame(matrix, columns=sorted(y_pred_sector.unique()))
    df_matrix[var.id_secteur] = sorted(y_pred_sector.unique())
    df_matrix.set_index(var.id_secteur, inplace=True)
    
    # Saving matrix
    df_matrix.to_excel(metrics_folder + var.confusion_matrix_sector, index=True, sheet_name=var.confusion_matrix)

def generate_confusion_matrixes_family(y_pred, metrics_folder):
    """
    Generates confusion matrixes for family predictions and saves them into a metrics folder.

    Parameters
    ----------
    y_pred : pd.DataFrame
        True and predicted labels.
    metrics_folder : String
        Path to metrics folder.

    Returns
    -------
    None.

    """
    
    y_pred_sector = y_pred[var.predicted_secteur]
    y_true_sector = y_pred[var.id_secteur]
    nb_sectors = len(y_true_sector.unique())
    y_pred_family = y_pred[var.predicted_famille]
    y_true_family = y_pred[var.id_famille]
    
    sectors = sorted(y_pred[var.predicted_secteur].unique())
    with pd.ExcelWriter(metrics_folder + var.confusion_matrix_family) as writer_confusion_matrix:
        for sector in sectors:
            
            y_res_pred_famille = y_pred_family[y_pred_sector == sector]
            res_index = y_res_pred_famille.index
            y_res_pred_sector = y_pred_sector.loc[res_index]
            y_res_true_sector = y_true_sector.loc[res_index]
            
            index_matrix = y_res_pred_famille[y_res_true_sector == y_res_pred_sector].index
            y_true_matrix = y_true_family.loc[index_matrix]
            y_pred_matrix = y_res_pred_famille.loc[index_matrix]

            matrix = confusion_matrix(y_true=y_true_matrix, y_pred=y_pred_matrix)
            
            display_labels = y_true_matrix.unique().tolist() + y_pred_matrix.unique().tolist()
            display_labels = sorted(set(display_labels))
            
            df_matrix = pd.DataFrame(matrix, columns=display_labels)
            df_matrix[var.id_famille] = display_labels
            df_matrix.set_index(var.id_famille, inplace=True)
            df_matrix.to_excel(writer_confusion_matrix, index=True, sheet_name=sector[:nb_sectors])

def generate_classification_report_sector(y_pred, metrics_folder):
    """
    Generates classification report for sector prediction.

    Parameters
    ----------
    y_pred : pd.DataFrame
        True and predicted labels.
    metrics_folder : String
        Path to metrics folder.

    Returns
    -------
    None.

    """
    
    y_true = y_pred[var.id_secteur]
    y_pred = y_pred[var.predicted_secteur]
    clf = classification_report(y_true, y_pred, output_dict=True, zero_division=0.0)
    df_clf = pd.DataFrame(clf).transpose()
    df_clf.to_excel(metrics_folder + var.classification_report_sector, index=True, sheet_name=var.confusion_matrix)
    

def generate_classification_reports_family(y_pred, metrics_folder):
    """
    Generates classification reports for family classifications and save them into a metrics folder.

    Parameters
    ----------
    y_pred : pd.DataFrame
        True and predicted labels.
    metrics_folder : String
        Path to metrics folder.

    Returns
    -------
    None.

    """
    
    y_true_sector = y_pred[var.id_secteur]
    nb_sectors = len(y_true_sector.unique()) 
    sectors = sorted(y_pred[var.predicted_secteur].unique())
    with pd.ExcelWriter(metrics_folder + var.classification_report_family) as writer_classification_report:
        for sector in sectors:
            y_res = y_pred[y_pred[var.id_secteur] == sector]
            y_report_true = y_res[var.id_secteur]
            y_report_pred = y_res[var.predicted_secteur]
            clf = classification_report(y_report_true, y_report_pred, output_dict=True, zero_division=0.0)
            df_clf = pd.DataFrame(clf).transpose()
            df_clf.to_excel(writer_classification_report, index=True, sheet_name=sector[:nb_sectors])