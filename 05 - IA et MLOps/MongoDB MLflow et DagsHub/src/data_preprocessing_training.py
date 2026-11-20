"""Data preprocessing and training utilities."""

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
import mlflow
import mlflow.sklearn
import joblib
import os


def load_data(csv_path: str) -> pd.DataFrame:
    """Load dataset from CSV."""
    return pd.read_csv(csv_path)


def preprocess_data(df: pd.DataFrame, target_col: str):
    """Split features and target, scale features."""
    X = df.drop(columns=[target_col])
    y = df[target_col]
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    return X_train_scaled, X_test_scaled, y_train, y_test, scaler


def transform_data(df: pd.DataFrame):
    """
    Cleans and preprocesses the fraud dataset as expected by the notebook.
    Returns X_train, X_test, y_train, y_test.
    """
    # Identify target column (usually 'is_fraud' or 'class' for this dataset)
    # If not present, we assume the last column is the target
    target_candidates = ['is_fraud', 'class', 'target']
    target_col = next((c for c in target_candidates if c in df.columns), df.columns[-1])
    
    X = df.drop(columns=[target_col])
    y = df[target_col]
    
    # Split into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    return X_train, X_test, y_train, y_test


def train_model(X_train, y_train, params=None):
    """Train a logistic regression model."""
    if params is None:
        params = {}
    model = LogisticRegression(**params)
    model.fit(X_train, y_train)
    return model


def evaluate_model(model, X_test, y_test):
    """Evaluate model and return accuracy."""
    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    return acc


def run_experiment(csv_path: str, target_col: str, params=None):
    """End-to-end experiment logging with MLflow."""
    # Check if we need to start a run
    started_run = False
    if mlflow.active_run() is None:
        mlflow.start_run()
        started_run = True

    try:
        # Load and preprocess
        df = load_data(csv_path)
        X_train, X_test, y_train, y_test, scaler = preprocess_data(df, target_col)

        # Log dataset info
        mlflow.log_param("train_samples", X_train.shape[0])
        mlflow.log_param("test_samples", X_test.shape[0])
        mlflow.log_param("n_features", X_train.shape[1])

        # Train
        model = train_model(X_train, y_train, params)
        for k, v in (params or {}).items():
            mlflow.log_param(k, v)

        # Evaluate
        acc = evaluate_model(model, X_test, y_test)
        mlflow.log_metric("accuracy", acc)

        # Log model and scaler
        mlflow.sklearn.log_model(model, "model")
        # Optionally log scaler as artifact
        scaler_path = "scaler.pkl"
        joblib.dump(scaler, scaler_path)
        mlflow.log_artifact(scaler_path)
        os.remove(scaler_path)

        return model, acc
    finally:
        if started_run:
            mlflow.end_run()
