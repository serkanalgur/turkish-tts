# Turkish Text-to-Speech (TTS) Service

A powerful, open-source multilingual Text-to-Speech service for **Turkish (tr-TR)**, **English**, and **Azerbaijani** using [Piper TTS](https://github.com/rhasspy/piper).

**🌐 Live Demo**: [https://turkish-tts.shot.az/](https://turkish-tts.shot.az/)

## About

Turkish TTS is a modern, web-based Text-to-Speech converter that leverages the advanced Piper TTS engine to provide natural-sounding speech synthesis. It includes intelligent processing for numbers, currencies, dates, times, and special formatting.

**Developer & Maintainer**: [Serkan Algur](https://github.com/serkanalgur)

## Features

✨ **Multi-Language Support**
- Turkish (Türkçe)
- English
- Azerbaijani (Azərbaycanca)

🎯 **Advanced Text Processing**
- Turkish number formatting (123.456 → yüzbindörtyüzellialtı)
- Currency conversion (₺, $, €, etc.)
- Date and time parsing
- Percentage handling
- Fraction conversion

🚀 **Technical Features**
- High-quality ONNX-based neural TTS
- REST API for programmatic access
- Responsive web frontend with language switcher
- Docker containerization for easy deployment
- SEO-optimized interface
- Production-ready with Gunicorn WSGI server
- Rate limiting to prevent abuse
- Modern, accessible UI with WCAG compliance
- Real-time error handling with translated messages

## Quick Start

### For Users:

1. Visit [https://turkish-tts.shot.az/](https://turkish-tts.shot.az/)
2. Select your preferred language (English, Turkish, or Azerbaijani)
3. Enter or paste text you want to convert to speech
4. Click "Generate Speech"
5. Listen to the generated audio or download it

### For Developers:

```bash
# Clone the repository
git clone https://github.com/serkanalgur/turkish-tts.git
cd turkish-tts

# Quick Docker setup
docker build -t trtts:latest .
docker run -p 5000:5000 trtts:latest

# Access the app
open http://localhost:5000
```

## User Interface Features

✨ **Multi-Language Interface**
- Seamless language switching (English, Turkish, Azerbaijani)
- Language preference saved in browser
- All UI elements translated
- Error messages in user's language

🎨 **Modern Design**
- Clean, responsive interface
- Smooth transitions and interactions
- Accessible form controls (WCAG AA compliant)
- Dark-friendly color scheme
- Mobile-friendly layout

🛡️ **User Support**
- Real-time status messages
- Clear error messages with solutions
- Sample text examples for testing
- Health check verification
- Rate limiting feedback with helpful messages

## Prerequisites

- **Docker** (recommended for quick setup)
- **Python 3.8+** (for local installation)

## Installation & Setup

### Option 1: Docker (Recommended)

```bash
# Build the Docker image
docker build -t trtts:latest .

# Run the container
docker run -p 5000:5000 --name turkish-tts trtts:latest
```

Access the web interface at: `http://localhost:5000`

### Option 2: Local Python Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Download TTS model
python backend/download_model.py

# Run the application
python backend/app.py
```

## Production Deployment

### Coolify Deployment

This project is optimized for **Coolify** deployment. The Docker container uses **Gunicorn** as the production WSGI server.

**Features:**
- ✅ Production-ready WSGI server (Gunicorn with 2 workers)
- ✅ Health check endpoint at `/health`
- ✅ Proper logging for production
- ✅ Optimized memory usage
- ✅ Port mapping: Internal 5000 → External configurable port

**Steps to deploy on Coolify:**

1. Connect your GitHub repository to Coolify
2. Select this project
3. Coolify will automatically detect the Dockerfile
4. Configure environment variables (optional):
   ```
   FLASK_ENV=production
   ```
5. Deploy!

The application will be running on the port you configure in Coolify (typically accessible via your domain).

### Local Docker Deployment

```bash
# Build the image
docker build -t trtts:latest .

# Run with Gunicorn
docker run -p 5000:5000 --name turkish-tts trtts:latest
```

Access at: `http://localhost:5000`

### Development Mode

To run in development mode (with Flask debug server):

```bash
# Set environment variable
export FLASK_ENV=development

# Run the application
python backend/app.py
```

This will start Flask's development server with debug mode enabled on port 5002.

## Project Structure

```
turkish-tts/
 backend/
    app.py              # Flask API server
    tts_engine.py       # TTS processing engine
    num2words_tr.py     # Turkish number-to-words converter
    download_model.py   # Model downloader
 frontend/
    index.html          # Web interface (multi-language)
    style.css           # Styling
    script.js           # Frontend logic
 Dockerfile              # Docker configuration
 requirements.txt        # Python dependencies
```

## API Usage

### Generate Speech

**Endpoint**: `POST /generate-speech`

**Request**:
```json
{
  "text": "Merhaba, bu bir test mesajıdır",
  "language": "tr-TR",
  "speaker": "dfki"
}
```

**Response**: Audio file (WAV format) with Content-Disposition header

**Example with cURL:**
```bash
curl -X POST http://localhost:5000/generate-speech \
  -H "Content-Type: application/json" \
  -d '{"text":"Merhaba","language":"tr-TR","speaker":"dfki"}' \
  -o speech.wav
```

### Health Check

**Endpoint**: `GET /health`

**Response**:
```json
{
  "status": "healthy",
  "model": "tr_TR-dfki-medium",
  "languages": ["tr-TR"],
  "number_handling": "advanced",
  "piper_version": "1.2.0"
}
```

## Configuration

The service runs on port `5000` in production (Docker) and port `5002` in development. 

**Environment Variables:**
- `FLASK_ENV`: Set to `production` (default) or `development`
- `WORKERS`: Number of Gunicorn workers (default: 2)
- `TIMEOUT`: Gunicorn timeout in seconds (default: 120)

## Rate Limiting

To protect the service from abuse and prevent crashes due to excessive usage, rate limiting is implemented:

- **Default Limit**: 30 requests per minute per IP address on `/generate-speech` endpoint
- **Daily Limit**: 200 requests per day per IP
- **Hourly Limit**: 50 requests per hour per IP

**Rate Limit Response** (HTTP 429):
```json
{
  "error": "Rate limit exceeded. Maximum 30 requests per minute allowed."
}
```

If you need higher limits for your use case, consider:
- Implementing IP whitelisting for trusted clients
- Using a custom Redis backend for distributed rate limiting
- Adjusting the `@limiter.limit()` decorator in `backend/app.py`

## Error Handling & User Feedback

The application provides comprehensive error handling with user-friendly messages:

| Scenario | Status | Message | Languages |
|----------|--------|---------|-----------|
| Empty text | Error | "Please enter some text" | All 3 |
| Rate limit exceeded | 429 | "Too many requests..." | All 3 |
| Service unavailable | 503 | "Service not available" | All 3 |
| Speech generated | Success | "Speech generated successfully!" | All 3 |
| Generating | Pending | "Generating speech..." | All 3 |

## Performance & Scalability

- **Single Request**: ~2-5 seconds depending on text length
- **Concurrent Requests**: 2 Gunicorn workers (configurable)
- **Memory Usage**: ~1.5-2GB per container (TTS model loaded)
- **Rate Limiting**: Default 30 req/min/IP prevents overload
- **Caching**: Browser caches generated audio in memory

## Troubleshooting

### Application won't start
```bash
# Check if port is already in use
lsof -i :5000  # On macOS/Linux
netstat -ano | findstr :5000  # On Windows

# Use different port
docker run -p 8080:5000 trtts:latest
```

### Service shows "not available"
- Check health endpoint: `curl http://localhost:5000/health`
- Check container logs: `docker logs turkish-tts`
- Verify model files downloaded: `ls backend/models/`

### Rate limit error
- Wait 1 minute before retrying
- Use different IP/proxy for testing
- Adjust rate limit settings in production

### Audio quality issues
- Try different speaker (dfki or fahrettin)
- Check text formatting (numbers, punctuation)
- Clear browser cache and reload

## Browser Support

- Chrome/Chromium ✅ (recommended)
- Firefox ✅
- Safari ✅
- Edge ✅
- Mobile browsers ✅ (tested on iOS Safari, Android Chrome) 

## Technologies Used

- **Backend**: Flask (Python)
- **WSGI Server**: Gunicorn (production) / Flask (development)
- **Rate Limiting**: Flask-Limiter
- **TTS Engine**: Piper TTS
- **Frontend**: HTML5, CSS3, JavaScript
- **Containerization**: Docker
- **Model Format**: ONNX
- **Deployment**: Coolify, Docker, Docker Compose

## Contributing

Contributions are welcome! Please feel free to submit issues and pull requests.

## License

This project is open-source and available under the MIT License.

## Support & Contact

- **GitHub**: [https://github.com/serkanalgur/turkish-tts](https://github.com/serkanalgur/turkish-tts)
- **Developer**: [Serkan Algur](https://github.com/serkanalgur/)
- **Website**: [https://turkish-tts.shot.az/](https://turkish-tts.shot.az/)

## Acknowledgments

- [Piper TTS](https://github.com/rhasspy/piper) - Excellent TTS engine
- [num2words](https://github.com/savoirfaire-dev/num2words) - Number conversion library

---

**Made with ❤️ by Serkan Algur**
