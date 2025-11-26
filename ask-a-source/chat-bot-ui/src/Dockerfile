FROM python:3.11-slim

WORKDIR /app

# Copy only the Streamlit app and requirements
COPY chat-bot-ui/src/llms.py ./llms.py
COPY requirements.txt ./requirements.txt

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose Streamlit’s default port
EXPOSE 8501

# Run Streamlit
CMD ["streamlit", "run", "llms.py", "--server.port=8501", "--server.address=0.0.0.0"]
