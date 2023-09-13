"""
Module LogJournal

Log journal class

@author: ThomasAujoux
"""



import datetime



class LogJournal():
    
    def __init__(self, path, name):
        self.path=path
        self.name=name
        self.open()

    def open(self):
        """
        Ouvre le journal

        Returns
        -------
        None.

        """
        with open(self.path + self.name + '.txt', "a") as file:
            file.write('\n_________________________________________  _\n\n\n')
            file.write('\n' + str(datetime.datetime.today()) + '\n\n')
            file.close()
    
    def write_text(self, text):
        """
        Ecrit le texte text dans le journal

        Parameters
        ----------
        text : String
            Texte à écrire.

        Returns
        -------
        None.

        """
        with open(self.path + self.name + '.txt', "a") as file:
            file.write('\n' + str(datetime.datetime.today()) + " | " + str(text) + '\n')
            file.close()
    
    def write_texts(self, texts):
        """
        Ecrit les textes de texts dans le journal

        Parameters
        ----------
        texts : List<String>
            Liste des textes à écrire.

        Returns
        -------
        None.

        """
        for text in texts:
            self.write_text(text)
        return
    
    def close(self):
        """
        Ferme le journal

        Returns
        -------
        None.

        """
        with open(self.path + self.name + '.txt', "a") as file:
            file.write('\n__________________________________________\n\n\n')
            file.close()