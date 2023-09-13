"""
@author: ThomasAujoux
"""

import click

from multiclass_cascade_classifier.Skeleton import split

def get_path(path):
    out = path.strip()
    out = out.replace('"', "")
    out = out.replace("'", "")
    
    return out

@click.command()
@click.option('--data_file_path', prompt="Path to raw data", help='Raw data.', required=True, type=str)
@click.option('--train_file', prompt="Path to train set", default="train_split.csv", help='File to save the training set.', type=str)
@click.option('--test_file', prompt="Path to test set", default="test_split.csv", help='File to save the test set.', type=str)
@click.option('--test_size', prompt="Test size (in %)", default=20, help='Size of test set.', type=int)
def command_split(data_file_path, train_file, test_file, test_size):
    """
    Split command.

    Parameters
    ----------
    data_file_path : String
        Path to the file that contains the data set.
    train_file : String
        Path to the file where the train set will be saved.
    test_file : String
        Path to the file where the test set will be saved.
    test_size : Integer
        Size of test set.

    Returns
    -------
    None.

    """
    data_file_path = get_path(data_file_path)
    
    train_file = get_path(train_file)
    
    test_file = get_path(test_file)
    
    split(data_file_path, train_file, test_file, int(test_size)/100)

if __name__ == '__main__':
    command_split()
