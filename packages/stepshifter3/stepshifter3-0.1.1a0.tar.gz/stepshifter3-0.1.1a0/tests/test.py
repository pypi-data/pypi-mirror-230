from xgboost import XGBRegressor, XGBClassifier
from lightgbm import LGBMRegressor, LGBMClassifier
from stepshifter3.stepshifter import StepShifter
from sklearn.base import is_classifier
from stepshifter3.synthetic_data_generator import SyntheticDataGenerator

# define some XGBRegressor parameters:
test_params_xgb_reg = {
    'objective': 'reg:squarederror',
    'n_estimators': 300,
    'max_depth': 3,
    'learning_rate': 0.1,
    'n_jobs': -1,
    'eval_metric': 'rmse',
}

test_params_xgb_clf = {
    'objective': 'binary:logistic',
    'n_estimators': 100,
    'max_depth': 3,
    'learning_rate': 0.1,
    'n_jobs': -1
}

test_params_lgbm_clf = {
    'objective': 'binary',
    'n_estimators': 100,
    'max_depth': 3,
    'learning_rate': 0.1,
    'n_jobs': -1
}

test_params_lgbm_reg = {
    'objective': 'regression',
    'n_estimators': 100,
    'max_depth': 3,
    'learning_rate': 0.1,
    'n_jobs': -1
}

list_of_estimators = [XGBRegressor(**test_params_xgb_reg),
                      XGBClassifier(**test_params_xgb_clf),
                      LGBMRegressor(**test_params_lgbm_reg),
                      LGBMClassifier(**test_params_lgbm_clf)]


def test_stepshifter3(list_of_test_estimators=list_of_estimators):

    df = SyntheticDataGenerator("pgm", n_time=516, n_prio_grid_size=100, n_country_size= 242,n_features=3,use_dask=False).generate_dataframe()

    # Make a copy of the dataframe
    df_clf = df.copy()
    df_clf['ln_ged_sb_dep'] = df_clf['ln_ged_sb_dep'].apply(lambda x: 1 if x > df_clf['ln_ged_sb_dep'].mean() else 0)

    counter = 0

    for estimator in list_of_test_estimators:
        stepshifter_config_test = {
            "target_column": "ln_ged_sb_dep",
            "ID_columns": ["month_id", "country_id"],
            "time_column": "month_id",
            "run_name": f'test_run_{counter}',
            "experiment_name": 'xgb_reg_experiment_0',
            "mlflow_tracking_uri": 'http://127.0.0.1:5000',
            "tau^e_0": 121,  # training period start
            "tau^e_t": 131,  # training period end
            "tau^e_c": 136,  # calibration period end
            "tau^e_f": 468,  # forecast period end
            "tau_f": 516,   # Test Forfecast end
            "k": 13,
            "S": 5,
            "metrics_report": True,
            "combine_method": 'mean_of_all',
            "fit_params": {},
        }

        if is_classifier(estimator):
            # use df_clf:
            stepshifter = StepShifter(estimator, df_clf, stepshifter_config_test)
        else:
            # use df:
            stepshifter = StepShifter(estimator, df, stepshifter_config_test)

        models = stepshifter.fit(stepshifter_config_test['tau^e_0'], stepshifter_config_test['tau^e_t'])
        assert len(models) == stepshifter_config_test['S']
        
    """
    counter = 0
    for estimator in list_of_test_estimators:
        stepshifter_config_test = {"target_column": "ln_ged_sb_dep",
                                    "ID_columns": ["month_id", "country_id"],
                                    "time_column": "month_id",
                                    "run_name": f'test_run_{counter}',
                                    "experiment_name": 'xgb_reg_experiment_0',
                                    "mlflow_tracking_uri": 'http://127.0.0.1:5000',
                                    "tau^e_0": 121,  # training period start
                                    "tau^e_t": 131,  # training period end
                                    "tau^e_c": 136,  # calibration period end
                                    "tau^e_f": 468,  # forecast period end
                                    "tau_f": 516,   # Test Forfecast end
                                    "k": 13,
                                    "S": 5,
                                    "metrics_report": True
                                    }

        if is_classifier(estimator):
            # use df_clf:
            stepshifter = StepShifter(estimator, df_clf, stepshifter_config_test)
        else:
            # use df:
            stepshifter = StepShifter(estimator, df, stepshifter_config_test)
        stepshifter.start_mlflow()
        models = stepshifter.fit_mlflow(stepshifter_config_test['tau^e_0'], stepshifter_config_test['tau^e_t'])
        assert len(models[list(models.keys())[0]]) == stepshifter_config_test['S']
        assert len(models[list(models.keys())[-1]]) == 1
        counter += 1
    """


if __name__ == "__main__":
    test_stepshifter3()
