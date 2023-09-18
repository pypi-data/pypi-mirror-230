import os
import shutil
import time
from copy import deepcopy

import pandas as pd
import pytest
import shap
from catboost import CatBoostClassifier, CatBoostRegressor
from lightgbm import LGBMClassifier, LGBMRegressor
from sklearn.calibration import CalibratedClassifierCV
from sklearn.datasets import load_breast_cancer, load_diabetes
from sklearn.ensemble import (ExtraTreesClassifier, ExtraTreesRegressor,
                              GradientBoostingClassifier,
                              GradientBoostingRegressor,
                              RandomForestClassifier, RandomForestRegressor,
                              StackingClassifier, StackingRegressor,
                              VotingClassifier, VotingRegressor)
from sklearn.linear_model import (ElasticNet, Lasso, LinearRegression,
                                  LogisticRegression, Ridge)
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor
from xgboost import XGBClassifier, XGBRegressor

from auto_shap.auto_shap import (generate_shap_values,
                                 produce_shap_values_and_summary_plots)


def train_simple_classification_model(model):
    x, y = load_breast_cancer(return_X_y=True, as_frame=True)
    model.fit(x, y)
    x = x.head(50)
    return model, x


def voting_classifier_and_data():
    return train_simple_classification_model(VotingClassifier(estimators=[
        ('rf', RandomForestClassifier()), ('et', ExtraTreesClassifier())], voting='soft'))


model, x = voting_classifier_and_data()
print(model)
print(x)

