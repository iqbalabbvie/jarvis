# Stage 1: Build React frontend
FROM node:18 AS frontend-builder

WORKDIR /app/chat-bot-ui
COPY chat-bot-ui/package*.json ./
RUN npm install
COPY chat-bot-ui/ ./
RUN npm run build

# Stage 2: Set up Python backend
FROM python:3.11-slim

WORKDIR /app

# Copy backend files
COPY app.py script.py .env requirements.txt ./
COPY files ./files

# Copy built frontend from previous stage
COPY --from=frontend-builder /app/chat-bot-ui/build ./chat-bot-ui/build

# Install Python dependencies from requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5000

CMD ["python", "app.py"]
