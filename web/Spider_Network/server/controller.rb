require 'securerandom'
require 'sqlite3'
require 'bcrypt'
require './sendmail'
require 'sucker_punch'
require 'mimemagic'
require 'dotenv'

require './modules/sessions'
require './modules/access'
require './modules/user'
require './modules/post'

Dotenv.load

#
# Constants
#

DB_NAME = ENV["DB_NAME"]
STATIC_DIR = ENV["STATIC_DIR"]
DEFAULT_AVATAR= ENV["DEFAULT_AVATAR"]
SECRET_KEY = ENV["SECRET_KEY"]
ADMIN_PASSWORD = ENV["ADMIN_PASSWORD"]

AVATAR_DIR = File.join(STATIC_DIR, "avatars")
ALLOWED_TYPES = ["image/jpeg", "image/png"]
SESSION_BITS = 32
DATE_FMT = "%d %h %G at %R"

#
# Helpers
#

# upload_avatar : File -> Boolean
# Uploads an avatar to the server (failing if the file is invalid).
# If no file is specified a default avatar is used
# Returns the path generated for the avatar (or nil on failure).
def upload_avatar(file)
  if file
    magic = MimeMagic.by_magic(file)
    # file type unknown
    return nil unless magic
    # file type not in allowed types
    return nil unless ALLOWED_TYPES.include?(magic.type)

    ext = magic.subtype
    filename = "#{SecureRandom.urlsafe_base64}.#{ext}"
    path = File.join(AVATAR_DIR, filename)

    File.open(path, "wb") { |f| f.write(file.read) }
    file.close
  # use default avatar	
  else
    path = File.join(AVATAR_DIR, DEFAULT_AVATAR)
  end

  path
end

# hash_password : String -> BCrypt::Password
# hashes the plaintext password using BCrypt
def hash_password(password)
  BCrypt::Password.create password
end

# valid_password : String String -> Boolean
# Returns whether the password hash matches a plaintext password.
def valid_password?(hashed, password)
  BCrypt::Password.new(hashed) == password
end

#
# Controller
#
# The Controller class defines a single interface to all the
# defined modules. It holds the server-side state of the
# application as well as the database handle.
#

class Controller
  include Sessions
  include Access
  include User
  include Posts

  attr_accessor :db

  def initialize
    @db = SQLite3::Database.new(DB_NAME)
    @errors = nil
    @sessions = {}
  end

  def set_error(err)
    @errors = err
  end

  def get_error
    err = @errors
    @errors = nil

    err
  end
end
