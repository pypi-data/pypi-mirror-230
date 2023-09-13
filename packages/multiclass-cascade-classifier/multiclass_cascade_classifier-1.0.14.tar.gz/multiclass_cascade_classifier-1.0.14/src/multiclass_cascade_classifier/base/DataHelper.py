"""
Module DataHelper

Help to import the csv files in a DataFrame

@author: ThomasAujoux
"""


import csv
import pandas as pd



def csv2data(csv_in, N=None):
    """
    Transforme le contenu du fichier csv csv_in en un data set

    Parameters
    ----------
    csv_in : String
        Fichier de chargement.
    N : Int, optional
        Nombre max d'instances à charger. The default is -1.

    Returns
    -------
    data : List (deux dimension)
        Tableau avec les données.

    """
    data = []
    #Ouverture du fichier
    with open(csv_in, 'rt') as csvfile:
        #Lecture du fichier
        rd = csv.reader(csvfile, delimiter=';', quotechar='"')
        #next(rd)  # skip the header row
        for row in rd:
            if len(row):
                data.append(row)
            if N != None and not len(data) < N and N != -1:
                break
    return data

def get_dataframe(csv_in, N=None):
    """
    Transforme le contenu du fichier csv csv_in en un pd.DataFrame

    Parameters
    ----------
    csv_in : String
        Path to data file.
    N : Int, optional
        Nombre max d'instances à charger. The default is -1.

    Returns
    -------
    df : pd.DataFrame
        DataFrame résultante.

    """
    data = csv2data(csv_in, N=N)
    df = pd.DataFrame(data[1:][:], columns = data[0][:])
    return df
