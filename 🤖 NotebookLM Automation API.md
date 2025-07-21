# 🤖 NotebookLM Automation API

A Selenium-based automation system for Google NotebookLM using Docker containers, designed to work seamlessly with Google Firebase Studio.

## 🌟 Features

- ✅ **Three REST API Endpoints** for complete NotebookLM automation
- ✅ **Bypasses Google automation detection** using advanced techniques
- ✅ **Docker containerized** with selenium/standalone-chrome
- ✅ **Firebase Studio compatible** with Nix configuration
- ✅ **Thread-safe browser management** for concurrent requests
- ✅ **Automatic content generation detection** (waits 30-60 seconds)
- ✅ **Copy button automation** with content extraction
- ✅ **Authentication handling** with redirect detection
- ✅ **Web interface** for easy testing and monitoring

## 🚀 Quick Start

### Option 1: Firebase Studio (Recommended)

1. **Open in Firebase Studio:**
   ```
   https://firebase.studio/import?url=https://github.com/your-repo/notebooklm-automation
   ```

2. **The environment will automatically set up** with all dependencies

3. **Start the services:**
   ```bash
   ./start.sh
   ```

4. **Access the web interface:**
   - Open the preview URL provided by Firebase Studio
   - Or visit `http://localhost:5000`

### Option 2: Local Docker

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd notebooklm-automation
   ```

2. **Start with Docker Compose:**
   ```bash
   ./start.sh
   ```

3. **Access the application:**
   - Web Interface: http://localhost:5000
   - API Status: http://localhost:5000/api/status
   - Selenium Hub: http://localhost:4444

## 📋 API Endpoints

### 1. Open NotebookLM
```http
POST /api/open_notebooklm
Content-Type: application/json

{
  "notebooklm_url": "https://notebooklm.google.com/notebook/..."
}
```

**Response:**
```json
{
  "success": true,
  "message": "NotebookLM opened successfully",
  "current_url": "https://notebooklm.google.com/notebook/...",
  "status": "ready"
}
```

### 2. Query NotebookLM
```http
POST /api/query_notebooklm
Content-Type: application/json

{
  "query": "What are the main topics in the documents?"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Query completed successfully",
  "query": "What are the main topics in the documents?",
  "response_content": "Based on the uploaded documents...",
  "content_length": 1250,
  "generation_time_seconds": 45
}
```

### 3. Close Browser
```http
POST /api/close_browser
```

**Response:**
```json
{
  "success": true,
  "message": "Browser closed successfully"
}
```

### 4. Check Status
```http
GET /api/status
```

**Response:**
```json
{
  "browser_active": true,
  "current_url": "https://notebooklm.google.com/notebook/...",
  "status": "ready"
}
```

## 🔧 Configuration

### Environment Variables

Copy `.env.example` to `.env` and customize:

```bash
# Flask Configuration
FLASK_ENV=production
SECRET_KEY=your-secret-key-here

# Selenium Configuration
SELENIUM_HUB_URL=http://selenium-chrome:4444/wd/hub
SELENIUM_TIMEOUT=30

# NotebookLM Configuration
DEFAULT_WAIT_TIME=60
CONTENT_STABILITY_CHECKS=5
```

### Firebase Studio Configuration

The project includes `.idx/dev.nix` for Firebase Studio:

- **Automatic Docker setup**
- **Python environment configuration**
- **VS Code extensions**
- **Preview configuration**
- **Workspace automation**

## 🐳 Docker Architecture

```
┌─────────────────────┐    ┌──────────────────────┐
│   Flask API         │    │  Selenium Chrome     │
│   (Port 5000)       │◄──►│  (Port 4444)         │
│                     │    │                      │
│ - REST Endpoints    │    │ - Headless Chrome    │
│ - Web Interface     │    │ - WebDriver Hub      │
│ - CORS Enabled      │    │ - VNC Access (7900)  │
└─────────────────────┘    └──────────────────────┘
```

## 🔒 Security Features

### Automation Detection Bypass

- **Custom Chrome options** to disable automation flags
- **User agent spoofing** with realistic browser signatures
- **JavaScript execution** to remove webdriver properties
- **Realistic timing** between actions
- **Headless mode** with proper viewport settings

### Authentication Handling

- **Google sign-in detection** with appropriate error responses
- **Session persistence** support
- **Redirect handling** for authentication flows

## 📊 Monitoring & Debugging

### Health Checks

Both containers include health checks:
- **Flask API**: `GET /api/status`
- **Selenium**: `GET http://localhost:4444/wd/hub/status`

### VNC Access

Access the Chrome browser visually:
- **URL**: http://localhost:7900
- **Password**: `secret`

### Logs

View real-time logs:
```bash
docker-compose logs -f
docker-compose logs -f notebooklm-api
docker-compose logs -f selenium-chrome
```

## 🚀 Deployment

### Firebase Studio Deployment

1. **Ensure all tests pass** in the development environment
2. **Use Firebase Studio's deployment features**:
   - Backend deployment for the Flask API
   - Container deployment for the full stack

### Manual Deployment

1. **Build and push Docker images:**
   ```bash
   docker build -t notebooklm-automation .
   docker tag notebooklm-automation your-registry/notebooklm-automation
   docker push your-registry/notebooklm-automation
   ```

2. **Deploy with docker-compose:**
   ```bash
   docker-compose -f docker-compose.prod.yml up -d
   ```

## 🛠️ Development

### Local Development

1. **Set up virtual environment:**
   ```bash
   cd notebooklm-automation
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # or
   venv\Scripts\activate     # Windows
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Start Selenium container:**
   ```bash
   docker run -d -p 4444:4444 selenium/standalone-chrome
   ```

4. **Run Flask app:**
   ```bash
   python src/main.py
   ```

### Testing

Use the web interface at http://localhost:5000 to test all endpoints interactively.

## 📝 Usage Examples

### Python Client Example

```python
import requests

# Open NotebookLM
response = requests.post('http://localhost:5000/api/open_notebooklm', 
                        json={'notebooklm_url': 'https://notebooklm.google.com/notebook/...'})
print(response.json())

# Submit query
response = requests.post('http://localhost:5000/api/query_notebooklm',
                        json={'query': 'Summarize the main points'})
print(response.json())

# Close browser
response = requests.post('http://localhost:5000/api/close_browser')
print(response.json())
```

### JavaScript/Fetch Example

```javascript
// Open NotebookLM
const openResponse = await fetch('/api/open_notebooklm', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ 
    notebooklm_url: 'https://notebooklm.google.com/notebook/...' 
  })
});

// Submit query
const queryResponse = await fetch('/api/query_notebooklm', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ 
    query: 'What are the key insights?' 
  })
});

const result = await queryResponse.json();
console.log(result.response_content);
```

## 🔧 Troubleshooting

### Common Issues

1. **"Browser not initialized"**
   - Call `/api/open_notebooklm` first
   - Check if Selenium container is running

2. **"Redirected to Google sign-in"**
   - Authentication required
   - Use authenticated session or handle login

3. **"Could not find input field"**
   - NotebookLM interface may have changed
   - Check browser console for errors

4. **Docker permission issues**
   - Ensure Docker daemon is running
   - Check user permissions for Docker

### Debug Mode

Enable debug logging:
```bash
export FLASK_ENV=development
export LOG_LEVEL=DEBUG
```

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📞 Support

For issues and questions:
- Create an issue in the repository
- Check the troubleshooting section
- Review the logs for error details

---

**Note**: This tool is designed for legitimate automation purposes. Please ensure compliance with Google's Terms of Service and NotebookLM usage policies.

