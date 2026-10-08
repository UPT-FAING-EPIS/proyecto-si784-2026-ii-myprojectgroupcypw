FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN useradd --create-home --uid 10001 notaryverify
USER notaryverify
EXPOSE 5500
CMD ["python", "-m", "http.server", "5500", "--bind", "0.0.0.0"]
