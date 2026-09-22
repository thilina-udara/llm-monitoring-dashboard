# 1. Base Image: Python 3.11 official slim image (Lightweight & Production-ready)
FROM python:3.11-slim

# 2. Security Hardening: Create a non-root user and group (Principle of Least Privilege)
RUN groupadd -g 10001 appgroup && \
    useradd -u 10001 -g appgroup -s /bin/sh -m appuser

# 3. Working Directory: Set container application directory
WORKDIR /app

# 4. Environment Variables: Prevent bytecode compilation and enforce unbuffered logs
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# 5. Copy Requirements: Optimize layer caching by copying dependencies first
COPY requirements.txt .

# 6. Install Dependencies
RUN pip install --no-cache-dir -r requirements.txt

# 7. Copy Source Code & Change Directory Ownership to non-root user
COPY . .
RUN chown -R appuser:appgroup /app

# 8. Switch to Non-Root User
USER appuser

# 9. Expose Port
EXPOSE 8000

# 10. Startup Command
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

