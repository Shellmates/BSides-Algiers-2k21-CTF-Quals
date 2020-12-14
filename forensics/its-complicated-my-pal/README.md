# It's Complicated My Pal

**`Author:`** [hfz](https://hfz1337.github.io)

## Description

Hey pal, I was sniffing some packets and stumbled upon some weird traffic, no idea what it is though. Could you take a look at it? It's complicated for me and I can't analyze it by myself.

## Write-up

Extract ICMP payload from the packets, piece those together and you get a `zip` file. The archive is password protected and the password is in the `rockyou` wordlist.
```bash
$ tshark -r capture.pcap -T fields -e data 'icmp && ip.src == 192.168.1.200' | tr -d '\n' | xxd -p -r > flag.zip
$ zip2john flag.zip > hash.txt
$ john hash.txt --wordlist=/usr/share/wordlists/rockyou.txt
```

Flag: `shellmates{icmp_p@yl04d_4in't_us3l3ss_4ft3r_4ll_r1gHt?}`
