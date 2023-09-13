"""
Module DataVectorizer

Data vectorization class

@author: ThomasAujoux
"""



import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer

import multiclass_cascade_classifier.base.variables.Variables as var



class DataVectorizer():
    def __init__(self,
                 columns_text=[],
                 columns_binary=[]
                 ):
        
        self.columns_text=columns_text
        self.columns_binary=columns_binary
        
        self.TfidfVectorizer_text = TfidfVectorizer(binary=False, norm='l2',
            use_idf=True, smooth_idf=True,
            min_df=1, max_features=1000, 
            ngram_range=(1, 2))
        
        self.TfidfVectorizer_binary = { }
        
        for column in self.columns_binary:
            self.TfidfVectorizer_binary[column] = TfidfVectorizer(
                binary=True, norm=None,
                use_idf=False, smooth_idf=False,
                min_df=1, max_features=None, ngram_range=(1, 1))
        
    def fit_transform(self, X):
        
        data_text = []
        for index, row in X.iterrows(): # Concaténation des variables à vectoriser
            row_txt = ""
            for column_txt in self.columns_text:
                row_txt += str(row[column_txt]) + " "
            data_text.append(row_txt)
            
        data_text_vect = self.TfidfVectorizer_text.fit_transform(data_text).toarray().tolist()
        
        data_bin_vect = { }
        for column_bin in self.columns_binary:
            data_bin_vect[column_bin] = self.TfidfVectorizer_binary[column_bin].fit_transform(X[column_bin]).toarray().tolist()
        
        X_vect_text = pd.DataFrame(data_text_vect, columns=self.TfidfVectorizer_text.get_feature_names_out())
        X_vect_text.set_index(X.index, inplace=True)
        
        X_vect_binary = { }
        for column_bin in self.columns_binary:
            X_vect_bin = pd.DataFrame(data_bin_vect[column_bin], columns=self.TfidfVectorizer_binary[column_bin].get_feature_names_out())
            X_vect_bin.set_index(X.index, inplace=True)
            X_vect_binary[column_bin] = X_vect_bin

        # Checking that all binary features are vectorized
        for column_bin in var.binary_features:
            if column_bin in self.columns_binary:
                x_features = X_vect_binary[column_bin].copy(deep=True)
                for feature in var.binary_features[column_bin]:
                    if feature not in x_features.columns.to_list():
                        x_features[feature] = 0
            X_vect_binary[column_bin] = x_features[var.binary_features[column_bin]]
            
        data_vect = []
        for index, row in X_vect_text.iterrows():
            X_row = X_vect_text.loc[index].values.tolist()
            for column_bin in self.columns_binary:
                X_row += X_vect_binary[column_bin].loc[index].values.tolist()
            data_vect.append(X_row)
                
        X_columns = X_vect_text.columns.to_list()
        for column_bin in self.columns_binary:
            X_columns += X_vect_binary[column_bin].columns.to_list()
        X_vect = pd.DataFrame(data_vect, columns=X_columns, index=X.index)
        
        print('--- Base ---')
        print('Nombre de produits : ', str(X_vect.shape[0]))
        print('Nombre de mots : ', str(X_vect.shape[1]))
        print('--- ---- ---')
        
        return X_vect
    
    def get_params(self, deep=True):
        return {
            "columns_text": self.columns_text,
            "columns_binary": self.columns_binary,
            "features": self.features,
        }    
    
    def set_params (self, **parameters):
        for parameter, value in parameters.items():
            setattr(self,parameter,value)
        return self  