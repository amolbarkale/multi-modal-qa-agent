# 🤖 Multimodal QA Agent

A sophisticated web application that combines image analysis with natural language processing to answer questions about uploaded images. Built with Flask, JavaScript, and powered by xAI's Grok-2-Vision model.

![Multimodal QA Agent](https://img.shields.io/badge/AI-Multimodal%20QA-blue?style=for-the-badge&logo=openai)
![Python](https://img.shields.io/badge/Python-3.8+-green?style=for-the-badge&logo=python)
![Flask](https://img.shields.io/badge/Flask-3.0.0-red?style=for-the-badge&logo=flask)

## ✨ Features

### 🎯 Core Functionality
- **Image Upload**: Drag & drop interface for local image files
- **URL Input**: Direct image URL loading with validation
- **Smart Questions**: AI-powered analysis of visual content
- **Responsive Design**: Works perfectly on desktop and mobile

### 🧠 AI Capabilities
- **Primary Model**: Grok-2-Vision for multimodal analysis
- **Fallback Mode**: Grok-2 text model when vision fails
- **Real-time Processing**: Fast image analysis and response generation
- **Error Handling**: Robust error management with user feedback

### 🎨 User Experience
- **Modern UI**: Beautiful gradient design with smooth animations
- **Quick Questions**: Pre-built prompts for common queries
- **Sample Images**: Test with curated example images
- **Keyboard Shortcuts**: Efficient navigation and interaction

## 🚀 Getting Started

### Prerequisites
- Python 3.8 or higher
- xAI API key (get one at [x.ai](https://x.ai))

### Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd multi-modal-qa-agent
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   # Windows
   set XAI_API_KEY=your_xai_api_key_here
   
   # macOS/Linux
   export XAI_API_KEY=your_xai_api_key_here
   ```

4. **Run the application**
   ```bash
   python multi_modal.py
   ```

5. **Open your browser**
   Navigate to `http://localhost:5000`

## 🎯 Usage Examples

### Example 1: NASA Space Telescope Image
**Question**: "What celestial objects can you identify in this image?"
**Response**: Detailed analysis of stars, galaxies, and cosmic phenomena visible in the Webb telescope image.

### Example 2: Everyday Objects
**Question**: "What objects do you see and what might someone be doing?"
**Response**: Identification of books, coffee cup, and inference about reading/studying activity.

### Example 3: Animal Recognition
**Question**: "What breed is this dog and what are its characteristics?"
**Response**: Breed identification, physical characteristics, and behavioral traits.

## 🛠️ Technical Architecture

### Backend (Flask)
- **REST API**: Clean endpoints for image analysis
- **Image Processing**: PIL for image validation and processing
- **Error Handling**: Comprehensive error management
- **Logging**: Detailed logging for debugging

### Frontend (Vanilla JavaScript)
- **Modern ES6+**: Clean, maintainable code
- **Responsive Design**: Mobile-first approach
- **User Interactions**: Drag & drop, keyboard shortcuts
- **Real-time Feedback**: Loading states and error messages

### AI Integration
- **xAI Grok-2-Vision**: Primary multimodal model
- **xAI Grok-2**: Text-only fallback model
- **OpenAI Client**: Unified API interface
- **Robust Fallback**: Graceful degradation when vision fails

## 📁 Project Structure

```
multi-modal-qa-agent/
├── multi_modal.py          # Flask backend server
├── templates/
│   └── index.html          # Main HTML template
├── static/
│   ├── script.js           # Frontend JavaScript
│   └── styles.css          # CSS styling
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## 🎛️ API Endpoints

### `POST /analyze`
Analyzes an image and answers questions about it.

**Request Body:**
```json
{
    "question": "What do you see in this image?",
    "image_url": "https://example.com/image.jpg",
    "image_data": "data:image/jpeg;base64,..."
}
```

**Response:**
```json
{
    "success": true,
    "response": "I can see a beautiful landscape with mountains...",
    "model_used": "grok-2-vision-latest",
    "fallback_used": false
}
```

### `GET /health`
Health check endpoint.

**Response:**
```json
{
    "status": "healthy",
    "message": "Multimodal QA Agent is running"
}
```

## 🔧 Configuration

### Environment Variables
- `XAI_API_KEY`: Your xAI API key (required)

### Model Configuration
- **Vision Model**: `grok-2-vision-latest`
- **Text Model**: `grok-2-latest`
- **Temperature**: 0.1 (balanced creativity/accuracy)
- **Max Tokens**: 1000 (vision), 500 (fallback)

## 🚀 Deployment

### Local Development
```bash
python multi_modal.py
```

### Production Deployment
For production, consider using:
- **Gunicorn**: `gunicorn -w 4 multi_modal:app`
- **Docker**: Containerized deployment
- **Cloud Platforms**: Heroku, AWS, Google Cloud

## 🧪 Testing

### Manual Testing
1. Upload different image types (JPEG, PNG, GIF)
2. Test with various image sizes
3. Try different question types
4. Test URL loading functionality
5. Verify fallback behavior

### Sample Test Cases

| Image Type | Question | Expected Response |
|------------|----------|------------------|
| Landscape | "Describe the scenery" | Detailed landscape description |
| Portrait | "What emotions do you see?" | Emotion analysis |
| Food | "What ingredients might be used?" | Ingredient identification |
| Text/Document | "What does this document say?" | Text extraction and summary |

## 🐛 Troubleshooting

### Common Issues

1. **API Key Error**
   - Ensure `XAI_API_KEY` is set correctly
   - Verify API key is valid and active

2. **Image Loading Failed**
   - Check image URL accessibility
   - Verify image format is supported
   - Ensure file size is under 10MB

3. **Connection Errors**
   - Check internet connectivity
   - Verify xAI API status
   - Try again after a few moments

## 🔄 Future Enhancements

- [ ] **Bounding Box Visualization**: Draw detection boxes on images
- [ ] **Multi-language Support**: Internationalization
- [ ] **Batch Processing**: Multiple images at once
- [ ] **Image Editing**: Basic image preprocessing
- [ ] **Export Results**: Save analysis results
- [ ] **User Authentication**: Personal analysis history

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **xAI** for providing the Grok-2-Vision API
- **OpenAI** for the excellent client library
- **Flask** community for the fantastic web framework
- **Unsplash** for sample images

## 📞 Support

For support, please open an issue on GitHub or contact the development team.

---

**Built with ❤️ for the AI community** # multi-modal-qa-agent
