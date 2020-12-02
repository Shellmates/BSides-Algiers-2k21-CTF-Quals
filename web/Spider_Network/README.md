# Spider Network - 0x1

**`Author:`** [LaidMalik](https://github.com/malikDaCoda)

## Description

> Come join this revolutionary new social media platform designed for Spider-People and their allies !

## Write-up

### Brief Summary (not so brief)

- on the index page, there is a github link to some of the code used for the webapp
- we find a backup zip file that contains a .git directory
- when inspecting this backup git repo, we find another branch `add-forgot-password`
- the branch contains `forgot_password.rb`, which shows that the generation of the forgot password token is not secure :
  - it generates the token using the HMAC hexdigest of a secret key and the email of the user
  - when reading `TODO.md`, we learn that the secret key is weak
  - if we can determine the secret key and the email of a user, their account can be hijacked (our target is the admin user)
- determining the secret key :
  - register an account with any valid email address
  - use forgot password feature to retrieve token from email
  - brute force the secret key to generate a token that matches
- determining the admin email address :
  - with basic enumeration, we can find it on the timeline when registering and logging into an account
- with that we can generate the admin token and log in to take the flag and ssh creds for second part of the challenge

### TODO

Flag: `shellmates{w3lc0me_2_th3_5pid3r_v3rs3}`
