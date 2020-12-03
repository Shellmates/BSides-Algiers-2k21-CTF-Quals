#
# Posts
#
# The Posts module is concerned with creating and retrieving
# posts. These are the little messages that make up communication
# on our network.
#

module Posts

  # publish_post : String Integer String Integer -> Boolean
  # Publish post from user with given content. Returns status.
  def publish_post(user, session, content)
    if content.strip.empty?
      set_error({
        :field => "Post",
        :msg => "cannot be empty"
      })
      return false
    end

    timestamp = Time.now.to_i

    stm = @db.prepare %{
      INSERT INTO Posts(User, Content, Date)
      VALUES (:user, :content, :timestamp)
    }
    stm.execute(user, content, timestamp)

    true
  end

  # get_posts : (String or NilClass) -> Array
  # Returns array of all posts from the given user or all posts
  # in the system if given nil.
  def get_posts(user)
    stm = @db.prepare %{
      SELECT Posts.User, Avatar, Content, Date
      FROM Posts
      JOIN Users ON Posts.User = Users.User
      #{"WHERE Posts.User = :user" if user}
      ORDER BY Posts.ID DESC
    }
    rs = user ? stm.execute(user) : stm.execute

    rs.map do |p|
      date_str = Time.at(p[3].to_i).strftime(DATE_FMT)
      {
        :user => p[0],
        # this is because public folder is set to STATIC_DIR
        :avatar => p[1].split(STATIC_DIR)[1],
        :content => p[2],
        :date => date_str
      }
    end
  end

  # all_posts : -> Array
  # Returns all posts.
  def all_posts
    get_posts nil
  end
end
