// DOM Elements
const uploadArea = document.getElementById('uploadArea');
const imageUpload = document.getElementById('imageUpload');
const imageUrl = document.getElementById('imageUrl');
const loadUrlBtn = document.getElementById('loadUrlBtn');
const imagePreview = document.getElementById('imagePreview');
const previewImg = document.getElementById('previewImg');
const clearImageBtn = document.getElementById('clearImageBtn');
const questionInput = document.getElementById('questionInput');
const analyzeBtn = document.getElementById('analyzeBtn');
const resultsSection = document.getElementById('resultsSection');
const errorSection = document.getElementById('errorSection');
const responseContent = document.getElementById('responseContent');
const modelInfo = document.getElementById('modelInfo');
const fallbackIndicator = document.getElementById('fallbackIndicator');
const errorMessage = document.getElementById('errorMessage');

// State
let currentImageData = null;
let currentImageUrl = null;

// Initialize app
document.addEventListener('DOMContentLoaded', function() {
    setupEventListeners();
    setupQuickQuestions();
    setupSampleImages();
});

function setupEventListeners() {
    // File upload events
    uploadArea.addEventListener('click', () => imageUpload.click());
    uploadArea.addEventListener('dragover', handleDragOver);
    uploadArea.addEventListener('dragleave', handleDragLeave);
    uploadArea.addEventListener('drop', handleDrop);
    imageUpload.addEventListener('change', handleFileSelect);
    
    // URL input events
    loadUrlBtn.addEventListener('click', handleUrlLoad);
    imageUrl.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') handleUrlLoad();
    });
    
    // Clear image
    clearImageBtn.addEventListener('click', clearImage);
    
    // Question input
    questionInput.addEventListener('input', validateForm);
    
    // Analyze button
    analyzeBtn.addEventListener('click', analyzeImage);
    
    // Enter key in question input
    questionInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            if (!analyzeBtn.disabled) {
                analyzeImage();
            }
        }
    });
}

function setupQuickQuestions() {
    const quickBtns = document.querySelectorAll('.quick-btn');
    quickBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const question = btn.getAttribute('data-question');
            questionInput.value = question;
            validateForm();
        });
    });
}

function setupSampleImages() {
    const sampleItems = document.querySelectorAll('.sample-item');
    sampleItems.forEach(item => {
        item.addEventListener('click', () => {
            const url = item.getAttribute('data-url');
            imageUrl.value = url;
            handleUrlLoad();
        });
    });
}

// Drag and drop handlers
function handleDragOver(e) {
    e.preventDefault();
    uploadArea.classList.add('dragover');
}

function handleDragLeave(e) {
    e.preventDefault();
    uploadArea.classList.remove('dragover');
}

function handleDrop(e) {
    e.preventDefault();
    uploadArea.classList.remove('dragover');
    
    const files = e.dataTransfer.files;
    if (files.length > 0 && files[0].type.startsWith('image/')) {
        handleFileUpload(files[0]);
    } else {
        showError('Please drop a valid image file.');
    }
}

function handleFileSelect(e) {
    const file = e.target.files[0];
    if (file && file.type.startsWith('image/')) {
        handleFileUpload(file);
    }
}

function handleFileUpload(file) {
    // Validate file size (10MB limit)
    if (file.size > 10 * 1024 * 1024) {
        showError('Image file is too large. Please use an image smaller than 10MB.');
        return;
    }
    
    const reader = new FileReader();
    reader.onload = function(e) {
        currentImageData = e.target.result;
        currentImageUrl = null;
        displayImagePreview(e.target.result);
        imageUrl.value = ''; // Clear URL input
        validateForm();
    };
    reader.onerror = function() {
        showError('Error reading the image file. Please try again.');
    };
    reader.readAsDataURL(file);
}

function handleUrlLoad() {
    const url = imageUrl.value.trim();
    
    if (!url) {
        showError('Please enter an image URL.');
        return;
    }
    
    if (!isValidImageUrl(url)) {
        showError('Please enter a valid image URL (http/https).');
        return;
    }
    
    // Show loading state
    loadUrlBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Loading...';
    loadUrlBtn.disabled = true;
    
    // Test if image loads
    const testImg = new Image();
    testImg.onload = function() {
        currentImageUrl = url;
        currentImageData = null;
        displayImagePreview(url);
        validateForm();
        
        // Reset button
        loadUrlBtn.innerHTML = '<i class="fas fa-link"></i> Load';
        loadUrlBtn.disabled = false;
    };
    testImg.onerror = function() {
        showError('Unable to load image from the provided URL. Please check the URL and try again.');
        
        // Reset button
        loadUrlBtn.innerHTML = '<i class="fas fa-link"></i> Load';
        loadUrlBtn.disabled = false;
    };
    testImg.src = url;
}

function displayImagePreview(src) {
    previewImg.src = src;
    imagePreview.style.display = 'block';
    hideError();
}

function clearImage() {
    currentImageData = null;
    currentImageUrl = null;
    imagePreview.style.display = 'none';
    imageUrl.value = '';
    imageUpload.value = '';
    validateForm();
}

function validateForm() {
    const hasImage = currentImageData || currentImageUrl;
    const hasQuestion = questionInput.value.trim().length > 0;
    
    analyzeBtn.disabled = !hasImage || !hasQuestion;
}

function isValidImageUrl(url) {
    try {
        const urlObj = new URL(url);
        return urlObj.protocol === 'http:' || urlObj.protocol === 'https:';
    } catch {
        return false;
    }
}

async function analyzeImage() {
    if (analyzeBtn.disabled) return;
    
    const question = questionInput.value.trim();
    if (!question) {
        showError('Please enter a question about the image.');
        return;
    }
    
    // Show loading state
    setLoadingState(true);
    hideError();
    hideResults();
    
    try {
        const payload = {
            question: question,
            image_url: currentImageUrl,
            image_data: currentImageData
        };
        
        const response = await fetch('/analyze', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(payload)
        });
        
        const data = await response.json();
        
        if (response.ok && data.success) {
            showResults(data);
        } else {
            throw new Error(data.error || 'An error occurred while analyzing the image.');
        }
        
    } catch (error) {
        console.error('Analysis error:', error);
        showError(error.message || 'Failed to analyze image. Please check your connection and try again.');
    } finally {
        setLoadingState(false);
    }
}

function setLoadingState(loading) {
    analyzeBtn.classList.toggle('loading', loading);
    analyzeBtn.disabled = loading;
    
    if (loading) {
        analyzeBtn.querySelector('.btn-text').style.display = 'none';
        analyzeBtn.querySelector('.btn-loading').style.display = 'inline-block';
    } else {
        analyzeBtn.querySelector('.btn-text').style.display = 'inline-block';
        analyzeBtn.querySelector('.btn-loading').style.display = 'none';
        validateForm(); // Re-validate form after loading
    }
}

function showResults(data) {
    // Update model info
    modelInfo.textContent = `Model: ${data.model_used}`;
    
    // Show/hide fallback indicator
    if (data.fallback_used) {
        fallbackIndicator.style.display = 'inline-flex';
    } else {
        fallbackIndicator.style.display = 'none';
    }
    
    // Format and display response
    const formattedResponse = formatResponse(data.response);
    responseContent.innerHTML = formattedResponse;
    
    // Show results section
    resultsSection.style.display = 'block';
    
    // Scroll to results
    resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function formatResponse(text) {
    // Convert markdown-like formatting to HTML
    return text
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>') // Bold
        .replace(/\*(.*?)\*/g, '<em>$1</em>') // Italic
        .replace(/\n\n/g, '</p><p>') // Paragraphs
        .replace(/\n/g, '<br>') // Line breaks
        .replace(/^/, '<p>') // Start paragraph
        .replace(/$/, '</p>'); // End paragraph
}

function showError(message) {
    errorMessage.textContent = message;
    errorSection.style.display = 'block';
    
    // Scroll to error
    errorSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
    
    // Auto-hide error after 10 seconds
    setTimeout(hideError, 10000);
}

function hideError() {
    errorSection.style.display = 'none';
}

function hideResults() {
    resultsSection.style.display = 'none';
}

// Utility functions
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Add some nice touch interactions for mobile
if ('ontouchstart' in window) {
    document.addEventListener('touchstart', function() {}, {passive: true});
}

// Add keyboard shortcuts
document.addEventListener('keydown', (e) => {
    // Ctrl/Cmd + Enter to analyze
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
        e.preventDefault();
        if (!analyzeBtn.disabled) {
            analyzeImage();
        }
    }
    
    // Escape to clear image
    if (e.key === 'Escape' && (currentImageData || currentImageUrl)) {
        clearImage();
    }
});

// Console welcome message
console.log(`
🤖 Multimodal QA Agent
━━━━━━━━━━━━━━━━━━━━━━
✨ Features:
• Image upload & URL input
• AI-powered visual Q&A
• Fallback text-only mode
• Beautiful responsive UI

🚀 Ready to analyze images!
`);
