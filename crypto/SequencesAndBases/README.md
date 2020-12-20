# Sequences & Bases

**`Author:`** [m0kr4n3](https://github.com/m0kr4n3)

## Description

I was playing with the bits of my secret but now i can't recover it, can u help me?

## Write-up

    - Factorize  N by using any online tool (i used SageMath)

    - Find p and q from the N factors such as p*q == n, and also p and q in certain bases (Dec2Base(p,BaseOfp),Dec2Base(q,Baseofq) resp.) each one form (sequence of the bit '1',sequence of the bit '0')  
    
    - Notice that we can not have a '0' in both sequences and the difference between the length of the 2 Sequences can't surpass 1 (so it equals to 0 or 1), and this way we eliminate a lot of possiblities

    - Bruteforce by variating the factors,the bases (they can't be more than 8) and with which bit have we to start  

Flag: `shellmates{Just_a_sm4ll_fl4g}`
