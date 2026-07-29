# Regression tests for the shared-estimator bug: ModelManager's class-level
# CLASSIFICATION_MODELS entries are templates and must never be fitted.
# Before the fix, train_classification_model fitted the registry instance in
# place, so a second training run silently mutated the first run's model.

import numpy as np

from trading.ml.models import ModelManager


def _dataset(seed):
    rng = np.random.default_rng(seed)
    X = rng.normal(size=(80, 4))
    y = rng.integers(-1, 2, 80)
    return X, y


def test_registry_templates_stay_unfitted(tmp_path):
    mgr = ModelManager(model_dir=str(tmp_path))
    X, y = _dataset(1)
    mgr.train_classification_model(X, y, model_type="random_forest",
                                   feature_cols=["a", "b", "c", "d"])
    template = ModelManager.CLASSIFICATION_MODELS["random_forest"]
    assert not hasattr(template, "classes_"), \
        "registry template was fitted in place -- train must clone() it"


def test_second_training_does_not_mutate_first_model(tmp_path):
    mgr = ModelManager(model_dir=str(tmp_path))
    X1, y1 = _dataset(1)
    res1 = mgr.train_classification_model(X1, y1, model_type="random_forest",
                                          feature_cols=["a", "b", "c", "d"])
    model1 = res1["model"]
    preds_before = model1.predict(X1).copy()

    X2, y2 = _dataset(2)
    res2 = mgr.train_classification_model(X2, y2, model_type="random_forest",
                                          feature_cols=["a", "b", "c", "d"])

    assert res2["model"] is not model1, "both trainings returned the same object"
    assert (model1.predict(X1) == preds_before).all(), \
        "first model's predictions changed after training a second model"


def test_scaler_is_fresh_per_training_run(tmp_path):
    mgr = ModelManager(model_dir=str(tmp_path))
    X1, y1 = _dataset(1)
    mgr.train_classification_model(X1, y1, model_type="random_forest",
                                   feature_cols=["a", "b", "c", "d"])
    scaler1 = mgr.scaler

    X2, y2 = _dataset(2)
    mgr.train_classification_model(X2, y2, model_type="random_forest",
                                   feature_cols=["a", "b", "c", "d"])
    assert mgr.scaler is not scaler1, "scaler object reused across training runs"
