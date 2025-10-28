# Deployment Guide for CheckWealth

## Production Deployment

### Prerequisites
- Python 3.8+
- Web server (nginx or Apache)
- WSGI server (Gunicorn or uWSGI)
- OpenAI API key

### Setup Steps

1. **Clone and Setup**
   ```bash
   git clone https://github.com/poojanagvekar/checkwealth.git
   cd checkwealth
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   pip install gunicorn  # For production server
   ```

2. **Configure Environment**
   ```bash
   cp .env.example .env
   # Edit .env and add your OpenAI API key
   ```

3. **Create Required Directories**
   ```bash
   mkdir -p uploads
   chmod 700 uploads  # Restrict access
   ```

4. **Run with Gunicorn (Production)**
   ```bash
   gunicorn -w 4 -b 0.0.0.0:8000 app:app
   ```

5. **Nginx Configuration (Optional)**
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;
       
       location / {
           proxy_pass http://127.0.0.1:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           client_max_body_size 20M;
       }
       
       location /uploads {
           deny all;  # Protect uploaded files
       }
   }
   ```

### Environment Variables

```bash
# Required
OPENAI_API_KEY=your_api_key_here

# Optional
FLASK_ENV=production  # Don't use 'development' in production
MAX_CONTENT_LENGTH=16777216  # 16MB in bytes
```

### Security Checklist

- [ ] Set strong file permissions on uploads directory (700)
- [ ] Use HTTPS in production
- [ ] Set FLASK_ENV to production (not development)
- [ ] Never commit .env file
- [ ] Implement rate limiting
- [ ] Use a reverse proxy (nginx/Apache)
- [ ] Set up proper logging
- [ ] Implement user authentication if needed
- [ ] Regular security updates

### Docker Deployment (Optional)

Create a `Dockerfile`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn

COPY . .

RUN mkdir -p uploads && chmod 700 uploads

EXPOSE 8000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8000", "app:app"]
```

Build and run:
```bash
docker build -t checkwealth .
docker run -p 8000:8000 -e OPENAI_API_KEY=your_key -v $(pwd)/uploads:/app/uploads checkwealth
```

### Monitoring

- Monitor uploads directory size
- Set up log rotation
- Monitor API usage and costs
- Set up error alerting

### Backup

Regularly backup:
- Configuration files (.env - without secrets)
- Uploads directory (if needed)
- Generated reports

