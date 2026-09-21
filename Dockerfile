# 1. Base Image: Python 3.11 official slim image එක භාවිතා කරමු (Lightweight සහ Production-ready)
FROM python:3.11-slim

# 2. Working Directory: Container එක ඇතුළේ අපගේ App එක තිබෙන Folder එක /app ලෙස සකසමු
WORKDIR /app

# 3. Environment Variables: Python bytecode files (.pyc) හැදීම නතර කිරීමට සහ Logs ඍජුව Terminal එකට ලබා දීමට
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 4. Copy Requirements: Docker Cache Layer optimize කිරීමට ප්‍රථමයෙන් requirements.txt පමනක් Copy කරමු
COPY requirements.txt .

# 5. Install Dependencies: requirements.txt හි ඇති සියලුම Python Libraries Install කරමු
RUN pip install --no-cache-dir -r requirements.txt

# 6. Copy Source Code: අපගේ Project එකේ ඇති සියලුම Code Files (main.py, guardrails.py) Container එකට Copy කරමු
COPY . .

# 7. Expose Port: FastAPI App එක ධාවනය වන Port 8000 Document කරමු
EXPOSE 8000

# 8. Startup Command: Container එක Start වන විට Uvicorn Web Server එක ධාවනය වන Command එක
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
