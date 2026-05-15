"""
Núcleo de inteligência para Aviator AI — versão integrada.

Adaptado para integração com o código existente, mantendo compatibilidade
com o AnalysisEngine e adicionando:
- Armazenamento em SQLite
- Engenharia de atributos temporais
- Classificação de velas
- Validação walk-forward
- Previsões probabilísticas
- Auditoria de acertos
"""

from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

try:
    from sklearn.ensemble import HistGradientBoostingClassifier
    from sklearn.metrics import accuracy_score, balanced_accuracy_score, brier_score_loss, classification_report
    from sklearn.model_selection import TimeSeriesSplit
    from sklearn.pipeline import Pipeline
    from sklearn.preprocessing import StandardScaler
except Exception:
    HistGradientBoostingClassifier = None
    accuracy_score = None
    balanced_accuracy_score = None
    brier_score_loss = None
    classification_report = None
    TimeSeriesSplit = None
    Pipeline = None
    StandardScaler = None


CLASS_LABELS = ["baixa", "boa", "rosa"]
CLASS_TO_ID = {name: idx for idx, name in enumerate(CLASS_LABELS)}
ID_TO_CLASS = {idx: name for name, idx in CLASS_TO_ID.items()}


@dataclass
class PredictionConfig:
    min_rows_to_train: int = 80
    min_rows_for_backtest: int = 160
    horizon: int = 10
    random_state: int = 42
    min_confidence_to_signal: float = 0.58


def classify_multiplier(multiplier: float) -> str:
    """Classifica o multiplicador conforme a regra definida pelo usuário."""
    if multiplier < 2.0:
        return "baixa"
    if multiplier < 10.0:
        return "boa"
    return "rosa"


def safe_float(value) -> Optional[float]:
    try:
        if pd.isna(value):
            return None
        value = str(value).replace("x", "").replace(",", ".").strip()
        return float(value)
    except Exception:
        return None


class AviatorStore:
    def __init__(self, db_path: str | Path = "aviator_ai.sqlite"):
        self.db_path = Path(db_path)
        self._init_db()

    def _connect(self):
        return sqlite3.connect(self.db_path)

    def _init_db(self):
        with self._connect() as con:
            con.execute(
                """
                CREATE TABLE IF NOT EXISTS rounds (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ts TEXT NOT NULL,
                    multiplier REAL NOT NULL,
                    label TEXT NOT NULL,
                    source TEXT DEFAULT 'manual',
                    raw TEXT,
                    UNIQUE(ts, multiplier)
                )
                """
            )
            con.execute(
                """
                CREATE TABLE IF NOT EXISTS predictions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ts TEXT NOT NULL,
                    horizon INTEGER NOT NULL,
                    predicted_label TEXT NOT NULL,
                    p_baixa REAL NOT NULL,
                    p_boa REAL NOT NULL,
                    p_rosa REAL NOT NULL,
                    confidence REAL NOT NULL,
                    model_version TEXT NOT NULL,
                    resolved_round_id INTEGER,
                    actual_label TEXT,
                    hit INTEGER,
                    raw_features TEXT
                )
                """
            )

    def add_round(self, multiplier: float, ts: Optional[str] = None, source: str = "manual", raw: Optional[dict] = None):
        ts = ts or datetime.now(timezone.utc).isoformat()
        label = classify_multiplier(multiplier)
        with self._connect() as con:
            con.execute(
                "INSERT OR IGNORE INTO rounds(ts, multiplier, label, source, raw) VALUES (?, ?, ?, ?, ?)",
                (ts, float(multiplier), label, source, json.dumps(raw or {}, ensure_ascii=False)),
            )

    def add_dataframe(self, df: pd.DataFrame, multiplier_col: str = "multiplier", ts_col: Optional[str] = None, source: str = "csv"):
        for _, row in df.iterrows():
            multiplier = safe_float(row.get(multiplier_col))
            if multiplier is None or multiplier <= 0:
                continue
            ts = None
            if ts_col and ts_col in row and pd.notna(row[ts_col]):
                ts = pd.to_datetime(row[ts_col]).isoformat()
            self.add_round(multiplier=multiplier, ts=ts, source=source, raw=row.to_dict())

    def get_rounds(self) -> pd.DataFrame:
        with self._connect() as con:
            df = pd.read_sql_query("SELECT * FROM rounds ORDER BY id ASC", con)
        if df.empty:
            return df
        df["ts"] = pd.to_datetime(df["ts"], errors="coerce")
        return df

    def save_predictions(self, predictions: pd.DataFrame, raw_features: Dict):
        model_version = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
        with self._connect() as con:
            for _, row in predictions.iterrows():
                con.execute(
                    """
                    INSERT INTO predictions(
                        ts, horizon, predicted_label, p_baixa, p_boa, p_rosa,
                        confidence, model_version, raw_features
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        datetime.now(timezone.utc).isoformat(),
                        int(row["horizon"]),
                        row["predicted_label"],
                        float(row["p_baixa"]),
                        float(row["p_boa"]),
                        float(row["p_rosa"]),
                        float(row["confidence"]),
                        model_version,
                        json.dumps(raw_features, ensure_ascii=False),
                    ),
                )

    def get_predictions(self) -> pd.DataFrame:
        with self._connect() as con:
            return pd.read_sql_query("SELECT * FROM predictions ORDER BY id DESC", con)


def make_features(rounds: pd.DataFrame) -> Tuple[pd.DataFrame, pd.Series]:
    """Gera atributos usando apenas passado para prever a próxima classe."""
    df = rounds.copy().reset_index(drop=True)
    df["multiplier"] = df["multiplier"].astype(float)
    df["log_multiplier"] = np.log1p(df["multiplier"].clip(lower=0))
    df["is_baixa"] = (df["multiplier"] < 2.0).astype(int)
    df["is_boa"] = ((df["multiplier"] >= 2.0) & (df["multiplier"] < 10.0)).astype(int)
    df["is_rosa"] = (df["multiplier"] >= 10.0).astype(int)

    for lag in range(1, 16):
        df[f"lag_{lag}"] = df["log_multiplier"].shift(lag)
        df[f"lag_baixa_{lag}"] = df["is_baixa"].shift(lag)
        df[f"lag_boa_{lag}"] = df["is_boa"].shift(lag)
        df[f"lag_rosa_{lag}"] = df["is_rosa"].shift(lag)

    for window in [3, 5, 10, 20, 50]:
        shifted = df["log_multiplier"].shift(1)
        df[f"roll_mean_{window}"] = shifted.rolling(window).mean()
        df[f"roll_std_{window}"] = shifted.rolling(window).std()
        df[f"roll_max_{window}"] = shifted.rolling(window).max()
        df[f"rate_baixa_{window}"] = df["is_baixa"].shift(1).rolling(window).mean()
        df[f"rate_boa_{window}"] = df["is_boa"].shift(1).rolling(window).mean()
        df[f"rate_rosa_{window}"] = df["is_rosa"].shift(1).rolling(window).mean()

    last_rosa = -1
    last_baixa = -1
    dist_rosa = []
    dist_baixa = []
    for i, row in df.iterrows():
        dist_rosa.append(i - last_rosa if last_rosa >= 0 else np.nan)
        dist_baixa.append(i - last_baixa if last_baixa >= 0 else np.nan)
        if row["is_rosa"] == 1:
            last_rosa = i
        if row["is_baixa"] == 1:
            last_baixa = i
    df["dist_since_rosa"] = pd.Series(dist_rosa).shift(1)
    df["dist_since_baixa"] = pd.Series(dist_baixa).shift(1)

    y = df["label"].map(CLASS_TO_ID).shift(-1)
    feature_cols = [c for c in df.columns if c.startswith(("lag_", "roll_", "rate_", "dist_"))]
    X = df[feature_cols]
    data = pd.concat([X, y.rename("target")], axis=1).dropna().reset_index(drop=True)
    if data.empty:
        return pd.DataFrame(), pd.Series(dtype=int)
    return data[feature_cols], data["target"].astype(int)


def build_model(config: PredictionConfig):
    if Pipeline is None:
        raise RuntimeError("scikit-learn não está instalado.")
    return Pipeline(
        steps=[
            ("scaler", StandardScaler()),
            (
                "clf",
                HistGradientBoostingClassifier(
                    max_iter=120,
                    learning_rate=0.04,
                    l2_regularization=0.1,
                    random_state=config.random_state,
                ),
            ),
        ]
    )


def backtest_walk_forward(rounds: pd.DataFrame, config: PredictionConfig) -> Dict:
    X, y = make_features(rounds)
    if len(X) < config.min_rows_for_backtest or TimeSeriesSplit is None:
        return {
            "status": "dados_insuficientes",
            "n_samples": int(len(X)),
            "message": f"São necessárias pelo menos {config.min_rows_for_backtest} amostras úteis para backtest temporal.",
        }

    n_splits = min(5, max(2, len(X) // 80))
    tscv = TimeSeriesSplit(n_splits=n_splits)
    y_true: List[int] = []
    y_pred: List[int] = []
    prob_good_or_pink: List[float] = []
    true_good_or_pink: List[int] = []

    for train_idx, test_idx in tscv.split(X):
        model = build_model(config)
        model.fit(X.iloc[train_idx], y.iloc[train_idx])
        pred = model.predict(X.iloc[test_idx])
        proba = model.predict_proba(X.iloc[test_idx])
        y_true.extend(y.iloc[test_idx].tolist())
        y_pred.extend(pred.tolist())
        class_order = list(model.named_steps["clf"].classes_)
        idx_boa = class_order.index(CLASS_TO_ID["boa"]) if CLASS_TO_ID["boa"] in class_order else None
        idx_rosa = class_order.index(CLASS_TO_ID["rosa"]) if CLASS_TO_ID["rosa"] in class_order else None
        for i, actual in enumerate(y.iloc[test_idx].tolist()):
            p = 0.0
            if idx_boa is not None:
                p += float(proba[i, idx_boa])
            if idx_rosa is not None:
                p += float(proba[i, idx_rosa])
            prob_good_or_pink.append(p)
            true_good_or_pink.append(1 if actual in [CLASS_TO_ID["boa"], CLASS_TO_ID["rosa"]] else 0)

    acc = float(accuracy_score(y_true, y_pred))
    bacc = float(balanced_accuracy_score(y_true, y_pred))
    brier = float(brier_score_loss(true_good_or_pink, prob_good_or_pink))
    report = classification_report(
        y_true,
        y_pred,
        labels=[0, 1, 2],
        target_names=CLASS_LABELS,
        output_dict=True,
        zero_division=0,
    )
    return {
        "status": "ok",
        "n_samples": int(len(X)),
        "accuracy": acc,
        "balanced_accuracy": bacc,
        "brier_good_or_pink": brier,
        "classification_report": report,
    }


def train_and_predict(rounds: pd.DataFrame, config: PredictionConfig) -> Tuple[pd.DataFrame, Dict]:
    X, y = make_features(rounds)
    if len(X) < config.min_rows_to_train:
        return pd.DataFrame(), {
            "status": "dados_insuficientes",
            "message": f"Coletar pelo menos {config.min_rows_to_train} amostras úteis antes de exibir sinais de IA.",
            "usable_samples": int(len(X)),
        }

    model = build_model(config)
    model.fit(X, y)
    latest_features = X.iloc[[-1]].copy()
    class_order = list(model.named_steps["clf"].classes_)

    rows = []
    for h in range(1, config.horizon + 1):
        proba = model.predict_proba(latest_features)[0]
        p_map = {ID_TO_CLASS.get(cls, str(cls)): float(proba[i]) for i, cls in enumerate(class_order)}
        for label in CLASS_LABELS:
            p_map.setdefault(label, 0.0)
        predicted_label = max(CLASS_LABELS, key=lambda k: p_map[k])
        confidence = p_map[predicted_label]
        action = "OBSERVAR"
        if confidence >= config.min_confidence_to_signal and predicted_label in ["boa", "rosa"]:
            action = "SINAL COM CAUTELA"
        elif confidence >= 0.72 and predicted_label == "baixa":
            action = "EVITAR ENTRADA"
        rows.append(
            {
                "horizon": h,
                "predicted_label": predicted_label,
                "p_baixa": p_map["baixa"],
                "p_boa": p_map["boa"],
                "p_rosa": p_map["rosa"],
                "confidence": confidence,
                "action": action,
            }
        )
    return pd.DataFrame(rows), {"status": "ok", "usable_samples": int(len(X)), "feature_count": int(X.shape[1])}


def summarize_distribution(rounds: pd.DataFrame) -> pd.DataFrame:
    if rounds.empty:
        return pd.DataFrame()
    summary = rounds["label"].value_counts(normalize=True).reindex(CLASS_LABELS).fillna(0).reset_index()
    summary.columns = ["classe", "frequencia"]
    summary["percentual"] = (summary["frequencia"] * 100).round(2)
    return summary
