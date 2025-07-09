# AI Content Moderation API

A FastAPI-based backend service for AI-powered content moderation, designed for parental control systems and browser extensions.

## 🚀 Features

- **Text Moderation**: Analyze text content for harmful or inappropriate material using OpenAI or local LLM models
- **Image Classification**: Detect NSFW content, violence, and inappropriate imagery
- **Audio Processing**: Transcribe audio and moderate the resulting text
- **CORS Support**: Ready for browser extension integration
- **Modular Architecture**: Easy to extend with new models and services
- **Health Checks**: Monitor service status and model availability

## 📁 Project Structure

```
bantai-backend/
├── app/
│   ├── main.py              # FastAPI application entry point
│   ├── config.py            # Configuration and settings
│   ├── api/                 # API endpoints
│   │   ├── text_filter.py   # Text moderation endpoints
│   │   ├── image_filter.py  # Image moderation endpoints
│   │   └── audio_filter.py  # Audio moderation endpoints
│   ├── services/            # Business logic
│   │   ├── text_analyzer.py    # Text analysis service
│   │   ├── image_classifier.py # Image classification service
│   │   └── audio_processor.py  # Audio processing service
│   └── models/
│       └── schemas.py       # Pydantic models
├── requirements.txt         # Python dependencies
├── run.sh                   # Unix startup script
├── run.bat                  # Windows startup script
└── .env.example            # Environment configuration template
```

## 🔧 Setup

### Prerequisites

- Python 3.8+
- pip or conda

### Installation

1. **Clone and navigate to the project**:

   ```bash
   cd bantai-backend
   ```

2. **Create and activate a virtual environment**:

   ```bash
   # Using venv
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate

   # Or using conda
   conda create -n bantai-backend python=3.9
   conda activate bantai-backend
   ```

3. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**:

   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Run the application**:

   ```bash
   # Using the startup script
   ./run.sh  # On Windows: run.bat

   # Or directly with uvicorn
   uvicorn app.main:app --reload
   ```

The API will be available at `http://localhost:8000`

## 📚 API Endpoints

### Text Moderation

- **POST** `/moderate/text` - Moderate text content
- **GET** `/moderate/text/health` - Text moderation health check

### Image Moderation

- **POST** `/moderate/image` - Moderate image content
- **POST** `/moderate/image/batch` - Batch image moderation
- **GET** `/moderate/image/health` - Image moderation health check

### Audio Moderation

- **POST** `/moderate/audio` - Moderate audio content
- **POST** `/moderate/audio/transcribe` - Transcribe audio only
- **GET** `/moderate/audio/health` - Audio moderation health check

### General

- **GET** `/` - API information
- **GET** `/health` - Overall health check
- **GET** `/docs` - Interactive API documentation

## 🧪 Usage Examples

### Text Moderation

```bash
curl -X POST "http://localhost:8000/moderate/text" \
  -H "Content-Type: application/json" \
  -d '{"text": "This is a sample text to moderate"}'
```

### Image Moderation

```bash
curl -X POST "http://localhost:8000/moderate/image" \
  -F "file=@image.jpg"
```

### Audio Moderation

```bash
curl -X POST "http://localhost:8000/moderate/audio" \
  -F "file=@audio.mp3"
```

## 🔌 Model Integration

The API is designed with placeholder implementations that can be easily replaced with actual AI models:

### Text Analysis (`app/services/text_analyzer.py`)

- **OpenAI Integration**: Configure `OPENAI_API_KEY` in `.env`
- **Local LLM**: Replace `analyze_with_custom_model()`
- **Hugging Face**: Use transformers library
- **Cloud APIs**: Azure Content Safety, AWS Comprehend

### Image Classification (`app/services/image_classifier.py`)

- **NSFW Detection**: Integrate ONNX models or nsfwjs
- **CLIP Integration**: OpenAI CLIP for semantic understanding
- **Cloud APIs**: Azure Computer Vision, AWS Rekognition

### Audio Processing (`app/services/audio_processor.py`)

- **Whisper Integration**: OpenAI Whisper for transcription
- **Cloud APIs**: Azure Speech Services, AWS Transcribe

## 🛡️ Security & Configuration

### Environment Variables

Key configuration options in `.env`:

```env
# API Configuration
DEBUG=false
HOST=0.0.0.0
PORT=8000

# Model Configuration
OPENAI_API_KEY=your_key_here
TEXT_CONFIDENCE_THRESHOLD=0.7
IMAGE_CONFIDENCE_THRESHOLD=0.8

# File Upload Limits
MAX_FILE_SIZE=10485760  # 10MB
```

### CORS Configuration

For browser extension support:

```python
ALLOWED_ORIGINS=["chrome-extension://*", "moz-extension://*"]
```

## 🔄 Development

### Adding New Models

1. Create service in `app/services/`
2. Add endpoint in `app/api/`
3. Update schemas in `app/models/schemas.py`
4. Include router in `app/main.py`

### Testing

```bash
# Run with reload for development
uvicorn app.main:app --reload

# Test endpoints
curl http://localhost:8000/health
```

## 📊 Monitoring

- Health check endpoints for each service
- Request logging middleware
- Error handling and reporting
- Performance metrics (processing time)

## 🚢 Deployment

### Docker (Future)

```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Production Considerations

- Use environment-specific `.env` files
- Configure proper CORS origins
- Set up reverse proxy (nginx)
- Use multiple workers for production
- Implement proper logging and monitoring

## 📝 License

This project is designed for educational and development purposes. Please ensure compliance with AI model licenses and terms of service.

## 🤝 Contributing

This is a starter template designed to be extended. Key areas for enhancement:

1. **Model Integration**: Replace dummy logic with actual AI models
2. **Performance**: Add caching, async processing, batch processing
3. **Security**: Add authentication, rate limiting, input validation
4. **Monitoring**: Add metrics, logging, alerting
5. **Testing**: Add unit tests, integration tests

## 🆘 Support

For issues and questions:

1. Check the API documentation at `/docs`
2. Review health check endpoints
3. Check application logs
4. Verify environment configuration

---

**Note**: This is a starter template with dummy implementations. Replace the placeholder model logic with actual AI models for production use.
