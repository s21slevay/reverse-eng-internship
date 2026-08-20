# attention.py — attention from the math up. Fill in each TODO, then run the tests.
import numpy as np


def softmax(x, axis=-1):
    """Scores -> probabilities that sum to 1, computed stably.
    Stability trick: subtract the max along `axis` before exp() so nothing overflows."""
    m = np.max(x, axis=axis, keepdims=True)
    e = np.exp(x - m)
    return e / np.sum(e, axis=axis, keepdims=True)


def scaled_dot_product_attention(X, Wq, Wk, Wv, causal=False):
    """X:(T,d) tokens. Wq,Wk:(d,dk) Wv:(d,dv). Returns (output:(T,dv), weights:(T,T)).
    Q=XWq  K=XWk  V=XWv
    S = Q Kᵀ / sqrt(dk)
    weights = softmax(S)   # each row sums to 1
    output = weights V     # weighted sum of value vectors
    """
    Q = X @ Wq
    K = X @ Wk
    V = X @ Wv

    dk = Q.shape[-1]
    S = Q @ K.T / np.sqrt(dk)

    if causal:
        T = S.shape[0]
        mask = np.triu(np.ones((T, T)), k=1).astype(bool)
        S = np.where(mask, -np.inf, S)

    weights = softmax(S, axis=-1)
    output = weights @ V

    return output, weights

def batched_scaled_dot_product_attention(X, Wq, Wk, Wv, causal=False):
    """X:(B,T,d) batch of token sequences. Wq,Wk:(d,dk) Wv:(d,dv), shared across the batch.
    Returns (output:(B,T,dv), weights:(B,T,T)).
    """
    # TODO 1: project X into Q, K, V — same weights, now applied to a 3D X.
    #         Hint: X @ Wq still works here even with a leading batch dim —
    #         matmul broadcasts the (d,dk) matrix across every (T,d) slice in the batch.
    Q = X @ Wq
    K = X @ Wk
    V = X @ Wv

    
    # TODO 2: dk = Q.shape[-1]
    #         S = scores of shape (B,T,T) — each batch item needs its own T x T score matrix.
    #         Hint: use np.einsum('btd,bsd->bts', Q, K) / sqrt(dk)
    #         Read left to right: for each batch b, take token t's query and token s's key,
    #         dot them over the shared d-axis, producing a (T,T) score matrix per batch.
    dk= Q.shape[-1]
    S = np.einsum('btd, bsd->bts',Q, K)/np.sqrt(dk)

    # TODO 3: if causal, build the SAME (T,T) upper-triangular mask as before,
    #         but broadcast it across the batch dimension when applying it to S.
    if causal:
        T = S.shape[1]
        mask = np.triu(np.ones((T, T)), k=1).astype(bool)
        S = np.where(mask, -np.inf, S)
    # TODO 4: weights = softmax(S, axis=-1)  # softmax over the LAST axis still works fine in 3D
    weights = softmax(S, axis=-1)
    # TODO 5: output = weighted sum of V per batch item.
    #         Hint: np.einsum('bts,bsd->btd', weights, V)
    #         Read left to right: for each batch b and token t, sum over s (the "source" tokens),
    #         weighting each value vector V[b,s] by weights[b,t,s].
    output = np.einsum('bts,bsd->btd', weights, V)
    return output, weights


    

