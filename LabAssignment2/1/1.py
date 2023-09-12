import numpy as np

M = np.arange(5, 21)
print(M)

print("")

M = np.arange(5,21).reshape(4, 4)
print(M)

print("")

M[1:3,1:3] = 0
print(M)

print("")

M = M @ M

print(M)

print("")

v = M[0,0:4]

print(np.sqrt(v@v))

