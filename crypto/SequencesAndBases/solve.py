from Crypto.Util.number import bytes_to_long
#from sage.all import factor # in case you have SageMath 
from itertools import combinations,permutations
from functools import reduce
from gmpy2 import digits as Dec2Base


def Bin2Str(b):
    return ''.join(chr(int(b[i:i+8],2)) for i in range(0,len(b),8))

def Factorize(n):
    expression=str(factor(n)).split('*')
    factors=[]
    for i in expression:
        if '^' in i:
            number,power=i.strip().split('^')
            for j in range(int(pwer)):factors.append(int(number))
        else:
            factors.append(int(i.strip()))
    return factors

def decrypt(c1,c2):
    for test in range(2):
        clairtext = ''
        if len(c1) == len(c2):
            for j in range(len(c1)):
                clairtext += str(test) * int(c1[j])
                clairtext += str(int(not test)) * int(c2[j])
        else :
            if len(c1) > len(c2):
                for j in range(len(c1)):
                    clairtext += str(test) * int(c1[j])
                    if j != len(c2):
                        clairtext += str(int(not test)) * int(c2[j])
            else :
                for j in range(len(c2)):
                    clairtext += str(test) * int(c2[j])
                    if j != len(c1):
                        clairtext += str(int(not test)) * int(c1[j])
        
        flag=Bin2Str(clairtext)
        if flag.startswith("shellmates") :
            print(flag)
            exit(0)

if __name__ == "__main__": 
    ct=open('ciphertext','rb').read().strip()
    n=bytes_to_long(ct)
    #n=5654655333396589573009251270272824452868045532409847035578809519921971758405056586087615745288
    
    #for this solution factors should be decomposed for exemple '2^3' we decompose it to 2,2,2 not 8 
    #factors=Factorize(n)# it's the purpose of this function


    #if you don't have it you can use online tools
    factors=[2, 2, 2, 3, 157, 179, 4339, 1112581, 53693611291973, 94333140093961, 349904234337911801671, 979906911043329098468466567737]
    
    
    for i in range(1,len(factors)):
        for comb in combinations(factors,i):
            p = reduce(lambda a,b:a*b,comb)
            q = n // p
            assert p*q == n
            for base1 in range(2,8):
                for base2 in range(2,8):
                    c1 = Dec2Base(p,base1)
                    c2 = Dec2Base(q,base2)
                    if abs(len(c1)-len(c2))>1 or ('0' in c1) or ('0' in c2):
                        continue
                    else :
                        decrypt(c1,c2)
    print("Couldn't Decrypt it !")

                        




