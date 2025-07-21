# Firebase Studio Deployment Guide

## 🚀 Deploying NotebookLM Automation on Firebase Studio

This guide provides step-by-step instructions for deploying the NotebookLM Automation system on Google Firebase Studio.

## 📋 Prerequisites

1. **Google Account** with access to Firebase Studio
2. **Firebase Studio workspace** (free tier available)
3. **Basic understanding** of Docker and REST APIs

## 🔧 Deployment Steps

### Step 1: Import Project to Firebase Studio

1. **Open Firebase Studio**: https://firebase.studio/
2. **Create New Workspace** or use existing one
3. **Import from Git**:
   - Use the repository URL
   - Firebase Studio will automatically detect the `.idx/dev.nix` configuration

### Step 2: Automatic Environment Setup

Firebase Studio will automatically:
- ✅ Install Python 3.11 and dependencies
- ✅ Set up Docker and docker-compose
- ✅ Configure VS Code extensions
- ✅ Create virtual environment
- ✅ Install Python packages from requirements.txt

### Step 3: Manual Configuration (if needed)

If automatic setup doesn't complete:

```bash
# Install dependencies
cd /workspace/notebooklm-automation
python -m pip install -r requirements.txt

# Make scripts executable
chmod +x start.sh stop.sh

# Create environment file
cp .env.example .env
```

### Step 4: Start Services

```bash
# Start Docker services
./start.sh

# Or manually with docker-compose
docker-compose up --build -d
```

### Step 5: Test the Deployment

1. **Check service status**:
   ```bash
   curl http://localhost:5000/api/status
   ```

2. **Open web interface**:
   - Use Firebase Studio's preview feature
   - Or access via the provided URL

### Step 6: Deploy to Production

#### Option A: Firebase App Hosting

1. **Configure for deployment**:
   ```bash
   # Update requirements.txt
   pip freeze > requirements.txt
   ```

2. **Deploy backend**:
   - Use Firebase Studio's deployment panel
   - Select "Deploy Backend"
   - Choose Flask framework

#### Option B: Google Cloud Run

1. **Build container**:
   ```bash
   docker build -t gcr.io/your-project/notebooklm-automation .
   ```

2. **Push to registry**:
   ```bash
   docker push gcr.io/your-project/notebooklm-automation
   ```

3. **Deploy to Cloud Run**:
   - Use Firebase Studio's Cloud Run integration
   - Configure environment variables
   - Set up external access

## 🔧 Firebase Studio Specific Configuration

### Nix Configuration (`.idx/dev.nix`)

The project includes a comprehensive Nix configuration:

```nix
{
  # Docker support
  packages = [ pkgs.docker pkgs.docker-compose ];
  
  # Python environment
  packages = [ pkgs.python311 ];
  
  # Preview configuration
  idx.previews.web = {
    command = ["python" "src/main.py"];
    manager = "web";
  };
}
```

### Workspace Automation

Firebase Studio will automatically:
- Install dependencies on workspace creation
- Start Docker daemon
- Pull required Docker images
- Set up development environment

## 🌐 External Access Configuration

### For Development

Firebase Studio provides automatic preview URLs:
- **Web Interface**: Available via preview panel
- **API Endpoints**: Accessible from external browsers
- **WebSocket Support**: For real-time features

### For Production

1. **Enable external access**:
   ```bash
   # Ensure Flask listens on 0.0.0.0
   app.run(host='0.0.0.0', port=5000)
   ```

2. **Configure CORS**:
   ```python
   from flask_cors import CORS
   CORS(app)  # Already configured in the project
   ```

3. **Set up custom domain** (optional):
   - Use Firebase Studio's domain configuration
   - Configure DNS settings

## 🔒 Security Considerations

### Firebase Studio Environment

1. **No sudo access**: All configurations use Nix package manager
2. **Sandboxed environment**: Containers run in isolated environment
3. **Resource limits**: Respect Firebase Studio's resource quotas

### Production Security

1. **Environment variables**:
   ```bash
   # Set in Firebase Studio environment
   FLASK_ENV=production
   SECRET_KEY=your-secure-secret-key
   ```

2. **API rate limiting**:
   - Implement rate limiting for production
   - Use Firebase Studio's built-in protections

3. **Authentication**:
   - Add API key authentication if needed
   - Integrate with Firebase Auth

## 📊 Monitoring and Logging

### Firebase Studio Monitoring

1. **Built-in logs**: Available in Firebase Studio console
2. **Performance monitoring**: Use Firebase Studio's monitoring tools
3. **Error tracking**: Automatic error reporting

### Custom Monitoring

```python
# Add to Flask app
import logging
logging.basicConfig(level=logging.INFO)

@app.route('/health')
def health_check():
    return {'status': 'healthy', 'timestamp': time.time()}
```

## 🚀 Scaling Considerations

### Firebase Studio Limits

- **Workspace limits**: 3 free workspaces per user
- **Resource limits**: CPU and memory constraints
- **Network limits**: Bandwidth restrictions

### Scaling Solutions

1. **Upgrade to Premium**: More workspaces and resources
2. **Deploy to Cloud Run**: Auto-scaling capabilities
3. **Use Firebase App Hosting**: Integrated scaling

## 🛠️ Troubleshooting

### Common Firebase Studio Issues

1. **Docker not starting**:
   ```bash
   sudo service docker start
   ```

2. **Permission issues**:
   ```bash
   # Check file permissions
   ls -la start.sh
   chmod +x start.sh
   ```

3. **Port conflicts**:
   ```bash
   # Check running services
   netstat -tulpn | grep :5000
   ```

### Debug Mode

Enable debug logging in Firebase Studio:
```bash
export FLASK_ENV=development
export LOG_LEVEL=DEBUG
python src/main.py
```

## 📞 Support

For Firebase Studio specific issues:
- **Firebase Studio Documentation**: https://firebase.google.com/docs/studio
- **Community Forum**: Firebase Studio community
- **Support Tickets**: Firebase Studio support

For project-specific issues:
- Check the main README.md
- Review application logs
- Test locally with Docker

---

**Note**: Firebase Studio is in preview. Features and limitations may change. Always test thoroughly before production deployment.

