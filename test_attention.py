# test_attention.py — your correctness check.
import numpy as np
from attention import softmax, scaled_dot_product_attention

def test_softmax_sums_to_one_and_matches():
    s = softmax(np.array([1.0, 2.0, 3.0]))
    assert np.isclose(s.sum(), 1.0)
    assert np.allclose(s, [0.09003057, 0.24472847, 0.66524096])

def test_attention_shapes_and_weights():
    rng = np.random.default_rng(0)
    T, d, dk, dv = 5, 8, 4, 6
    X = rng.standard_normal((T, d))
    Wq = rng.standard_normal((d, dk)); Wk = rng.standard_normal((d, dk)); Wv = rng.standard_normal((d, dv))
    out, w = scaled_dot_product_attention(X, Wq, Wk, Wv)
    assert out.shape == (T, dv)
    assert np.allclose(w.sum(axis=1), 1.0)

def test_causal_mask_hides_the_future():
    rng = np.random.default_rng(1)
    T, d, dk, dv = 5, 8, 4, 6
    X = rng.standard_normal((T, d))
    Wq = rng.standard_normal((d, dk)); Wk = rng.standard_normal((d, dk)); Wv = rng.standard_normal((d, dv))
    _, w = scaled_dot_product_attention(X, Wq, Wk, Wv, causal=True)
    assert np.isclose(w[0, 0], 1.0) # first token attends only to itself
    assert np.allclose(np.triu(w, k=1), 0.0) # nobody attends to the future

def test_batched_matches_single_sequence():
    rng = np.random.default_rng(2)
    B, T, d, dk, dv = 3, 5, 8, 4, 6
    X = rng.standard_normal((B, T, d))
    Wq = rng.standard_normal((d, dk))
    Wk = rng.standard_normal((d, dk))
    Wv = rng.standard_normal((d, dv))

    from attention import scaled_dot_product_attention, batched_scaled_dot_product_attention
    batch_out, batch_w = batched_scaled_dot_product_attention(X, Wq, Wk, Wv, causal=True)

    # Running the single-sequence version on each batch item separately
    # should give the exact same result as the batched version.
    for b in range(B):
        single_out, single_w = scaled_dot_product_attention(X[b], Wq, Wk, Wv, causal=True)
        assert np.allclose(batch_out[b], single_out)
        assert np.allclose(batch_w[b], single_w)

def test_single_head_matches_day_one():
    rng = np.random.default_rng(3)
    T, d = 6, 8
    X = rng.standard_normal((T, d))
    Wq = rng.standard_normal((d, d))
    Wk = rng.standard_normal((d, d))
    Wv = rng.standard_normal((d, d))
    Wo = np.eye(d)

    from attention import scaled_dot_product_attention
    from multihead import multi_head_attention

    expected, _ = scaled_dot_product_attention(X, Wq, Wk, Wv, causal=True)
    actual = multi_head_attention(X, Wq, Wk, Wv, Wo, h=1, causal=True)

    assert np.allclose(expected, actual)