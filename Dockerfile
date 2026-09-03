# 1. Base Image: Use an official, lightweight Python image
FROM python:3.11-slim
# 2. Working Directory: Set the directory inside the container
WORKDIR /app
# 3. Dependencies: Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
# 4. App Code: Copy the rest of the application files
COPY . .
# 5. Port: Document that the container uses port 8000
EXPOSE 8000
# 6. Execution: The command to run when the container starts
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]