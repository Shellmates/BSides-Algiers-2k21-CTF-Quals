require './controller'
require 'sinatra'

#
# Constants
#

PORT = ENV['APP_PORT']
CTRL = Controller.new

#
# Helpers
#

# logged_in : -> Boolean
# Returns if user is logged in with correct session identifier
def logged_in?
  session[:user] and CTRL.authorize(session[:user], session[:session])
end

# login : String String -> Boolean
# Tries to login user using the provided credentials.
# Returns whether the login is successful.
def login(user, password)
  sess = CTRL.authenticate(user, password)
  if sess
    session[:user] = user
    session[:session] = sess

    # If user is admin, reset to original admin password.
    # This is to avoid ruining the challenge when one
    # manages to reset the admin password
    CTRL.set_password("admin", ADMIN_PASSWORD) if user == "admin"
  end

  !! sess
end

# get_layout : -> Symbol
# Returns correct page layout depending on login status, basically
# just changes the navigation links
def get_layout
  logged_in? ? :page_user : :page_visitor
end

#
# Configuration
#

enable :sessions

set(:public_folder, STATIC_DIR)

helpers do
  def h(text)
    Rack::Utils.escape_html text
  end
end

configure do
  set :port, PORT
end

not_found do
  status 404
  erb(:not_found, :layout => get_layout)
end

error 500 do
  status 500
  erb(:server_error, :layout => get_layout)
end

#
# Routes
#

get "/" do
  if logged_in?
    erb(
      :timeline,
      :layout => get_layout,
      :locals => {
        :user => session[:user],
        :posts => CTRL.all_posts,
        :err => CTRL.get_error
      }
    )
  else
    erb(:index, :layout => get_layout)
  end
end

# sharing posts is disabled

# post "/" do
#   if logged_in?
#     CTRL.publish_post(
#       session[:user],
#       session[:session],
#       params["content"]
#     )

#     redirect "/"
#   else
#     redirect "/login"
#   end
# end

get "/login" do
  if logged_in?
    redirect "/"
  else
    erb(
      :login,
      :layout => get_layout,
      :locals => {
        :err => CTRL.get_error
      }
    )
  end
end

post "/login" do
  if login(params["user"], params["password"])
    redirect "/"
  else
    redirect "/login"
  end
end

get "/register" do
  if logged_in?
    redirect "/"
  else
    erb(
      :register,
      :layout => get_layout,
      :locals => {
        :err => CTRL.get_error
      }
    )
  end
end

post "/register" do
  redirect "/" if logged_in?

  file = params["avatar"] ? params["avatar"]["tempfile"] : nil

  succ = CTRL.register(
    params["user"],
    params["email"],
    file,
    params["password"],
    params["confirm"]
  )

  if succ
    login(params["user"], params["password"])

    redirect "/"
  else
    redirect "/register"
  end
end

get "/logout" do
  if logged_in?
    CTRL.revoke(session[:user], session[:session])
    session.delete :user
    session.delete :session
  end

  redirect "/login"
end

get "/search" do
  locals = {
    :query => nil,
    :users => []
  }
  locals = CTRL.search(params[:q]) if params[:q]

  erb(
    :search,
    :layout => get_layout,
    :locals => locals
  )
end

get "/prefs" do
  if logged_in?
    erb(
      :prefs,
      :layout => get_layout,
      :locals => {
        :user => CTRL.get_user(session[:user])
      }
    )
  else
    redirect "/login"
  end
end

post "/prefs" do
  if logged_in?
    CTRL.update_prefs(
      session[:user],
      params["description"]
    )

    redirect "/prefs"
  else
    redirect "/login"
  end
end

get "/user/:name" do
  erb(
    :user,
    :layout => get_layout,
    :locals => {
      :user => CTRL.get_user(params["name"]),
      :posts => CTRL.get_posts(params["name"])
    }
  )
end

get "/forgot-password" do
  if not logged_in?
    erb(
      :forgot_password,
      :layout => get_layout,
      :locals => {
        :err => CTRL.get_error
      }
    )
  else
    redirect "/"
  end
end

post "/forgot-password" do
  if not logged_in?
    if CTRL.forgot_password(params["email"])
      redirect "/reset-password"
    else
      redirect "/forgot-password"
    end
  else
    redirect "/"
  end
end

get "/reset-password" do
  if not logged_in?
    erb(
      :reset_password,
      :layout => get_layout,
      :locals => {
        :err => CTRL.get_error
      }
    )
  else
    redirect "/"
  end
end

post "/reset-password" do
  if not logged_in?
    user = CTRL.reset_password(
      params["email"],
      params["token"],
      params["password"],
      params["confirm"]
    )
    
    if user
      login(user, params["password"])
      redirect "/"
    else
      redirect "/reset-password"
    end
  else
    redirect "/"
  end
end
