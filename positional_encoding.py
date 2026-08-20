# positional_encoding.py — sinusoids so the model can tell positions apart.
import numpy as np


def positional_encoding(T, d):
    """(T,d) matrix. For position pos and dim i:
    angle(pos,i) = pos / 10000**(2*(i//2)/d)
    even dims -> sin(angle), odd dims -> cos(angle)
    """
    # TODO 1: pos = column vector (T,1); i = row vector (1,d)
    pos = np.arange(T).reshape(-1,1)
    i = np.arange(d).reshape(1,-1)
    # TODO 2: angle_rates = 1.0 / (10000 ** (2*(i//2)/d))
    angle_rates = 1 / (1000** (2*(i//2)/d))
    # TODO 3: angles = pos * angle_rates
    angles = pos * angle_rates
    # TODO 4: pe = zeros((T,d)); pe[:,0::2]=sin(angles[:,0::2]); pe[:,1::2]=cos(angles[:,1::2])
    pe = np.zeros((T,d))
    pe[:,0::2]=np.sin(angles[:,0::2])
    pe[:,1::2]=np.cos(angles[:,1::2])
    return pe




if __name__ == "__main__":
    pe = positional_encoding(64, 32)
    # plot it if you have matplotlib: each column is a sinusoid of a different frequency
    print(pe.shape, pe.min(), pe.max())