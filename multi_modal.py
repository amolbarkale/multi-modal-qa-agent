import os
import base64
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from openai import OpenAI
import requests
from PIL import Image
import io
import logging
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Initialize OpenAI client for xAI
XAI_API_KEY = os.getenv("XAI_API_KEY")
if not XAI_API_KEY:
    logger.error("XAI_API_KEY environment variable not set!")

client = OpenAI(
    api_key=XAI_API_KEY,
    base_url="https://api.x.ai/v1"
)

# For fallback text-only responses
text_client = OpenAI(
    api_key=XAI_API_KEY,
    base_url="https://api.x.ai/v1"
)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze_image():
    try:
        data = request.get_json()
        question = data.get('question', 'What do you see in this image?')
        image_url = data.get('image_url')
        image_data = data.get('image_data')  # Base64 encoded image
        
        if not image_url and not image_data:
            return jsonify({'error': 'Please provide either an image URL or upload an image'}), 400
        
        # Prepare the image for analysis
        if image_data:
            # Handle uploaded image (base64)
            try:
                # Remove data URL prefix if present
                if ',' in image_data:
                    image_data = image_data.split(',')[1]
                
                # Validate image
                img_bytes = base64.b64decode(image_data)
                img = Image.open(io.BytesIO(img_bytes))
                
                # Convert back to data URL for API
                image_url = f"data:image/jpeg;base64,{image_data}"
                
            except Exception as e:
                logger.error(f"Error processing uploaded image: {e}")
                return jsonify({'error': 'Invalid image format'}), 400
        
        elif image_url:
            # Validate URL format
            if not (image_url.startswith('http://') or image_url.startswith('https://') or image_url.startswith('data:')):
                return jsonify({'error': 'Invalid image URL format'}), 400
        
        # Try multimodal analysis first
        try:
            messages = [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": image_url,
                                "detail": "high",
                            },
                        },
                        {
                            "type": "text",
                            "text": question,
                        },
                    ],
                },
            ]

            completion = client.chat.completions.create(
                model="grok-2-vision-latest",
                messages=messages,
                temperature=0.1,
                max_tokens=1000,
            )
            
            response_text = completion.choices[0].message.content
            
            return jsonify({
                'success': True,
                'response': response_text,
                'model_used': 'grok-2-vision-latest',
                'fallback_used': False
            })
            
        except Exception as vision_error:
            logger.error(f"Vision model error: {vision_error}")
            
            # Fallback to text-only model
            try:
                fallback_prompt = f"""
                The user asked: "{question}"
                
                I was unable to analyze the provided image due to a technical issue.
                Please provide a helpful response about what I would typically look for in images when answering this type of question,
                and suggest that the user try again or provide a different image.
                """
                
                fallback_completion = text_client.chat.completions.create(
                    model="grok-2-latest",
                    messages=[{"role": "user", "content": fallback_prompt}],
                    temperature=0.1,
                    max_tokens=500,
                )
                
                fallback_response = fallback_completion.choices[0].message.content
                
                return jsonify({
                    'success': True,
                    'response': f"⚠️ **Image Analysis Unavailable**\n\n{fallback_response}",
                    'model_used': 'grok-2-latest',
                    'fallback_used': True,
                    'original_error': str(vision_error)
                })
                
            except Exception as fallback_error:
                logger.error(f"Fallback model error: {fallback_error}")
                return jsonify({
                    'error': 'Both vision and text models are currently unavailable. Please try again later.',
                    'details': str(fallback_error)
                }), 500
    
    except Exception as e:
        logger.error(f"General error: {e}")
        return jsonify({'error': f'An unexpected error occurred: {str(e)}'}), 500

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'message': 'Multimodal QA Agent is running'})

if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    os.makedirs('templates', exist_ok=True)
    
    # Check if API key is available
    if not XAI_API_KEY:
        print("⚠️  Warning: XAI_API_KEY environment variable not set!")
        print("   Please set it with: export XAI_API_KEY='your-api-key-here'")
    
    print("🚀 Starting Multimodal QA Agent...")
    print("📸 Supports: Image upload, URL input, and text questions")
    print("🧠 Models: Grok-2-Vision (primary) + Grok-2 (fallback)")
    print("🌐 Access at: http://localhost:5000")
    
    app.run(debug=True, host='0.0.0.0', port=5000)