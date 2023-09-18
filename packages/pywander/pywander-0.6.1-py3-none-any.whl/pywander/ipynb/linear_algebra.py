"""
linear algebra

m : the linear equation system left matrix 
b : the linear equation right b array 
am : [argumented matrix] combine m and b to a entire linear system matrix 
v : a vector

"""

import numpy as np


def swap_rows(m, row_num_1, row_num_2):
    """
    Gaussian elimination basic operation 1
    swap two rows
    """
    m_new = m.copy()
    m_new[[row_num_1, row_num_2]] = m_new[[row_num_2, row_num_1]]
    return m_new


def multiply_row(m, row_num, row_num_multiple):
    """
    Gaussian elimination basic operation 2
    """
    m_new = m.copy()
    m_new[row_num] = m_new[row_num] * row_num_multiple
    return m_new


def add_rows(m, row_num_1, row_num_2, row_num_1_multiple):
    """
    Gaussian elimination basic operation 3
    """
    m_new = m.copy()
    m_new[row_num_2] = row_num_1_multiple * m_new[row_num_1] + m_new[row_num_2]
    return m_new


def solve(m, b):
    """
    solve the linear equation system
    """
    return np.linalg.solve(m, b)


def determinant(m):
    """
    calc the determinant
    """
    return np.linalg.det(m)


def combine_system(m, b):
    """
    combine m and b to system
    """
    return np.hstack((m, b.reshape(b.size, 1)))


def l2norm(v):
    """
    get the l2 norm of a vector
    """
    return np.linalg.norm(v)


def dot_product(v1, v2):
    """
    get the dot product of two vectors
    """
    return np.dot(v1, v2)

def matrix_multiplication(m1, m2):
    """
    notice: ndim=1 array is a vector, can not apply here.
    """
    return np.matmul(m1, m2)