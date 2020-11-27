from Crypto.Util.number import long_to_bytes
from functools import reduce
from secret import flag #flag Format : Bsides{}

def Str2Bin(s):
    return ''.join(bin(ord(i))[2:].zfill(8) for i in s)

def CountSequences(binary):
    SequencesOf1=[]
    SequencesOf0=[]
    count1=0
    count0=0
    for index,bit in enumerate(binary):
        if bit == '0':
            if index!=0 and binary[index-1]=='1':
                SequencesOf1.append(count1)
                count1=0
            count0+=1
            if index==len(binary)-1 : SequencesOf0.append(count0)
        else :
            if index!=0 and binary[index-1]=='0':
                SequencesOf0.append(count0)
                count0=0
            count1+=1
            if index==len(binary)-1 : SequencesOf1.append(count1)
    return SequencesOf0,SequencesOf1

def GenerateN(SequencesOf0,SequencesOf1):
    Max = lambda l:reduce(lambda a,b: max(a,b),l)
    maximum1 = Max(SequencesOf1)
    maximum0 = Max(SequencesOf0)
    p = int(''.join(str(i) for i in SequencesOf0),maximum0+1)
    q = int(''.join(str(i) for i in SequencesOf1),maximum1+1)
    return p * q 

if __name__ == "__main__":
    binaryflag=Str2Bin(flag)

    s0,s1= CountSequences(binaryflag)

    n=GenerateN(s0,s1)

    with open('ciphertext','wb') as w :
        w.write(long_to_bytes(n)) 
