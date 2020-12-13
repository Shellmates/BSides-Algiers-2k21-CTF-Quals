require_relative 'keygen.rb'
require 'socket'

sock = TCPSocket.open('192.168.1.40', 1337)

username = sock.gets[/Your goal is to send a serial valid for "(.+?)"/, 1]

serial = Keygen.keygen(username)
puts username
puts serial
sock.puts(serial)

loop{
  line = sock.gets;
  break unless line && line !~ /^\s+$/
  puts line
}
sock.close
