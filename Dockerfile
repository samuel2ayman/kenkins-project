FROM python:3.12-slim

WORKDIR /app

RUN pip install --no-cache-dir pandas matplotlib

COPY app.py .

# Run the script then serve the report so the container stays alive
CMD python app.py --out /app/report.html && python -m http.server 8080
