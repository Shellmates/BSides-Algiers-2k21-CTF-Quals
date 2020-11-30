#coding: ascii-8bit

if ARGV.count != 4
   puts "[-] Wrong usage"
   exit 1
end

res_file = File.open(ARGV[0], 'rb', &:read)

add_val = ARGV[1].include?(?x) ? ARGV[1].to_i(16) : ARGV[1].to_i

xor_val = ARGV[2].include?(?x) ? ARGV[2].to_i(16) : ARGV[2].to_i

res_file = res_file.each_codepoint.map{|c| (((c ^ xor_val) - add_val) & 0xff).chr}.join

File.open(ARGV[3], 'wb'){|f| f.write(res_file) }
