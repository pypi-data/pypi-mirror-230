from gmpy2 import *
from Crypto.Util.number import *

def know_pqec(factors:list,e:int,c:int):
    n=1
    phi=1
    factor_l=[]
    for _ in range(len(factors)):
        n*=factors[_]
    for _ in factors:
        if _ not in factor_l:
            factor_l.append(_)
    for factor in factor_l:
        phi=phi*(factor-1)*pow(factor,factors.count(factor)-1)
    d=int(invert(e,phi))
    m=pow(c,d,n)
    return long_to_bytes(int(m))

def small_e(e:int,c:int):
    m=int(iroot(c,e)[0])
    return long_to_bytes(m)

def know_dp(n:int,e:int,dp:int,c:int):
    for k in range(1,e):
        if (e*dp-1)%k==0:
            p=(e*dp-1)//k+1
            if n%p==0:
                q=n//p
                return know_pqec([p,q],e,c)

def know_pqdpdq(p:int,q:int,dp:int,dq:int,c:int):
    n=p*q
    phi=(p-1)*(q-1)
    dd=gcd(p-1,q-1)
    d=(dp-dq)//dd*int(invert((q-1)//dd,(p-1)//dd))*(q-1)+dq
    return long_to_bytes(int(pow(c,int(d),n)))



    