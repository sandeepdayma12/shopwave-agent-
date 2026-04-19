FROM python:3.10-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    BACKEND_PORT=8007 \
    FRONTEND_PORT=8502

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY config ./config
COPY utils ./utils
COPY db ./db
COPY tools ./tools
COPY agents ./agents
COPY scripts ./scripts
COPY data ./data
COPY main.py app.py ./

EXPOSE 8007 8502

# Run both FastAPI and Streamlit
CMD sh -c "uvicorn main:app --host 0.0.0.0 --port ${BACKEND_PORT} & streamlit run app.py --server.address=0.0.0.0 --server.port ${FRONTEND_PORT}"