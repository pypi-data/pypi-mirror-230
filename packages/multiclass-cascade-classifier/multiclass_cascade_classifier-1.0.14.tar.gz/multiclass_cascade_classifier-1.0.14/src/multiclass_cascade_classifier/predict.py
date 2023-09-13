"""
@author: ThomasAujoux
"""

import click

from multiclass_cascade_classifier.Skeleton import predict

def get_path(path):
    out = path.strip()
    out = out.replace('"', "")
    out = out.replace("'", "")
    
    return out

@click.command()
@click.option('--prediction_set_path', prompt="Path to test data", help='Train data.', required=True, type=str)
@click.option('--models_folder', prompt="Path to models folder", help='Folder where the trained classifiers are saved.', required=True, type=str)
@click.option('--predicted_set_path', prompt="Path to predicted data", help='File that will contain the predicted data.', required=True, type=str)
@click.option('--n_families', default=5, prompt="Number of families to predict", help='The number of families that will be predicted for each product.', required=True, type=int)
def command_predict(prediction_set_path, models_folder, predicted_set_path, n_families):
    """
    Test command.

    Parameters
    ----------
    prediction_set_path : String
        Path to the file that contains the data set.
    models_folder : String
        Path to the file that contains the trained classifiers as joblib files.
    predicted_set_path : String
        Path to the file that will contain the predicted data.
    n_families: Integer
        The number of families that will be predicted for each product.

    Returns
    -------
    None.

    """
    prediction_set_path = get_path(prediction_set_path)
    models_folder = get_path(models_folder)
    predicted_set_path = get_path(predicted_set_path)
    
    predict(prediction_set_path, models_folder, predicted_set_path, n_families)

if __name__ == '__main__':
    command_predict()
