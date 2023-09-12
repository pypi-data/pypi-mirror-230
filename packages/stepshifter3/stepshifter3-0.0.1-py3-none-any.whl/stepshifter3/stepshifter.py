from sklearn.base import BaseEstimator, clone
import numpy as np
import warnings
import pandas as pd
import mlflow
import os
import tqdm as tqdm
from xgboost import XGBRegressor, XGBClassifier
import requests


class StepShifter(BaseEstimator):
    """
    Introduction
    Stepshifter3 is a general purpose stepshifting algorithm for tabular data based on Hegre et.al 2019.
    It is designed to be used with any scikit-learn compatible estimator,
    and can be used for both regression and classification.
    It is further designed to be used with tabular data, and can handle both single and multi-index DataFrames.

    Definitions
    - The VIEWS month id is a counter that starter on 1. January 1980


    Variables
    τ           = reference time for which the project is operating,
                   we can observe values less than tau but not greater
    S           = maximum number of steps ahead to predict
    M           = the set of months in a test window, i.e., the months we want to iterate stepshifts over
    s           = step number, i.e., the number of steps ahead we want to predict
    e           = superscript denoting evaluation time partition
    τ^e_0       = training partition period starting point
    τ^e_t       = training partition period ending point
    τ_0         = forceast period starting point
    τ_t         = forecast period ending point
    τ^e_t + 1   = evaluation calibration period starting point
    τ^e_c       =  evaluation calibration period ending point
    τ^e^c + 1   = evaluation forecast period starting point
    τ^e_f       =  forecast period ending point
    τ_t+1       = forecast period starting point
    τ_c         = forecast period ending point
    m_j         = model specification

    Example:
    ___________________________________________________________________________________________________
    |                         | Periodization                                                          |
    |--------------------------------------------------------------------------------------------------|
    |                         | Evaluation                       |  Forecast                           |
    |-------------------------|----------------------------------|-------------------------------------|
    | Training Period         | τ^e_0     = 121 (January 1990)   | τ_0          = 121 (January 1990)   |
    |_________________________| τ^e_t     = 396 (December 2012)  | τ_t          = 432 (December 2015)  |
    | Calibration Period      | τ^e_t + 1 = 397 (January 2013)   | τ_t + 1      = 433 (January 2016)   |
    |_________________________| τ^e_c     = 432 (December 2015)  | τ_c          = 468 (December 2018)  |
    | Predictor Updating      | n/a                              | τ_c + 1      = 469 (January 2019)   |
    |_________________________| n/a                              | τ_c + (k −1) = 480 (December 2019)  |
    | Testing Period          | τ^e_c + 1 = 433 (January 2016)   | τ_c + k      = 481 (January 2020)   |
    |                         | τ^e_f     = 468 (December 2018)  | τ_f          = 516 (December_2022)  |
    |--------------------------------------------------------------------------------------------------|

    Pseudocode for stepshifter3:

    1.

        models are trained on the training partition period tau_0^e to tau_t^e
        for each step s in S:

    2.
        generate predictions for each m^(j,s)
        for all months i in the calibration period tau_t^e + 1 to tau_c^e
        using data up to s months before i

    3.
        Calibrate models, obtain ensamble weights for each model,
        and tune hyperparameters using the predictions from step 2;
        and the actuals for all months i in the calibration period tau_t^e + 1 to tau_c^e

    4.
        Retrain model m^(j,s) using both the training partition period,
        tau_0^e to tau_t^e and the calibration period tau_t^e + 1 to tau_c^e

    5.
        Generate predictions for the testing/forecasting period tau_^c_e + 1 to tau_^c_f

    Args:
        base_estimator (object): The estimator to be used for training and prediction.
        df (DataFrame): The DataFrame to be used for training and prediction.
        config (dict): A dictionary containing the configuration for the model,
        see the example config file for more information.

    Authors: Tom Daniel Grande, Jonas Schie Olsen
    Written: 2023-08-28 -> ????-??-??
"""

    def __init__(self, base_estimator,  df=None, config=None):
        self.base_estimator = base_estimator  # The wrapped estimator, could be xgboost, sklearn, etc.
        self.S = None  # Maximum steps ahead to predict
        self.t = None  # Training period starting point
        self.t_1 = None  # Training period ending point
        self.M_ssa = None  # The stepcombined model object
        self.models = {}  # Dictionary to store trained models for each step
        self.predictions = None
        self.metrics_report = None  # If True, will generate a metrics report
        self.run_name = None  # Name of the run
        self.ID_columns = None
        self.time_column = None
        self.X = None
        self.y = None
        self.mlflow_tracking_uri = None
        self.experiment_name = None
        self.fit_config = None
        self.fit_params = None
        self._set_internal_variables_from_config(config, df)

    def _set_internal_variables_from_config(self, config, df):
        """Sets internal variables from a config file."""
        self.S = config['S']
        self.t_0 = config['tau^e_0']
        self.t_1 = config['tau^e_t']
        self.ID_columns = config['ID_columns']
        self.mlflow_tracking_uri = config['mlflow_tracking_uri']
        self.metrics_report = config['metrics_report']
        self.experiment_name = config['experiment_name']
        self.run_name = config['run_name']
        self.df = self._validate_df(df, config)
        self.X = self._validate_X(config)
        self.y = self._validate_y(config)
        self.time_column = config['time_column']
        self.is_xgb = (isinstance(self.base_estimator, XGBRegressor) or isinstance(self.base_estimator, XGBClassifier))
        self.combine_method = config['combine_method']
        self.fit_params = config['fit_params']
        # Checks on parameters:

        # Check if S is an integer
        if not isinstance(self.S, int):
            raise ValueError("max_steps must be an integer.")
        if self.S > 1024:
            warnings.warn("You have specified more than 1024 steps, this could impact performance.")
    # Assuming these functions are part of a class

    def _validate_df(self, df, config):
        """
        Remove all countries that do not have rows in the range (t1, t2).

        Parameters:
            df (DataFrame): The original DataFrame.
            t1 (int): The start of the time range.
            t2 (int): The end of the time range.

        Returns:
            DataFrame: A filtered DataFrame.
        """
        # Get unique country IDs
        unique_countries = df.index.get_level_values(1).unique()

        # List to hold the countries that meet the criteria
        valid_countries = []

        for country_id in unique_countries:
            # Filter the DataFrame for the specific country
            df_country = df.loc[pd.IndexSlice[:, country_id], :]

            # Get unique months for this country
            country_months = df_country.index.get_level_values(0).unique()

            # Check if the country has data for the entire range
            if all(month in country_months for month in range(config['tau^e_0'], config['tau^e_f'])):
                valid_countries.append(country_id)

        # Filter the DataFrame to only include valid countries
        df_filtered = df.loc[pd.IndexSlice[:, valid_countries], :]

        # throw a warning if the number of rows is reduced:
        if len(df_filtered) < len(df):
            warnings.warn("The number of rows has been reduced due to missing values.")
            warnings.warn(f"Number of rows before filtering: {len(df)}, after filtering: {len(df_filtered)}")

        return df_filtered

    def _validate_params(self):
        """Validates the parameters."""
        if not isinstance(self.S, int):
            raise ValueError("max_steps must be an integer.")
        if self.S > 1024:
            warnings.warn("You have specified more than 1024 steps, this could impact performance.")

    def _validate_X(self, config):
        """Validates the X input."""
        if not isinstance(self.df, pd.DataFrame):
            raise ValueError("df must be a pandas DataFrame.")

        # X is everything but the column config["target _column"]:
        X_cols = [col for col in self.df.columns if col not in config["target_column"]]
        X = self.df[X_cols]

        if X.shape[1] < 1:
            raise ValueError("X must have at least 3 columns (2 ID columns and 1 feature column).")
        # remove ID columns and store them for perservance in the predict

        return X

    def _validate_y(self, config):
        """Validates the y input."""
        # y is the last column in the dataframe:
        y = self.df[config["target_column"]]

        # check if y is numeric
        if not np.issubdtype(y.dtype, np.number):
            raise ValueError("Target (y) must be numeric.")

        # check if y is nan:
        if y.isna().any():
            raise ValueError("Target (y) must not contain NaNs.")
        return y

    def start_mlflow(self):
        """Starts an mlflow run."""
        # check if there exist an mlflow server:
        response = requests.get(self.mlflow_tracking_uri)

        if response.status_code == 200:
            print("Status is 200 OK.")
        else:
            warnings.warn(f"Status is not 200 OK, but {response.status_code}, trying to start mlflow server, locally")
            try:
                os.system("mlflow server --host 127.0.0.1:5000")
            except Exception as e:
                warnings.warn(f"Could not start mlflow server, error: {e}")
                pass

        mlflow.set_tracking_uri(self.mlflow_tracking_uri)

    def fit(self, tau_start, tau_end):
        self.models = {}  # Clear previous models

        X_m = self.X.loc[slice(tau_start, (tau_end)), slice(None), :]
        y_m = self.y.loc[X_m.index]
        for s in tqdm.tqdm(range(1, self.S + 1)):  # Loop over each step
            # shift the data according to the step
            y_s = y_m.groupby(level=1).shift(-s)
            X_m = self.X.loc[slice(tau_start, (tau_end-s)), slice(None), :]
            y_s = y_s.loc[X_m.index]

            model = clone(self.base_estimator)
            model.fit(X_m, y_s, **self.fit_params)
            self.models[s] = model
        return self.models

    def predict(self, tau_start, tau_end):
        prediction_matrix = []
        for taus in range(tau_start, tau_end):
            X_m = self.X.loc[slice(taus, taus), slice(None), :]  # Do prediction for one month at a time
            predictions_for_step = []

            # loop through all steps for each month, but exlude steps we don't have a true value for
            for s in range(1, self.S+1):

                model = self.models[s]
                prediction = model.predict(X_m)
                predictions_for_step.append(prediction)

            prediction_matrix.append(predictions_for_step)

        self.predictions = prediction_matrix
        return prediction_matrix

    def predict_mlflow(self, X, logged_model):
        # TODO: implement this
        pass

    def get_step_number(self, step_number):
        """Retrieve the model for a given step number."""
        return self.models.get(step_number)

    def remove_ID_columns(self, df) -> pd.DataFrame:
        if isinstance(df.index, pd.MultiIndex):
            # Reset the index if it's a multi-index DataFrame
            df_reset = df.reset_index()

            # Only drop the columns specified in self.id_columns if they exist
            drop_columns = [col for col in self.ID_columns if col in df_reset.columns]
            df_clean = df_reset.drop(drop_columns, axis=1)

        else:
            # For single-index DataFrames, drop the columns specified in self.id_columns if they exist
            drop_columns = [col for col in self.ID_columns if col in df.columns]
            df_clean = df.drop(drop_columns, axis=1)

        return df_clean

    def generate_metrics_report(self):
        """Placeholder for generating a metrics report."""
        # To be implemented, will probably use the GenerateReport class:
        # GenerateReport(model, X, y)

    """
    DEBUG FUNCTIONS:
    """

    @staticmethod
    def _debug_visualize_step(y_1, y_2):
        # filter y to only include one country:
        y_1 = y_1.loc[y_1.index.get_level_values(1) == 3]
        y_2 = y_2.loc[y_2.index.get_level_values(1) == 3]
        pd.set_option('display.max_rows', None)
        # add both to same dataframe:
        y_1 = y_1.to_frame()
        y_2 = y_2.to_frame()
        y_1.columns = ['y_1']
        y_2.columns = ['y_2']
        y_1['y_2'] = y_2['y_2']
        print(y_1)

    @staticmethod
    def _debug_find_nan_positions(y):
        nan_positions = np.where(y.isna())[0]
        # Return also the country id for the nan positions:
        nan_positions = y.index.get_level_values(1)[nan_positions]
        return nan_positions
