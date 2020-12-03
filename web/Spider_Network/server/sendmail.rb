require 'mail'
require 'sucker_punch'
require 'dotenv'

Dotenv.load

EMAIL_ADDRESS = ENV["EMAIL_ADDRESS"]
EMAIL_PASSWORD = ENV["EMAIL_PASSWORD"]

OPTIONS = {
  :address => "smtp.gmail.com",
  :port => 465,
  :user_name => EMAIL_ADDRESS,
  :password => EMAIL_PASSWORD,
  :authentication => :login,
  :ssl => true,
  :openssl_verify_mode => 'none'
}

# email can be sent asynchronously using
# SendMailJob.perform_async(params...)
class SendMailJob
  include SuckerPunch::Job

  def perform(receiver_email:, subject: nil, text: nil, html: nil)
    Mail.defaults { delivery_method(:smtp, OPTIONS) }

    puts "Sending mail to #{receiver_email}..."

    mail = Mail.new do
      from %{"Spider's Web" <#{EMAIL_ADDRESS}>}

      to receiver_email

      subject subject

      text_part { body text }

      html_part do
        content_type 'text/html; charset=UTF-8'
        body html
      end
    end

    mail.deliver

    puts "Mail sent!"
  end
end
