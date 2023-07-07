FROM python:3.11-slim
RUN pip install flask gunicorn requests prometheus_client
WORKDIR /weather
COPY . .
EXPOSE 80
CMD ["gunicorn", "-b", "0.0.0.0:80", "weather"]