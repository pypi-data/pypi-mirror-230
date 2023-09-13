"""
@author: ThomasAujoux
"""

import click

from multiclass_cascade_classifier.Skeleton import train

def get_path(path):
    out = path.strip()
    out = out.replace('"', "")
    out = out.replace("'", "")
    
    return out

@click.command()
@click.option('--train_set_path', prompt="Path to train data", help='Train data.', required=True, type=str)
@click.option('--models_folder', prompt="Path to models folder", help='Folder where the trained classifiers will be saved.', required=True, type=str)
@click.option('--hyper_sector', prompt="Sector classification hyperparameters (yaml)", default="", help='File that contains the slected hyperparameters for the sector classifier.', required=False, type=str)
@click.option('--hyper_family_per_sector', prompt="Family classifications hyperparameters (yaml)", default="", help='File that contains the slected hyperparameters for the family classifiers.', required=False, type=str)
@click.option('--force', prompt="If True, if a sector doesn't appear in the yaml file for the family classifications, it forces the selection of hyperparameters for this sector.", is_flag=True, default=False, help="If some sectors don't have a trained classifier, it forces the test despite knowing some products will be falsely classified.", required=True, type=bool)
@click.option('--n_jobs', prompt="Number of jobs (for grid dearch)", default=-1, help='Number of jobs in the parallelization of the hyperparameters search.', type=int, required=False)
@click.option('--log_folder', prompt="Location of log file (log folder)", default="", help='Location of log file.', type=str, required=False)
def command_train(train_set_path, models_folder, hyper_sector, hyper_family_per_sector, force, n_jobs, log_folder):
    """
    Train command.

    Parameters
    ----------
    train_set_path : String
        Path to the file that contains the data set.
    models_folder : String
        Path to the file that will contain the trained classifiers as joblib files.
        It will also contains a file with the selected hyperparameters.
    hyper_sector : String
        Path to the file that contains the hyperparameters for the sector classifier.
    hyper_family_per_sector : String
        Path to the file that contains the hyperparameters for the family classifiers.
    force : Boolean
        If True, if a sector doesn't appear in the yaml file for the family classifications, it forces the selection of hyperparameters for this sector.
    log_folder : String
        Location where log file will be saved.
        
    Returns
    -------
    None.

    """
    train_set_path = get_path(train_set_path)
    models_folder = get_path(models_folder)
    hyper_sector = get_path(hyper_sector)
    hyper_family_per_sector = get_path(hyper_family_per_sector)

    log_folder = get_path(log_folder)

    train(train_set_path, models_folder, hyper_sector, hyper_family_per_sector, force, n_jobs, log_folder)

if __name__ == '__main__':
    command_train()
