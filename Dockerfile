FROM python:3.12-slim AS builder

WORKDIR /app

RUN pip install --no-cache-dir pandas matplotlib

COPY app.py .

RUN python app.py --out /app/report.html

FROM nginx:alpine

COPY --from=builder /app/report.html /usr/share/nginx/html/index.html

EXPOSE 80
