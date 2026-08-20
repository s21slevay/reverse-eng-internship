# perm_check.py — proving attention loses its blindness to order once position is added.
import numpy as np
from attention import scaled_dot_product_attention
from positional_encoding import positional_encoding

rng = np.random.default_rng(0)
T, d, dk, dv = 4, 8, 4, 6
X = rng.standard_normal((T, d))
Wq = rng.standard_normal((d, dk))
Wk = rng.standard_normal((d, dk))
Wv = rng.standard_normal((d, dv))

X_swapped = X.copy()
X_swapped[[0, 1]] = X_swapped[[1, 0]]

# WITHOUT position — should still be permutation-symmetric
out1, _ = scaled_dot_product_attention(X, Wq, Wk, Wv, causal=False)
out2, _ = scaled_dot_product_attention(X_swapped, Wq, Wk, Wv, causal=False)
print("Without position, swap-symmetric?", np.allclose(out1[[1, 0]], out2[[0, 1]]))

# WITH position added — should NOT be permutation-symmetric anymore
pe = positional_encoding(T, d)
X_pos = X + pe
X_swapped_pos = X_swapped + pe

out3, _ = scaled_dot_product_attention(X_pos, Wq, Wk, Wv, causal=False)
out4, _ = scaled_dot_product_attention(X_swapped_pos, Wq, Wk, Wv, causal=False)
print("With position, swap-symmetric?", np.allclose(out3[[1, 0]], out4[[0, 1]]))