FROM python:3.13-slim

WORKDIR /app

COPY . .
RUN python -m venv .venv && python -m pip install Flask streamlit paho-mqtt firebase-admin

# Flask e Streamlit
EXPOSE 5000
EXPOSE 8000

ENTRYPOINT ["sh", "-c", "/app/entrypoint.sh"]
