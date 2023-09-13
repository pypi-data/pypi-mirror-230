from gmpy2 import *
from Crypto.Util.number import *

def know_pqec(factors=list,e=int,c=int):
    n=1
    phi=1
    factor_l=[]
    for _ in range(len(factors)):
        n*=factors[_]
    for _ in factors:
        if _ not in factor_l:
            factor_l.append(_)
    for factor in factor_l:
        phi=phi*(factors.count(factor)-1)*pow(factor,factors.count(factor)-1)
    d=int(invert(e,phi))
    m=pow(c,d,n)
    print(long_to_bytes(int(m)))
    