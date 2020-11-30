#coding: ascii-8bit

class String
  def as_unicode
    each_char.map{|c|c+0.chr}.join
  end
end

pattern = "\x02\x01\x01\x01\x01\x01\x01"
pattern2 = 8.times.map{ 2.chr }.join
main_exe = File.open('main.exe', 'rb', &:read)

crackme_index = main_exe.index('CRACKME'.as_unicode)
dll_index = main_exe.index('MZEZMZCX'.as_unicode)

if crackme_index == nil
  puts "[-] No CRACKME"
  exit 1
end
if dll_index == nil
  puts "[-] No MzEzMzcx"
  exit 1
end

main_exe[dll_index, 8*2] = pattern2.as_unicode
main_exe[crackme_index, 7*2] = pattern.as_unicode

File.open('main.exe','wb'){|f| f.write(main_exe) }
