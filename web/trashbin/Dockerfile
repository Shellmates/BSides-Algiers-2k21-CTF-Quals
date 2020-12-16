FROM python:3.7
RUN pip install flask python-dotenv
COPY app /app
WORKDIR /app
RUN chown -R nobody:nogroup /app
USER nobody
EXPOSE 5000
ENTRYPOINT ["flask", "run"]
