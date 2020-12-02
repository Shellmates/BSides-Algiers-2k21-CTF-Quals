#
# Sessions
#
# The Sessions module handles session identifiers, integers
# which uniquely identify a user on a particular client.
# Once issued, these identifiers will automatically be stored
# in a cookie on the user's browser. We keep track of which
# identifiers belong to whom.
#

module Sessions

  # issue_session : -> Integer
  # Returns cryptographically secure session identifier.
  def issue_session
    SecureRandom.random_number(2 ** SESSION_BITS)
  end

  # assign_session : String -> Integer
  # Assigns a session identifier to a user and returns it.
  def assign_session(user)
    @sessions[user] = issue_session
  end

  # revoke_session : String -> Integer
  # Revokes session of a user and returns it.
  def revoke_session(user)
    @sessions.delete user
  end
end
