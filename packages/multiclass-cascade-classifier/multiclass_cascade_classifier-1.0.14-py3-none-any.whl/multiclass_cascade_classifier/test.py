"""
@author: ThomasAujoux
"""

import click

from multiclass_cascade_classifier.Skeleton import test

def get_path(path):
    out = path.strip()
    out = out.replace('"', "")
    out = out.replace("'", "")
    
    return out

@click.command()
@click.option('--test_set_path', prompt="Path to test data", help='Train data.', required=True, type=str)
@click.option('--models_folder', prompt="Path to models folder", help='Folder where the trained classifiers are saved.', required=True, type=str)
@click.option('--metrics_folder', prompt="Path to metrics folder", help='Folder where generated statistics will be saved.', required=True, type=str)
@click.option('--n_families', default=5, prompt="Number of families to predict", help='The number of families that will be predicted for each product.', required=True, type=int)
@click.option('--force', prompt="If true, if some sectors don't have a trained classifier, it forces the test despite knowing some products will be falsely classified.", is_flag=True, default=False, help="If some sectors don't have a trained classifier, it forces the test despite knowing some products will be falsely classified.", required=True, type=bool)

def command_test(test_set_path, models_folder, metrics_folder, n_families, force):
    """
    Test command.

    Parameters
    ----------
    test_set_path : String
        Path to the file that contains the data set.
    models_folder : String
        Path to the file that contains the trained classifiers as joblib files.
    metrics_folder : String
        Path to the folder that will contain the generated statistics.
    n_families: Integer
        The number of families that will be predicted for each product.
    force : Boolean
        If true, if some sectors don't have a trained classifier, it forces the test despite knowing some products will be falsely classified.

    Returns
    -------
    None.

    """
    test_set_path = get_path(test_set_path)
    models_folder = get_path(models_folder)
    metrics_folder = get_path(metrics_folder)
    test(test_set_path, models_folder, metrics_folder, n_families, force)

if __name__ == '__main__':
    command_test()
