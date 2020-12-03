#
# Access
#
# The Access module handles user authentication and authorization.
# We verify the user's identity by matching up the session identifier
# the user gives us (as a cookie) to the identifier we issued for that
# user at login.
#

module Access

  # authenticate : String String -> (Integer or NilClass)
  # If credentials are valid, assigns session identifier to user
  # and returns identifier, otherwise returns nil.
  def authenticate(user, password)
    assign_session(user) if validate_user(user, password)
  end

  # authorize : String Integer -> Boolean
  # Returns whether user was issued given session identifier.
  def authorize(user, session)
    session == @sessions[user]
  end

  # revoke : String Integer -> (Integer or NilClass)
  # Revokes a user's session so long as given session identifier
  # is valid. Returns the session if valid, otherwise nil.
  def revoke(user, session)
    revoke_session(user) if authorize(user, session)
  end
end
