"""
Module DataFrameNormalizer

DataFrame normalization class

@author: ThomasAujoux
"""



import pandas as pd
import re

import nltk
from nltk.stem.snowball import SnowballStemmer
stemmer = SnowballStemmer(language='french')
stopwords = nltk.corpus.stopwords.words('french')
stop_words_list = list(set(stopwords) )
inrae_dictio = ["", "a", "mg", "cm", "g", "gl", "ml", "k", "el", "ed", "gr" "k" "mi" "st" "the" , "kg", "dl", "l", "cl", "about", "ad", "al", "and", "in", "it", "too"]
for word in inrae_dictio:
    stop_words_list.append(word)

import multiclass_cascade_classifier.base.variables.Variables as var



#defining function for tokenization
def tokenization(text
                 ):
    """
    Tokenize columns of the dataframe

    Parameters
    ----------
    text : str
        cell of a DataFrame

    Returns
    -------
    list of str
        Données tokenizées.

    """
    tokens = text.split(sep = ' ')
    return tokens

#defining the function to remove stopwords from tokenized text
def remove_stopwords(text):
    """
    Remove the stopwords of a text

    Parameters
    ----------
    text : list of str
        cell of a DataFrame

    Returns
    -------
    list of str
        Données sans les stop words

    """
    output= [i for i in text if i not in stopwords]
    return output

def preprocess_text_stemm(df,
                        column=""
                        ):
    """
    Stemization of a column of a dataframe

    Parameters
    ----------
    X : pd.DataFrame
        Base de données.
    columns_text : String, optional
        Variables de textes (à prétraiter). The default is "".
    Returns
    -------
    pd.DataFrame
        Données lemmentizées.

    """
    for i in range(len(df[column])):
        if type(df[column][i]) != list :
            continue
        for j in range(len(df[column][i])):
            df[column][i][j] = stemmer.stem(df[column][i][j])
        while("" in df[column][i]):
            df[column][i].remove("")

    return df

def CleanDataFrame(X, 
               lowercase=False,
               removestopwords=False,
               removedigit=False, # doesn't use it anymore in the new version, it is in the preprocessing
               getstemmer=False,
               getlemmatisation=False, # doesn't use it anymore in the new version, for performance reasons
               columns_text=[],
               columns_binary=[], # doesn't use it anymore in the new version, for performance reasons
               columns_frozen=[]
              ):
    """
    Cleans, normalizes the dataframe

    Parameters
    ----------
    X : pd.DataFrame
        Base de données.
    lowercase : String, optional
        Lettres capitales -> minuscules. The default is False.
    removestopwords : Boolean, optional
        Enlever les stop words. The default is False.
    removedigit : Boolean, optional
        Enlever les chiffres. The default is False.
    getstemmer : Boolean, optional
        Racinisation. The default is False.
    getlemmatisation : Boolean, optional
        Lemmatisation. The default is False.
    columns_text : List<String>, optional
        Variables de textes (à prétraiter). The default is [].
    columns_binary : List<String>, optional
        Variables binaires (à ne pas prétraiter). The default is [].
    columns_frozen : List<String>, optional
        Variables avec prétraitement particulier si elles apparaissent dans les variables de texte. The default is [].

    Returns
    -------
    pd.DataFrame
        Données prétraitées.

    """
    for column in columns_text:
        print("We are processing this column:", column)
        if lowercase:
            X[column] = X[column].apply(lambda x: x.lower())

        X[column] = X[column].apply(lambda x: tokenization(x))

        if removestopwords:
            X[column] = X[column].apply(lambda x: remove_stopwords(x))
        
        if getstemmer:
            X = preprocess_text_stemm(X, column)
        if len(X.loc[X[column].isnull()])>0:
            X.loc[X[column].isnull()] = X.loc[X[column].isnull()].apply(lambda x: [""])

    return X



from sklearn.base import BaseEstimator, TransformerMixin

class DataFrameNormalizer(BaseEstimator, TransformerMixin):
    def __init__(self, 
                 removestopwords=False,
                 lowercase=False,
                 removedigit=False,
                 getstemmer=False,
                 getlemmatisation=False,
                 columns_text=[],
                 columns_binary=[],
                 columns_frozen=[]
                ):
        
        self.lowercase=lowercase
        self.getstemmer=getstemmer
        self.removestopwords=removestopwords
        self.getlemmatisation=getlemmatisation
        self.removedigit=removedigit
        self.columns_text=columns_text
        self.columns_binary = columns_binary
        self.columns_frozen=columns_frozen

    def transform(self, X, **transform_params):
        # Nettoyage du texte
        X=X.copy() # pour conserver le fichier d'origine
        return CleanDataFrame(X,lowercase=self.lowercase,
                            getstemmer=self.getstemmer,
                            removestopwords=self.removestopwords,
                            getlemmatisation=self.getlemmatisation,
                            removedigit=self.removedigit,
                            columns_text=self.columns_text,
                            columns_binary=self.columns_binary,
                            columns_frozen=self.columns_frozen)

    def fit(self, X, y=None, **fit_params):
        return self
    
    def fit_transform(self, X, y=None, **fit_params):
        return self.fit(X).transform(X)

    def get_params(self, deep=True):
        return {
            'lowercase':self.lowercase,
            'getstemmer':self.getstemmer,
            'removestopwords':self.removestopwords,
            'getlemmatisation':self.getlemmatisation,
            'removedigit':self.removedigit,
            'columns_text':self.columns_text,
            'columns_binary':self.columns_binary,
            'columns_frozen':self.columns_frozen
        }    
    
    def set_params (self, **parameters):
        for parameter, value in parameters.items():
            setattr(self,parameter,value)
        return self    
    
