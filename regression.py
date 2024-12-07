from scipy.optimize import least_squares
import numpy as np
import matplotlib.pyplot as plt

path = "C://Users/rodri/Documents/code/chimie/Imersion/app/data.txt"
f = open(path, "r")
t,I = f.read().split('\n#\n')

data = np.array(I.split('\n'),dtype=np.float64)
time = np.array(t.split('\n'),dtype=np.float64)

def fun(x,t,y):
    return x[0] + x[1]*np.exp(x[2]*t) - y

def gen_data(t, a, b, c):
    return a + b * np.exp(t * c)


x0 = np.array([1.0, 1.0, 0.0])

res_lsq = least_squares(fun, x0, args=(time, data))
y_lsq = gen_data(time, *res_lsq.x)

print('tau = ',-1/res_lsq.x[2])

plt.plot(time, data, 'o')
plt.plot(time, y_lsq, label='regression')
plt.xlabel("t")
plt.ylabel("I")
plt.legend()
plt.show()