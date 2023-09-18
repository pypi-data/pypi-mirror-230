
"""

nerual network modeling work

w : weight matrix
x : input X matrix
y : outout Y matrix
b : the bias matrix
"""

import numpy as np 


def init_model(node_numbers, parameter_numbers, samples):
    """
    node_numbers = weight matrix rows = b matrix rows = y matrix rows
    parameter_numbers = weight matrix columns = x matrix rows
    samples = x matrix columns = y matrix columns
    b matrix columns = 1
    """
    w = np.random.randn(node_numbers, parameter_numbers) * 0.01
    b = np.zeros((node_numbers, 1))

    return w,b 

def forward_propagation(x, w, b):
    y_hat = np.matmul(w, x) + b
    return y_hat


def compute_cost(y_hat, y):
    m = y.shape[1]

    cost = np.sum((y_hat - y)**2)/(2*m)
    
    return cost


def build_model(x, y,):
    node_numbers = y.shape[0]
    parameter_numbers = x.shape[0]
    samples = x.shape[1]

    w,b = init_model(node_numbers, parameter_numbers, samples)
    y_hat = forward_propagation(x, w, b)

    cost = compute_cost(y_hat, y)

    print(cost)


# from sklearn.datasets import make_regression

# m = 30

# x, y = make_regression(n_samples=m, n_features=1, noise=20, random_state=1)

# x = x.reshape((1, m))
# y = y.reshape((1, m))

# build_model(x, y)