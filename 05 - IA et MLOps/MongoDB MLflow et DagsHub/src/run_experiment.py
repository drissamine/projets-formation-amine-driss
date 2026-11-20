"""Run MLflow experiment with DagsHub tracking."""

import os
import mlflow
from dotenv import load_dotenv

# Load environment variables from .env file (located in backend/src)
load_dotenv(".env")

# Set MLflow tracking URI to DagsHub
# Replace <username> and <repo> with your DagsHub username and repository name
# Example: "https://dagshub.com/drissamine/my-first-repo"
mlflow_tracking_uri = os.getenv("MLFLOW_TRACKING_URI")
if not mlflow_tracking_uri:
    # Fallback: construct from DagsHub credentials (if not set in .env)
    username = os.getenv("DagsHub_username")
    repo = os.getenv("DagsHub_repo")  # You may want to add this to .env
    if username and repo:
        mlflow_tracking_uri = f"https://dagshub.com/{username}/{repo}.mlflow"
    else:
        raise ValueError("MLflow tracking URI not set and cannot be constructed from environment variables.")

mlflow.set_tracking_uri(mlflow_tracking_uri)

# Now import and run the experiment
from data_preprocessing_training import run_experiment

if __name__ == "__main__":
    # Example: using the Iris dataset
    csv_path = "../data/iris.csv"  # Adjust path as needed
    target_col = "species"         # Adjust target column name
    # Optional model parameters
    params = {
        "C": 1.0,
        "solver": "lbfgs",
        "max_iter": 200
    }

    print(f"Starting MLflow experiment with tracking URI: {mlflow_tracking_uri}")
    model, accuracy = run_experiment(csv_path, target_col, params)
    print(f"Experiment completed. Accuracy: {accuracy:.4f}")
