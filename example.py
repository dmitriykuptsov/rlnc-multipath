import numpy as np
import galois

b=[[1, 2, 78], [3, 43, 1], [23, 54, 102], [24, 55, 156]]
gf=galois.GF(2**8)
b=gf(b)
p=gf([142, 23, 11])
c=np.dot(b, p)
B=gf([b[0], b[2], b[3]])
C=gf([c[0], c[2], c[3]])
Binv=np.linalg.inv(B)
print(Binv)
print(np.dot(Binv, C))
print(p)
