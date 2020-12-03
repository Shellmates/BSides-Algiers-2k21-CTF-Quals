FROM ruby:2.5

COPY server /server

WORKDIR /server

RUN bundle install

RUN chmod +x runserver.sh

EXPOSE 80

ENTRYPOINT ["./runserver.sh"]
