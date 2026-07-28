FROM python:3.12-slim

WORKDIR /app

# Install runtime deps
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all project modules
COPY pyc64c/ pyc64c/
COPY pyc64_ui/ pyc64_ui/
COPY run_c64.py .
COPY scripts/ scripts/
COPY examples/ examples/

# Create output directory
RUN mkdir -p output

EXPOSE 8000

# Default: launch the TUI
CMD ["python3", "-m", "pyc64_ui.app"]
