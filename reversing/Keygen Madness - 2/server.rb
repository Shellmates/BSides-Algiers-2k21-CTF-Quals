require_relative 'keygen'
# require_relative 'pow.rb'
require 'timeout'
require 'socket'

FLAG = 'shellmates{n3v3r_r0ll_y0ur_0wn_4nti-RE_:PP}'.freeze

CHARSET = ('a'..'z').to_a + ('A'..'Z').to_a + ('0'..'9').to_a

s = TCPServer.new 1337

puts '[+] Accepting clients'
loop do
  client = s.accept
  pid = fork{
    begin
      Timeout.timeout(3) do
        sock_domain, remote_port, remote_hostname, remote_ip = client.peeraddr
        puts "[+] New connection from #{remote_ip}:#{remote_port}"
        # if PoW.proof_of_work(client)
        username = rand(8..10).times.map { CHARSET.sample }.join
        client.puts("Your goal is to send a serial valid for \"#{username}\", you have 3 seconds to do it")
        data = client.gets
        if data.chomp == Keygen.keygen(username)
          puts "[+] Solved by #{remote_ip}:#{remote_port}"
          client.puts("[+] Congratulations, I am really surprised you made it this far!\nHere is your flag: #{FLAG}\nI hope you've enjoyed this challenge")
        else
          client.puts('[-] Wrong serial, Try it on the crackme before you run it against the server')
        end
      end
    rescue Timeout::Error
      client.puts('[-] Timeout, closing')
    rescue StandardError => e
      puts "[?] error : #{e.message}"
      puts e.backtrace
    ensure
      client.close unless client.closed?
    end
  }
  Process.detach(pid)
end
