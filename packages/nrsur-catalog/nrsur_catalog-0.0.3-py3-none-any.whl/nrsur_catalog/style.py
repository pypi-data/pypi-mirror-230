import matplotlib.pyplot as plt
import os


HERE = os.path.dirname(os.path.realpath(__file__))

def set_style():
    try:
        plt.style.use(f"{HERE}/style.mplstyle")
    except Exception as e:
        plt.rcParams['savefig.dpi'] = 100
        plt.rcParams['figure.dpi'] = 100
        plt.rcParams['font.size'] = 16
        plt.rcParams['font.family'] = 'sans-serif'
        plt.rcParams['font.sans-serif'] = 'Liberation Sans'
        plt.rcParams['font.cursive'] = 'Liberation Sans'
        plt.rcParams['mathtext.fontset'] = 'custom'
        plt.rcParams['axes.grid'] = False
