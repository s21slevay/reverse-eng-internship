# multihead.py — many small attentions in parallel. Fill in the TODOs.
import numpy as np
from attention import scaled_dot_product_attention
from attention import softmax

def _attend(Q, K, V, causal=False):
    """Given already-projected Q, K, V, do just the attention math (no projection)."""
    dk = Q.shape[-1]
    S = Q @ K.T / np.sqrt(dk)
    if causal:
        T = S.shape[0]
        mask = np.triu(np.ones((T, T)), k=1).astype(bool)
        S = np.where(mask, -np.inf, S)
    weights = softmax(S, axis=-1)
    return weights @ V

def multi_head_attention(X, Wq, Wk, Wv, Wo, h, causal=False):
    """X:(T,d). Wq,Wk,Wv:(d,d). Wo:(d,d). h = number of heads (divides d).
    Split Q/K/V-space into h heads of size d//h, attend in each, concat, project with Wo.
    """
    T, d = X.shape
    dh = d // h

    # TODO 1: project once
    Q = X @ Wq   # (T, d)
    K = X @ Wk   # (T, d)
    V = X @ Wv   # (T, d)   
    # TODO 2: loop over heads, slice, run attention per head, collect outputs
    head_outputs = []
    for i in range(h):
        start = i * dh
        end = (i + 1) * dh
        Qi = Q[:, start:end]
        Ki = K[:, start:end]
        Vi = V[:, start:end]
        out_i = _attend(Qi, Ki, Vi, causal=causal)   # TODO 2, using the helper
        head_outputs.append(out_i)

    # TODO 3: concatenate
    concatenated = np.concatenate(head_outputs, axis=1)  # axis=1 glues columns side by side

    # TODO 4: project with Wo
    return concatenated @ Wo

   