# 🔬 DeepResearchAgent-AI

**Advanced AI-Powered Research Assistant v2.0**

🚀 **[Try it Live on Hugging Face Spaces](https://huggingface.co/spaces/hari7261/DeepSearch-Agent)** 🚀

![DeepResearchAgent-AI](image.png)epResearchAgent-AI

## 🚀 Features

- **🎯 Intelligent Web Search**: Uses DuckDuckGo to find the most relevant sources
- **📊 Advanced Content Analysis**: Automatically extracts and processes content from multiple websites
- **🤖 AI-Powered Synthesis**: Leverages Google's Gemini 2.0 Flash to create comprehensive reports
- **📄 Professional Reports**: Generates both Markdown and beautifully formatted PDF reports
- **🎨 Modern UI**: Sleek, responsive interface with gradient backgrounds and smooth animations
- **🔐 Secure API Handling**: Built-in validation with detailed error messages and troubleshooting
- **⚡ Fast & Reliable**: Automated research in minutes with real-time progress tracking
- **🛡️ Safe File Handling**: Automatic filename sanitization for cross-platform compatibility
- **📱 Responsive Design**: Works perfectly on desktop, tablet, and mobile devices

## 📋 Prerequisites

- Python 3.8 or higher
- Google Gemini API key (get it from [AI Studio](https://aistudio.google.com/))
- Internet connection for web research

## 🔧 Installation

1. **Clone or download this repository**
   ```bash
   git clone <your-repo-url>
   cd hell
   ```

2. **Automated Setup (Recommended)**
   ```bash
   python setup.py
   ```

3. **Manual Setup**
   ```bash
   pip install -r requirements.txt
   ```

4. **Get your Gemini API key**
   - Visit [Google AI Studio](https://aistudio.google.com/)
   - Create an account or sign in
   - Generate a new API key
   - Copy the complete API key (usually 30-50 characters)
   - Keep this key secure and don't share it publicly

## 🚀 Quick Start

1. **Automated Setup**
   ```bash
   python setup.py
   ```

2. **Manual Setup**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   python app.py
   ```

4. **Get your API key**
   - Visit [Google AI Studio](https://aistudio.google.com/)
   - Generate your Gemini API key

## 🧪 API Key Testing

Before running the main application, you can test your API key independently:

```bash
python test_api_key.py
```

Or test with your API key directly:
```bash
python test_api_key.py "your-api-key-here"
```

This will help you identify and resolve API key issues before using the main application.

1. **Run the application**
   ```bash
   python app.py
   ```

2. **Open your browser**
   - The application will automatically open in your default browser
   - Or navigate to the URL shown in the terminal (usually `http://127.0.0.1:7860`)

3. **Start researching**
   - Enter your Gemini API key in the designated field
   - Click "🔍 Validate API Key" to test your key (recommended)
   - Type your research topic (e.g., "Latest developments in AI", "Climate change solutions 2024")
   - Click "🚀 Start Deep Research"
   - Wait for the comprehensive report to be generated (1-2 minutes)
   - Download your report in either:
     - **📝 Markdown format** (.md file)
     - **📄 Professional PDF** with formatted layout, branding, and citations

## 🎨 Modern Interface Features

- **🎯 Professional Hero Section**: Eye-catching gradient header with DeepResearchAgent-AI branding
- **🔑 Smart API Setup**: Collapsible step-by-step guide for API key configuration
- **📊 Real-time Validation**: Instant feedback on API key status with detailed error messages
- **🔄 Progress Tracking**: Visual progress indicators during research process
- **📱 Fully Responsive**: Optimized for desktop, tablet, and mobile devices
- **🎨 Modern Glassmorphism**: Professional styling with gradients, shadows, and blur effects
- **🌈 High Contrast**: Dark text on light backgrounds for perfect readability
- **⚡ Fast Loading**: Optimized performance with efficient caching

## 📁 Project Structure

```
hell/
├── app.py              # Main application with modern UI and PDF generation
├── README.md           # Comprehensive documentation
├── requirements.txt    # All dependencies including PDF generation
└── setup.py           # Automated setup and testing script
```

## 🔍 How It Works

1. **🔍 Intelligent Search**: Uses DuckDuckGo to find the most relevant and recent sources
2. **📊 Content Processing**: Fetches and extracts meaningful content from multiple web pages
3. **🤖 AI Analysis**: Google's Gemini 2.0 Flash analyzes all gathered information
4. **📄 Professional Reports**: Generates comprehensive reports with:
   - **Executive Summary** with key findings
   - **Detailed Analysis** with explanations and examples
   - **Real-world Applications** and use cases
   - **Future Trends** and predictions
   - **Professional Citations** with source links
   - **Branded PDF Layout** with your platform name and styling

## ✅ **What's Fixed & Enhanced:**

### � **Fixed Issues:**
- ✅ **Filename Generation**: Now correctly uses topic name instead of report content
- ✅ **File Safety**: Proper sanitization of special characters (?, <, >, :, /, \, |, *)
- ✅ **UI Visibility**: Fixed white text issues with high-contrast dark text on light backgrounds
- ✅ **Responsive Design**: Fully responsive layout that works on all devices
- ✅ **Error Handling**: Robust error handling for PDF generation and file creation

### 🎨 **UI Enhancements:**
- ✅ **Modern Glassmorphism**: Professional glass-like effects with blur and transparency
- ✅ **Gradient Backgrounds**: Beautiful color gradients throughout the interface
- ✅ **High Contrast Text**: Dark text on light backgrounds for perfect readability
- ✅ **Responsive Layout**: Adapts seamlessly to different screen sizes
- ✅ **Professional Styling**: Enhanced buttons, inputs, and layout components
- ✅ **Status Indicators**: Clear success/error messages with color coding

### 📄 **PDF Features:**
- ✅ **Professional Layout**: Multi-page PDF with headers, footers, and branding
- ✅ **DeepResearchAgent-AI Branding**: Platform name prominently displayed
- ✅ **Organized Sections**: Table of contents with proper formatting
- ✅ **Source Citations**: Complete bibliography with links
- ✅ **Modern Typography**: Professional fonts and color scheme

## ⚙️ Configuration

### Environment Variables (Optional)
You can set your Gemini API key as an environment variable:

**Windows (PowerShell):**
```powershell
$env:GEMINI_API_KEY="your-api-key-here"
```

**Linux/Mac:**
```bash
export GEMINI_API_KEY="your-api-key-here"
```

### Customization Options

You can modify the following parameters in `app.py`:

- `max_results`: Number of search results to fetch (default: 10)
- `max_sources`: Number of sources to analyze (default: 5)
- `content_length`: Maximum content length per source (default: 5000 characters)

## 📊 Example Use Cases

- **Academic Research**: Gather information on scientific topics
- **Market Analysis**: Research industry trends and competitors
- **Technology Updates**: Stay current with latest developments
- **Investment Research**: Analyze market opportunities
- **Educational Content**: Create comprehensive study materials

## 🛠️ Dependencies

- `gradio`: Web interface framework
- `google-generativeai`: Google's Gemini AI API
- `ddgs`: Web search functionality (formerly duckduckgo-search)
- `requests`: HTTP requests for web scraping
- `beautifulsoup4`: HTML parsing and content extraction

## ⚠️ Important Notes

- **API Limits**: Be mindful of your Gemini API usage limits and costs
- **Rate Limiting**: The tool includes delays between requests to be respectful to websites
- **Content Length**: Content is automatically truncated to avoid token limits
- **Source Quality**: The tool filters out low-quality sources automatically

## 🔒 Security

- Never share your API key publicly
- The API key is handled securely and not stored permanently
- Use environment variables for production deployments

## 🐛 Troubleshooting

### Common Issues

1. **"No relevant sources found"**
   - Try different keywords or a more specific search term
   - Check your internet connection

### 2. **"Invalid API key" or "API key validation failed"**
   - ✅ **Copy the complete key** - make sure you didn't miss any characters
   - ✅ **Check for extra spaces** at the beginning or end of the key
   - ✅ **Try refreshing** the AI Studio page and copying the key again
   - ✅ **Make sure you're signed in** to the correct Google account
   - ✅ **Use the test script**: `python test_api_key.py "your-key"`
   - ✅ **Try creating a new API key** if the current one doesn't work

### 3. **"API quota exceeded"**
   - Check your usage at https://aistudio.google.com/
   - Wait for the quota to reset (usually monthly)
   - Consider upgrading your plan if needed

### 4. **"Network error" or "Connection timeout"**
   - Check your internet connection
   - Try again in a few minutes
   - Disable VPN if you're using one
   - Check if Google services are accessible in your region

### 5. **"API key doesn't have required permissions"**
   - Regenerate your API key at https://aistudio.google.com/
   - Make sure the API key is enabled for Gemini API
   - Check if your Google Cloud project has the necessary permissions

3. **"Search error: operation timed out"**
   - This is usually a temporary network issue
   - Try running the search again
   - Check your internet connection

4. **Import errors with ddgs**
   - Make sure you've uninstalled the old `duckduckgo-search` package
   - Install the new `ddgs` package: `pip install ddgs`
   - Run the setup script: `python setup.py`

5. **Installation issues**
   - Make sure you have Python 3.8+ installed
   - Try installing dependencies one by one
   - Use the provided setup script for automated installation

6. **Filename errors or download issues**
   - The app automatically sanitizes filenames to remove invalid characters
   - Special characters like `?`, `<`, `>`, `:`, `/`, `\`, `|`, `*` are replaced with underscores
   - Very long research topics are automatically truncated for safe file creation

### Getting Help

If you encounter issues:
1. Check the console output for detailed error messages
2. Verify all dependencies are installed correctly
3. Ensure your API key is valid and has sufficient quota

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues, feature requests, or pull requests.

## 📧 Contact

For questions or support, please create an issue in the repository.

---

**Happy Researching! 🔍✨**
