#
# User
#
# The User module handles all user-creating, modifying, and
# data retrieval actions.
#

module User

  # search : String -> Hash
  # Returns a hash containing the search query and the set of
  # users matching the query (by name or description).
  def search(user_query)
    stm = @db.prepare %{
      SELECT User, Avatar, Description
      FROM Users
      WHERE User LIKE :query OR
      Description LIKE :query
    }
    rs = stm.execute("%#{user_query}%")

    users = rs.map do |u|
      {
        :name => u[0],
        # this is because public folder is set to STATIC_DIR
        :avatar => u[1].split(STATIC_DIR)[1],
        :description => u[2]
      }
    end

    {
      :query => user_query,
      :users => users
    }
  end

  # register : String String File String String -> Boolean
  # Registers a new user if they don't already exist,
  # username and password are not empty, and
  # password and confirm password match. Returns status.
  def register(user, email, file, password, confirm)
    if user.strip.empty?
      set_error({
        :field => "User",
        :msg => "cannot be empty"
      })
      return false
    elsif password.strip.empty?
      set_error({
        :field => "Password",
        :msg => "cannot be empty"
      })
      return false
    elsif password != confirm
      set_error({
        :field => "Password",
        :msg => "passwords don't match"
      })
      return false
    end

    # verify that username and email are not already taken
    if @db.get_first_row(%{
      SELECT 1
      FROM Users
      WHERE User = :user OR Email = :email
    }, user, email)
      set_error({
        :field => "User/Email",
        :msg => "already taken"
      })
      return false
    end
    
    avatar_path = upload_avatar(file)
    # invalid file
    if not avatar_path
      set_error({
        :field => "Avatar",
        :msg => "wrong image type (allowed types: jpg, png)"
      })
      return false
    end

    stm = @db.prepare %{
      INSERT INTO Users(User, Email, Password, Avatar)
      VALUES (:user, :email, :hashed_password, :avatar_path)
    }
    hashed_password = hash_password(password)
    stm.execute(user, email, hashed_password, avatar_path)

    true
  end

  # get_user: String -> (Hash or NilClass)
  # Gets user preferences of given user or nil if non-existent
  def get_user(user)
    row = @db.get_first_row(%{
      SELECT Avatar, Description
      FROM Users
      WHERE User = :user
    }, user)

    return nil unless row

    {
      # this is because public folder is set to STATIC_DIR
      :avatar => row[0].split(STATIC_DIR)[1],
      :description => row[1]
    }
  end

  # validate_user: String String -> Boolean
  # Validates the credentials of the user. Returns true if
  # the credentials are valid, otherwise false
  def validate_user(user, password)
    row = @db.get_first_row(%{
      SELECT Password
      FROM Users
      WHERE User = :user
    }, user)

    # User doesn't exist
    if not row
      set_error({
        :field => "User/Password",
        :msg => "invalid credentials"
      })
      return false
    end

    hashed = row[0]
    valid = valid_password?(hashed, password)

    set_error({
      :field => "User/Password",
      :msg => "invalid credentials"
    }) unless valid

    valid
  end

  # update_prefs : String Integer String Integer -> Boolean
  # Update preferences of given user returning success status.
  def update_prefs(user, description)
    stm = @db.prepare %{
      UPDATE Users
      SET Description = :description
      WHERE User = :user
    }
    stm.execute(description, user)

    true
  end

  # set_password : String String -> Boolean
  # sets password for user if it exists.
  # Returns status.
  def set_password(user, password)
    # verify that user exists in the database
    row = @db.get_first_row(%{
      SELECT 1
      FROM Users
      WHERE User = :user
    }, user)
    return false unless row

    hashed_password = hash_password(password)

    stm = @db.prepare %{
      UPDATE Users
      SET Password = :hashed_password
      WHERE User = :user
    }
    stm.execute(hashed_password, user)

    true
  end

  # forgot_password : String -> Boolean
  # sends an email containing a token to reset the password.
  # Returns status.
  def forgot_password(email)
    # verify that the email address exists in the database
    row = @db.get_first_row(%{
      SELECT 1
      FROM Users
      WHERE Email = :email
    }, email)

    if not row
      set_error({
        :field => "Email",
        :msg => "invalid email"
      })
      return false
    end

    # generate password reset token
    token = OpenSSL::HMAC.hexdigest("SHA256", SECRET_KEY, email)

    SendMailJob.perform_async(
      receiver_email: email,
      subject: "Password Reset",
      html: <<-EOF
      <h1>Spider's Web : Password Reset</h1>
      <h3>Your token is : #{token}</h3>
      EOF
    )

    true
  end

  # reset_password : String String String String -> Boolean
  # resets the password if the email and token are valid,
  # password is not empty, and password matches confirm.
  # Returns the user who's password was reset (or nil on failure).
  def reset_password(email, token, password, confirm)
    if password.strip.empty?
      set_error({
        :field => "Password",
        :msg => "cannot be empty"
      })
      return nil
    elsif password != confirm
      set_error({
        :field => "Password",
        :msg => "passwords don't match"
      })
      return nil
    end

    # verify that the email address exists in the database
    row = @db.get_first_row(%{
      SELECT User
      FROM Users
      WHERE Email = :email
    }, email)

    if not row
      set_error({
        :field => "Email/Token",
        :msg => "invalid"
      })
      return nil
    end

    user = row[0]

    # verify that the token is valid
    if token != OpenSSL::HMAC.hexdigest("SHA256", SECRET_KEY, email)
      set_error({
        :field => "Email/Token",
        :msg => "invalid"
      })
      return nil
    end

    set_password(user, password)

    user
  end
end
