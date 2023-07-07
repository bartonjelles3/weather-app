FROM python:3.11-slim
RUN pip install flask gunicorn requests prometheus_client
WORKDIR /query_service
COPY . .
EXPOSE 80
CMD ["gunicorn", "-b", "0.0.0.0:80", "query_service"]