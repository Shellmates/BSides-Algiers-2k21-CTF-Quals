require'socket';
require'base64';
class TCPSocket
	def read_until_menu
		loop{
			break if self.gets.start_with?('[_]');
		}
	end
end
puts "[*] Compiling raw_sha256.c";
`gcc raw_sha256.c -o/tmp/raw -lcrypto`;
sock = TCPSocket.open('localhost', 1337);

sock.read_until_menu;
sock.puts(?3);
sock.read_until_menu;
sock.puts(?1);
sock.puts('red0xff');

res = nil;
loop{
	res = sock.gets;
	break if res =~ /Your access token/;
}
token = res.chomp[/(?<=: ).+/];
puts "[+] token = #{token}"
data, mac = token.split(?.).map{|e| Base64.decode64(e).each_codepoint.to_a }
data_length = data.length;
if data_length % 64 < 56
	data << 0x80;
	data << 0 until data.length % 64 == 56;
	[data_length*8].pack('Q>').each_codepoint{|c| data << c};
end

additional_data = "|admin:1|expires:1981088127|";
data += additional_data.each_codepoint.to_a
data = data.map(&:chr).join

puts "[*] Executing /tmp/raw '#{mac.map{|e|e.to_s(16).rjust(2,?0)}.join}' '#{additional_data}'"
res = `/tmp/raw '#{mac.map{|e|e.to_s(16).rjust(2,?0)}.join}' '#{additional_data}'`.chomp

fake_token = Base64.encode64(data).gsub(/\s/,'') + ?. + Base64.encode64(res.each_char.each_slice(2).map{|sl|sl.join.to_i(16).chr}.join)
puts "[+] fake token = #{fake_token}";

sock.read_until_menu;
sock.puts(?2)
sock.puts(fake_token)
loop{
	res = sock.gets;
	puts res;
	break if res =~ /^\[_\]/;
}
sock.close;
