FROM python:3.11-slim

WORKDIR /app

# Install build essentials
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy dependencies and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project code
COPY . .

# Expose ports: 8501 for Streamlit Dashboard, 3000 for Dagster
EXPOSE 8501 3000

# Default entrypoint runs pipeline and launches Streamlit dashboard
CMD ["sh", "-c", "python run_pipeline.py && streamlit run dashboard/app.py --server.address=0.0.0.0 --server.port=8501"]
