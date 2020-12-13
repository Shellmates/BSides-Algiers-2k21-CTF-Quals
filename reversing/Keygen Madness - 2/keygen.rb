require 'openssl'
require 'digest'

class AutoIT
  def initialize(seed)
    @rng = Random.new seed
  end

  def srand(seed)
    @rng.srand = seed
  end

  def rand(min, max)
    ((@rng.rand(0x100000000) >> 1) % (max - min + 1)) + min
  end
end

class Keygen
  SBOX1 = [20, 14, 22, 11, 24, 13, 5, 9, 8, 28, 29, 1, 23, 30, 19, 4, 3, 16, 2, 31, 10, 17, 26, 21, 12, 7, 18, 6, 0,
           25, 15, 27].freeze
  SBOX2 = [9, 24, 19, 25, 10, 12, 2, 16, 4, 14, 6, 27, 22, 21, 30, 20, 26, 15, 28, 31, 7, 3, 13, 0, 18, 8, 11, 23, 17,
           1, 29, 5].freeze

  # .each_with_index.to_a.to_h;
  INV_SBOX2 = SBOX2.each_with_index.to_a.to_h

  def self.keygen(username)
    perms = [3, 8, 4, 10, 0, 13, 6, 11, 15, 9, 1, 7, 14, 12, 2, 5]
    seed = 0
    username.each_codepoint.with_index do |c, i|
      seed ^= c << (8 * (i % 4))
    end
    autoit = AutoIT.new seed

    username += username.length.upto(15).map do |_i|
      c = autoit.rand(0, 35)
      if c < 26
        c += 97
      else
        c = c - 26 + 48
      end
      c.chr
    end.join
    username = 16.times.map { |i| username[perms[i]] }.join
    cipher = OpenSSL::Cipher.new('aes-128-ecb')
    cipher.encrypt
    cipher.key = username
    cipher.padding = 0
    aes = cipher.update(1.upto(16).map(&:chr).join).each_codepoint.to_a
    md5 = Digest::MD5.digest(username).each_codepoint.to_a
    enc = 16.times.map { |i| aes[i] ^ md5[i] }
    i = 0
    serial = []
    enc.each_slice(5) do |(x, y, z, k, t)|
      break if i == 25

      u = ((t || 0) << 32) | ((k || 0) << 24) | ((z || 0) << 16) | ((y || 0) << 8) | (x || 0)
      8.times do |v|
        c = INV_SBOX2[SBOX1[((u >> (5 * v)) & 0b11111)]]
        serial << (c < 26 ? c + 'A'.ord : c + '0'.ord - 26)
        i += 1
        break if i == 25
      end
    end
    serial.map(&:chr).each_slice(5).map(&:join) * '-'
  end
end

puts "serial(\"#{ARGV[0]}\") = #{Keygen.keygen(ARGV[0])}" if ARGV.count == 1
