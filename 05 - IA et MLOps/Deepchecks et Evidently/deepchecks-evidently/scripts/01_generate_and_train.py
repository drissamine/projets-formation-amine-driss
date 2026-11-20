"""Génère les données reference/current + entraîne un modèle.

But:
- créer une baseline (reference)
- simuler une dérive (current)
- produire un artefact modèle réutilisable
"""
import numpy as np
import pandas as pd
import joblib
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.linear_model import LogisticRegression

RNG = np.random.default_rng(7)

def make_df(n: int, drift: bool = False) -> pd.DataFrame:
    amt = RNG.gamma(2.0, 120.0, n)
    city_pop = RNG.integers(500, 1_500_000, n)
    gender = RNG.integers(0, 2, n)
    merchant_risk = RNG.choice(["low","med","high"], size=n, p=[0.6,0.3,0.1])

    if drift:
        amt = amt * RNG.normal(1.25, 0.08, n).clip(1.05, 1.6)
        merchant_risk = RNG.choice(["low","med","high"], size=n, p=[0.45,0.35,0.20])

    mr_map = {"low":0.0,"med":0.35,"high":0.75}
    mr = np.vectorize(mr_map.get)(merchant_risk)
    logit = (amt/450) + (1_000_000 - city_pop)/1_500_000*0.35 + gender*0.03 + mr - 1.35
    p = 1/(1+np.exp(-logit))
    y = RNG.binomial(1, p)

    return pd.DataFrame({
        "amt": amt.astype(float),
        "city_pop": city_pop.astype(int),
        "gender": gender.astype(int),
        "merchant_risk": merchant_risk.astype(str),
        "is_fraud": y.astype(int)
    })

def main():
    repo = Path(__file__).resolve().parents[1]
    data_dir = repo / "data"
    art_dir = repo / "artifacts"
    data_dir.mkdir(exist_ok=True)
    art_dir.mkdir(exist_ok=True)

    df_ref = make_df(2000, drift=False)
    df_cur = make_df(1200, drift=True)

    (data_dir / "reference.csv").write_text(df_ref.to_csv(index=False), encoding="utf-8")
    (data_dir / "current.csv").write_text(df_cur.to_csv(index=False), encoding="utf-8")

    num_features = ["amt","city_pop","gender"]
    cat_features = ["merchant_risk"]
    features = num_features + cat_features

    X = df_ref[features]
    y = df_ref["is_fraud"]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    preprocess = ColumnTransformer([
        ("num", StandardScaler(), num_features),
        ("cat", OneHotEncoder(handle_unknown="ignore"), cat_features),
    ])

    model = Pipeline([("prep", preprocess), ("clf", LogisticRegression(max_iter=2000))])
    model.fit(X_train, y_train)

    artifact = {"model": model, "features": features, "target": "is_fraud", "version": "v1.0-deepchecks-evidently"}
    joblib.dump(artifact, art_dir / "model.joblib")

    print("OK: data + modèle générés.")

if __name__ == "__main__":
    main()
