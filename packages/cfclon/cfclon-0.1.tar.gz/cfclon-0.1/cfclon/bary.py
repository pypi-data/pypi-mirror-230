import numpy as np
from numpy import linalg, array, linspace, log, exp, arange, pi, sin, cos, tan, arctan, sqrt
import matplotlib.pyplot as plt

def bary_coords_map(cage):
    A = [point + (1,) for point in cage]
    I = np.identity(3)
    M = linalg.solve(A, I).transpose()
    map = lambda x,y: np.dot(M,[x,y,1])
    return map
    
def draw_cage(cage):
    draw_poly(cage, color="black", marker="o")
    
def draw_poly(coords, color="blue", marker="s"):
    if isinstance(coords[0], tuple):
        points = coords
    else:
        points = []
        for i in range(0, len(coords), 2):
            points.append(tuple(coords[i:i+2]))
    poly_points = points.copy()
    if not poly_points[0] == poly_points[-1]:
        poly_points.append(poly_points[0]) #repeat the first point to create a 'closed loop'
    X, Y = zip(*poly_points) #create lists of x and y values
    #plt.rcParams["figure.figsize"] = [7.00, 5.50]
    #plt.rcParams["figure.autolayout"] = True
    xlow = min(X) - 1
    xhigh = max(X) + 1
    ylow = min(Y) - 1
    yhigh = max(Y) + 1
    plt.xlim(xlow, xhigh)
    plt.ylim(ylow, yhigh)
    plt.plot(X,Y, color=color) 
    plt.grid('on', linestyle=':')
    for x,y in poly_points[0:-1]:
        draw_point(x,y, color=color, marker=marker, markersize=4)
    return X,Y

def draw_point(x, y, color="blue", marker="s", markersize=6):
    X = [x]
    Y = [y]
    plt.plot(X, Y, marker=marker, markersize=markersize, markeredgecolor="none", markerfacecolor=color)
    label = f"({x},{y})"
    #plt.text(x, y, label, fontsize=18, fontweight='bold', horizontalalignment='center')
    #plt.plot(x, y, marker="o", markersize=8, markerfacecolor=color)
    #plt.show()

def draw_ellipse(x0, y0, a, b):
    X,Y = ellipse_coords(x0, y0, a, b)
    plt.plot(X, Y)
    return X,Y

def ellipse_coords(x0, y0, a, b, t1=0, t2=2*np.pi, num=180):
    T = linspace(t1, t2, num=num)
    X = x0 + a*cos(T)
    Y = y0 + b*sin(T)
    return X,Y

def translate_coords(coords, n, dx, dy):
    man = []
    for i in range(0, len(coords), 2):
        x,y = coords[i:i+2]
        x = x/n
        y = y/n
        x += dx
        y += dy
        man.append(x)
        man.append(y)
    s = ""
    for x in man:
        s += f"{int(x)}, "
    print(s)
    return s

def coords_to_tuples(coords):
    tcoords = []
    for i in range(0, len(coords), 2):
        x,y = coords[i:i+2]
        tcoords.append((x,y))
    return tcoords


