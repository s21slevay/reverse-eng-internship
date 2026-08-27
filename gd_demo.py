# gd_demo.py — gradient descent on a simple 1D loss, watching the learning-rate tradeoff.
import numpy as np

def loss(w):
    return (w - 3) ** 2  # minimum at w = 3

def grad(w):
    return 2 * (w - 3)  # derivative of (w-3)^2

def gradient_descent(w0, lr, steps):
    w = w0
    history = [w]
    for _ in range(steps):
        w = w - lr * grad(w)
        history.append(w)
    return history

for lr in [0.01, 0.5, 1.05]:
    history = gradient_descent(w0=0.0, lr=lr, steps=10)
    print(f"\nlr={lr}")
    for i, w in enumerate(history):
        print(f"  step {i}: w={w:.4f}, loss={loss(w):.4f}")