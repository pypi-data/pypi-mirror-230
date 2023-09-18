def transform(x,y):
    arr=[]
    while y:
        arr+=[x//y]
        x,y=y,x%y
    return arr

def sub_fraction(k):
    x=0
    y=1
    for i in k[::-1]:
        x,y=y,x+i*y
    return (y,x)