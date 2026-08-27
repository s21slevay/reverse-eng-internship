# test_losses.py
import numpy as np
from losses import cross_entropy


def test_confident_correct_prediction_near_zero_loss():
    logits = np.array([[100.0, -100.0, -100.0]])
    targets = np.array([0])
    loss = cross_entropy(logits, targets)
    assert loss < 1e-6


def test_uniform_distribution_gives_log_v():
    V = 10
    N = 5
    logits = np.zeros((N, V))
    targets = np.random.default_rng(0).integers(0, V, size=N)
    loss = cross_entropy(logits, targets)
    assert np.isclose(loss, np.log(V), atol=1e-6)