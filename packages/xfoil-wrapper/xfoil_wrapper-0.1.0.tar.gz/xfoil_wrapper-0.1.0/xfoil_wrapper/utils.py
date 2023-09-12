import numpy as np


def read_polar_file(filename):
    columns = "alpha CL CD CDp CM Top_Xtr Bot_Xtr".split()
    try:
        data = np.loadtxt(filename, skiprows=12)
        if len(data.shape) == 1:
            data.shape = (1, -1)
        polar = {columns[i]: data[:, i] for i in range(len(columns))}
    except FileNotFoundError:
        polar = {x: np.array([]) for x in columns}

    return polar


def read_cp_file(filename):
    try:
        cp = np.loadtxt(filename, skiprows=3)
    except:
        cp = []

    return cp


def read_cf_file(filename):
    try:
        cf = np.loadtxt(filename, skiprows=7)
    except:
        cf = []

    return cf
