# Challenge Name

**`Author:`** [hfz](https://hfz1337.github.io)

## Description


## Write-up (pseudo writeup, might give more explanations later)

From `sftp`, we notice the presence of the `.jupyter` folder in Homer's home directory, hence, `jupyter notebook` is probably running on his machine, which listens on `localhost` port `8888` by default.  
Inside `.jupyter`, there's a configuration file that stores the password hash for the application.  
After successfully cracking that SHA1 hash (the password can be found in rockyou.txt), our goal now is to connect to `jupyter` which is not exposed to the outside.
Since we have `sftp` credentials, and sftp is basically ftp over a secure SSH channel, then we can use that to tunnel our way to the local service:

```bash
# Set a listening socket on localhost port 1337, and redirect traffic sent to this socket
# through the secure SSH channel. Our traffic will land on the remote localhost:8888, a.k.a jupyter notebook. 
ssh -p ${CHALLENGE_PORT} -TNL 1337:127.0.0.1:8888 sftp@${CHALLENGE_IP}
```

Access `http://localhost:1337` using the web browser and enter the cracked password. Once inside the application, we can start a new terminal and have command execution.

Flag: `shellmates{h4h@_y3s_l0c4lh0st_g0eS_sw0osh}`
