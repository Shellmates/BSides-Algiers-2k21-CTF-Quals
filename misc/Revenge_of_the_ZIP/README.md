# Revenge of the ZIP

**`Author:`** [Ouxs](https://github.com/ouxs-19)

## Description

> A friend sent me this file saying it contains important data , but I couldn't extract it .  
> Can you take a look at it .  
## Write-up

### Foothold 
Taking a looking at the challenge we can see that we have four files :   
*`UnzipME50.zip`* : For someone used to play ctf this is clearly an Unzip me challenge where the flag get zipped many times but i couldn't unzip it because it's password protected .    
*`Password.png`* : Since we are looking for a password, the password.png is a very good condidate .It is a normal png file (200 x 60) but it has no sense the image looks scrambled .My guessing is it's either a rabbit hole or a scrambled picture that when re-ordering we may have a clue for the password .    
*`shift_keys`* : This is the last file , its name is very intresting and it contains a list of random number .     

### Solution
Remember The password.png that it was scrambled ? now we have file called shift keys , so it could be that the picture got shifted (horizontally or vertically) and they used these keys so all we need is to do the reverse  
```   
An additional information we have is the the picture is 200*60 and when checking the keys list we see that we have 60 lines  so it's propably columns shifting 
```
I tried to shift all columns using `width - key` (doing the reverse operation) and I got a picture containing a string .   
I tried that string as password and bingo it worked , now all what we have to do is repeating the process for another 50 times and we will get the flag , you can check that in the `solve.py`.  

### Flag 
`shellmates{z1ppity_5hiFty_th3_fl4g_1s_n0w_YouR_pr0p3rty}`

