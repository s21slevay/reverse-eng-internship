# losses.py — cross-entropy, the thing training minimizes.
import numpy as np
from attention import softmax # reuse the softmax you wrote
def cross_entropy(logits, targets):
    """logits:(N,V) raw scores over a V-word vocab. targets:(N,) correct token ids.
    loss = mean over examples of -log( probability the model gave the correct token ).
    """
    N = logits.shape[0]

    p = softmax(logits)
    correct = p[np.arange(N), targets]
    mean = np.mean(-np.log(1e-12 + correct))
    return mean