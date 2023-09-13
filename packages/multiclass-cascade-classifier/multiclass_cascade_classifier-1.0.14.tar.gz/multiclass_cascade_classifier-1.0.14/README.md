# Implementation of a multi-class cascade classifier in a package

<p align="center">
<img src='presentation/Capture d’écran 2023-09-12 105708.png' alt="banner"></img>
</p>

## General Presentation

This repository includes the second part of my second-year internship at ENSAE (National School of Statistics and Economic Administration), which I carried out at INRAE (National Research Institute for Agriculture, Food and the Environment) over a 4-month period.

More specifically, it contains the development and implementation part
in a functional Python package, accessible from Pypi, of a cascade classifier.

**! To find out more about the code: take a look at the Wiki of the Wiki !**

## Project hierarchy


    ├── LICENSE
    ├── README.md
    ├── dist/ <- Folder containing the package
    ├── examples/ <- For testing
    │   ├── data/
    │   │   └── merged_final.csv
    │   ├── log/
    │   ├── metrics/
    │   │   ├── classification_report_famille.xlsx
    │   │   ├── classification_report_secteur.xlsx
    │   │   ├── confusion_matrix_famille.xlsx
    │   │   ├── confusion_matrix_secteur.xlsx
    │   │   ├── general_stats.txt
    │   │   └── predictions.csv
    │   ├── models/
    │   │   ├── hyper-family.yaml
    │   │   ├── hyper-sector.yaml
    │   │   └── secteurs.joblib
    │   ├── predict_out/
    │   │   └── predictions.csv
    │   └── train_test/
    │       ├── test_split.csv
    │       └── train_split.csv
    ├── pyproject.toml <- To generate the package
    ├── setup.cfg <- To generate the package
    └── src/ <- Package source code
        ├── multiclass_cascade_classifier/
        │   ├── Scripts.py
        │   ├── Skeleton.py
        │   ├── __init__.py
        │   ├── base/
        │   │   ├── ClassifierHelper.py
        │   │   ├── DataFrameNormalizer.py
        │   │   ├── DataHelper.py
        │   │   ├── DataPredicter.py
        │   │   ├── DataTrainer.py
        │   │   ├── DataVectorizer.py
        │   │   ├── FeaturesManipulator.py
        │   │   ├── HyperSelector.py
        │   │   ├── LogJournal.py
        │   │   ├── MetricsGenerator.py
        │   │   ├── PreProcessing.py
        │   │   ├── VariablesChecker.py
        │   │   ├── __init__.py
        │   │   └── variables/ <- Contains general variables
        │   │       ├── Variables.py
        │   │       ├── __init__.py
        │   ├── predict.py
        │   ├── split.py
        │   ├── test.py
        │   └── train.py
        └── multiclass_cascade_classifier.egg-info/



## Installation via Pypi


```bash
pip install multiclass_cascade_classifier
```

Note: if this doesn't work, check the file name. It may change depending on the version.

You can now import and use the modules in this package!
**To find out more, check out the wiki!**