# var_check.py — checking var(q·k) ≈ dk
import numpy as np

rng = np.random.default_rng(0)
for dk in [4, 64, 1024]:
    q = rng.standard_normal((10000, dk))
    k = rng.standard_normal((10000, dk))
    dots = np.sum(q * k, axis=1)
    print(f"dk={dk:5d}   measured var {dots.var():8.1f}   (your prediction: {dk})")
    from attention import softmax

# Take a big-dk score vector and compare scaled vs unscaled
dk = 1024
rng2 = np.random.default_rng(1)
q = rng2.standard_normal(dk)
k_vectors = rng2.standard_normal((5, dk))  # 5 "keys" to score against
scores = k_vectors @ q  # raw dot products, unscaled

print("\nUnscaled scores:", scores)
print("Softmax (unscaled):", softmax(scores))
print("Softmax (scaled by 1/sqrt(dk)):", softmax(scores / np.sqrt(dk)))