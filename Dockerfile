FROM python:3.12-slim AS builder

WORKDIR /app
COPY app.py .
RUN python app.py

FROM nginx:alpine
COPY --from=builder /app/report.html /usr/share/nginx/html/index.html

EXPOSE 80
