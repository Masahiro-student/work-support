import matplotlib
matplotlib.use('TkAgg')
import random
import math
import numpy as np
import matplotlib.pyplot as plt

dt = 0.1
F = np.array([[1, dt],
              [0,1]])
G = np.array([[0],
              [math.sqrt(dt)]])
H = np.array([[1,0]])

xt = np.zeros((2,1))

S = np.zeros((2,2))

R = np.array([[1.0]])
Q = np.array([[1.0]])

xt[0,0]=-1
xt[1,0]=2

S[0,0]=1
S[1,1]=1

T=[]
X=[]
XT=[]
ZT=[]
measurements = [9., 10.,11.,12,13,14,15,16,17,18,19,20,20,20,19,18,17,16,15,14,13,12,11,10,9,8,7,6,5,4,3,2,1,2,3,4,5,4,3,4,5,6,7,8,7,6,5,6,7,8,9,10]
t=0
for measurement in measurements:
    D = np.linalg.pinv(H.dot(S.dot(H.T)) + R)
    K = S.dot(H.T).dot(D)

    # observation
    #zt = H.dot(x) + np.random.multivariate_normal([0], Q, 1).T
    zt = measurement
    x2 = xt + K.dot(zt - H.dot(xt))
    S2 = (np.eye(2) - K.dot(H)).dot(S)

    T.append(t)
    XT.append(x2[0,0])
    ZT.append(zt)
    xt = F.dot(x2)
    S = F.dot(S2.dot(F.T)) + G.dot(Q.dot(G.T))
    
    # update state
    #x = F.dot(x) + G.dot( np.random.multivariate_normal([0], R, 1).T )

    t = t + dt        
print(XT)
print(ZT)

#plt.plot(T,X, color='blue', linewidth=1.0, label='State Model')
plt.plot(T,XT, 'o', color='orange', linewidth=1.0, label='Estimation')
plt.plot(T,ZT, '*',color='green',label='Obvervation')
# plt.errorbar(T,XT, yerr=XTERR, capsize=5, fmt='o', color='red', ecolor='orange',label='Estimate')
plt.xlabel('T')
plt.ylabel('X')
plt.grid(True)
plt.legend()
plt.show()
plt.savefig('figure01.jpg')