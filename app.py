import gradio as gr
import google.generativeai as genai
from ddgs import DDGS
import requests
from bs4 import BeautifulSoup
import time
from urllib.parse import urlparse
import re
import json
from typing import List, Dict, Any
from datetime import datetime
import os
import tempfile
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
import markdown

# Application Constants
APP_NAME = "DeepResearchAgent-AI"
APP_VERSION = "v2.0"
APP_DESCRIPTION = "Advanced AI-Powered Research Assistant"

# Enhanced topic detection and search helper functions
def detect_topic_category(query: str) -> str:
    """Detect the category of research topic for specialized search strategies"""
    politics_keywords = ['politics', 'political', 'government', 'policy', 'election', 'democracy', 'parliament', 'congress', 'senate', 'president', 'minister', 'geopolitics', 'diplomacy', 'foreign policy', 'international relations']
    history_keywords = ['history', 'historical', 'ancient', 'medieval', 'world war', 'civilization', 'empire', 'dynasty', 'revolution', 'century', 'era', 'timeline', 'past', 'heritage']
    geography_keywords = ['geography', 'geographical', 'country', 'continent', 'ocean', 'mountain', 'river', 'climate', 'population', 'capital', 'border', 'region', 'territory', 'map']
    current_affairs_keywords = ['current', 'news', 'today', 'recent', 'latest', 'breaking', 'update', 'happening', '2024', '2025', 'this year', 'now']
    technology_keywords = ['technology', 'tech', 'ai', 'artificial intelligence', 'machine learning', 'software', 'hardware', 'computer', 'digital', 'programming', 'coding', 'algorithm', 'data science', 'cybersecurity']
    war_keywords = ['war', 'warfare', 'conflict', 'battle', 'military', 'army', 'defense', 'weapon', 'strategy', 'combat', 'invasion', 'occupation', 'siege']
    economics_keywords = ['economy', 'economic', 'finance', 'financial', 'market', 'trade', 'business', 'industry', 'company', 'corporation', 'gdp', 'inflation', 'recession']
    science_keywords = ['science', 'scientific', 'research', 'study', 'experiment', 'discovery', 'innovation', 'physics', 'chemistry', 'biology', 'medicine', 'health']
    
    query_lower = query.lower()
    
    if any(keyword in query_lower for keyword in politics_keywords):
        return 'politics'
    elif any(keyword in query_lower for keyword in history_keywords):
        return 'history'
    elif any(keyword in query_lower for keyword in geography_keywords):
        return 'geography'
    elif any(keyword in query_lower for keyword in current_affairs_keywords):
        return 'current_affairs'
    elif any(keyword in query_lower for keyword in technology_keywords):
        return 'technology'
    elif any(keyword in query_lower for keyword in war_keywords):
        return 'war'
    elif any(keyword in query_lower for keyword in economics_keywords):
        return 'economics'
    elif any(keyword in query_lower for keyword in science_keywords):
        return 'science'
    else:
        return 'general'

def get_specialized_domains(topic_type: str) -> List[str]:
    """Get specialized domains based on topic category"""
    domain_mapping = {
        'politics': ['reuters.com', 'bbc.com', 'cnn.com', 'politico.com', 'foreignaffairs.com', 'cfr.org', 'brookings.edu', 'csis.org'],
        'history': ['britannica.com', 'history.com', 'nationalgeographic.com', 'smithsonianmag.com', 'historynet.com', 'worldhistory.org'],
        'geography': ['nationalgeographic.com', 'worldatlas.com', 'britannica.com', 'cia.gov', 'worldbank.org', 'un.org'],
        'current_affairs': ['reuters.com', 'bbc.com', 'cnn.com', 'ap.org', 'npr.org', 'aljazeera.com', 'theguardian.com', 'nytimes.com'],
        'technology': ['techcrunch.com', 'wired.com', 'ars-technica.com', 'ieee.org', 'nature.com', 'sciencemag.org', 'mit.edu', 'stanford.edu'],
        'war': ['janes.com', 'defensenews.com', 'militarytimes.com', 'csis.org', 'rand.org', 'stratfor.com'],
        'economics': ['reuters.com', 'bloomberg.com', 'economist.com', 'ft.com', 'worldbank.org', 'imf.org', 'federalreserve.gov'],
        'science': ['nature.com', 'sciencemag.org', 'scientificamerican.com', 'newscientist.com', 'pnas.org', 'cell.com'],
        'general': ['wikipedia.org', 'britannica.com', 'reuters.com', 'bbc.com', 'cnn.com']
    }
    return domain_mapping.get(topic_type, domain_mapping['general'])

def get_topic_keywords(query: str, topic_type: str) -> List[str]:
    """Get enhanced keywords based on topic category"""
    keyword_mapping = {
        'politics': ['analysis', 'policy', 'government', 'official', 'statement', 'report', 'briefing', 'summit', 'debate', 'legislation'],
        'history': ['timeline', 'chronology', 'facts', 'documented', 'archive', 'primary source', 'historian', 'evidence', 'analysis', 'context'],
        'geography': ['facts', 'statistics', 'data', 'demographic', 'topography', 'atlas', 'survey', 'official', 'census', 'coordinates'],
        'current_affairs': ['breaking', 'latest', 'update', 'developing', 'live', 'recent', 'today', 'headlines', 'news', 'report'],
        'technology': ['innovation', 'breakthrough', 'development', 'advancement', 'research', 'cutting-edge', 'emerging', 'trend', 'future', 'application'],
        'war': ['analysis', 'strategy', 'tactics', 'intelligence', 'assessment', 'report', 'conflict', 'situation', 'update', 'briefing'],
        'economics': ['analysis', 'forecast', 'data', 'statistics', 'trend', 'market', 'report', 'outlook', 'indicator', 'growth'],
        'science': ['research', 'study', 'discovery', 'breakthrough', 'publication', 'peer-reviewed', 'journal', 'findings', 'methodology', 'evidence'],
        'general': ['information', 'facts', 'comprehensive', 'detailed', 'overview', 'guide', 'explanation', 'analysis', 'summary', 'background']
    }
    return keyword_mapping.get(topic_type, keyword_mapping['general'])

def get_priority_domains_for_topic(topic_type: str) -> List[str]:
    """Get priority domains for result ranking based on topic"""
    priority_mapping = {
        'politics': ['reuters.com', 'bbc.com', 'cnn.com', 'politico.com', 'foreignaffairs.com', 'cfr.org', 'brookings.edu', 'apnews.com'],
        'history': ['britannica.com', 'history.com', 'nationalgeographic.com', 'smithsonianmag.com', 'worldhistory.org', 'historynet.com'],
        'geography': ['nationalgeographic.com', 'worldatlas.com', 'britannica.com', 'cia.gov', 'worldbank.org', 'un.org'],
        'current_affairs': ['reuters.com', 'bbc.com', 'cnn.com', 'ap.org', 'npr.org', 'aljazeera.com', 'theguardian.com', 'nytimes.com'],
        'technology': ['techcrunch.com', 'wired.com', 'ars-technica.com', 'ieee.org', 'nature.com', 'mit.edu', 'stanford.edu', 'acm.org'],
        'war': ['janes.com', 'defensenews.com', 'csis.org', 'rand.org', 'stratfor.com', 'cfr.org'],
        'economics': ['reuters.com', 'bloomberg.com', 'economist.com', 'ft.com', 'worldbank.org', 'imf.org', 'federalreserve.gov'],
        'science': ['nature.com', 'sciencemag.org', 'scientificamerican.com', 'newscientist.com', 'pnas.org', 'cell.com'],
        'general': ['wikipedia.org', 'britannica.com', 'reuters.com', 'bbc.com', 'cnn.com', 'nationalgeographic.com']
    }
    return priority_mapping.get(topic_type, priority_mapping['general'])

# Sanitize filename for safe file creation
def sanitize_filename(filename: str) -> str:
    """Sanitize filename to remove invalid characters for Windows/Unix systems"""
    # Remove or replace invalid characters
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    
    # Remove multiple consecutive underscores and trim
    filename = re.sub(r'_+', '_', filename)
    filename = filename.strip('_')
    
    # Limit length to prevent issues
    if len(filename) > 200:
        filename = filename[:200]
    
    # Ensure it's not empty and add extension if missing
    if not filename:
        filename = "research_report"
    
    if not filename.endswith('.md'):
        filename += '.md'
    
    return filename

# PDF Generation Function
def create_pdf_report(content: str, topic: str, sources: List[Dict], filename: str) -> str:
    """Create a professional PDF report from markdown content"""
    try:
        # Create temporary PDF file
        temp_dir = tempfile.gettempdir()
        pdf_path = os.path.join(temp_dir, filename.replace('.md', '.pdf'))
        
        # Create PDF document
        doc = SimpleDocTemplate(pdf_path, pagesize=A4, topMargin=1*inch, bottomMargin=1*inch)
        styles = getSampleStyleSheet()
        story = []
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#2C3E50'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        
        subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#34495E'),
            spaceAfter=20,
            alignment=TA_CENTER
        )
        
        header_style = ParagraphStyle(
            'CustomHeader',
            parent=styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#2980B9'),
            spaceAfter=12,
            spaceBefore=20,
            fontName='Helvetica-Bold'
        )
        
        body_style = ParagraphStyle(
            'CustomBody',
            parent=styles['Normal'],
            fontSize=11,
            textColor=colors.HexColor('#2C3E50'),
            spaceAfter=6,
            alignment=TA_LEFT,
            leading=14
        )
        
        # Header Section
        story.append(Paragraph(APP_NAME, title_style))
        story.append(Paragraph(APP_DESCRIPTION, subtitle_style))
        story.append(Spacer(1, 0.2*inch))
        
        # Add decorative line
        line_data = [['', '']]
        line_table = Table(line_data, colWidths=[5*inch])
        line_table.setStyle(TableStyle([
            ('LINEBELOW', (0,0), (-1,-1), 2, colors.HexColor('#3498DB')),
        ]))
        story.append(line_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Research Topic
        story.append(Paragraph("Research Topic", header_style))
        story.append(Paragraph(topic, body_style))
        story.append(Spacer(1, 0.2*inch))
        
        # Generation Info
        current_time = datetime.now().strftime("%B %d, %Y at %I:%M %p")
        story.append(Paragraph("Generated", header_style))
        story.append(Paragraph(f"{current_time}", body_style))
        story.append(Spacer(1, 0.2*inch))
        
        # Sources Summary
        if sources:
            story.append(Paragraph("Sources Analyzed", header_style))
            story.append(Paragraph(f"{len(sources)} reliable sources processed", body_style))
            story.append(Spacer(1, 0.3*inch))
        
        story.append(PageBreak())
        
        # Main Content
        story.append(Paragraph("Research Report", header_style))
        story.append(Spacer(1, 0.1*inch))
        
        # Process markdown content
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                story.append(Spacer(1, 6))
                continue
                
            if line.startswith('# '):
                story.append(Paragraph(line[2:], header_style))
            elif line.startswith('## '):
                story.append(Paragraph(line[3:], header_style))
            elif line.startswith('### '):
                header_3_style = ParagraphStyle(
                    'Header3',
                    parent=header_style,
                    fontSize=14,
                    textColor=colors.HexColor('#7F8C8D')
                )
                story.append(Paragraph(line[4:], header_3_style))
            elif line.startswith('**') and line.endswith('**'):
                bold_style = ParagraphStyle(
                    'Bold',
                    parent=body_style,
                    fontName='Helvetica-Bold'
                )
                story.append(Paragraph(line[2:-2], bold_style))
            elif line.startswith('- ') or line.startswith('* '):
                bullet_style = ParagraphStyle(
                    'Bullet',
                    parent=body_style,
                    leftIndent=20,
                    bulletIndent=10,
                    bulletText='•',
                    bulletColor=colors.HexColor('#3498DB')
                )
                story.append(Paragraph(line[2:], bullet_style))
            elif line.startswith(('1. ', '2. ', '3. ', '4. ', '5. ')):
                story.append(Paragraph(line, body_style))
            else:
                # Clean basic markdown formatting
                line = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', line)
                line = re.sub(r'\*(.*?)\*', r'<i>\1</i>', line)
                story.append(Paragraph(line, body_style))
        
        # Footer section
        story.append(PageBreak())
        story.append(Paragraph("Sources", header_style))
        
        if sources:
            for i, source in enumerate(sources[:10], 1):  # Limit to 10 sources
                source_style = ParagraphStyle(
                    'Source',
                    parent=body_style,
                    fontSize=10,
                    leftIndent=10,
                    spaceAfter=8
                )
                title = source.get('title', 'No Title')[:100]
                url = source.get('url', '')
                story.append(Paragraph(f"{i}. {title}", source_style))
                if url:
                    url_style = ParagraphStyle(
                        'URL',
                        parent=source_style,
                        fontSize=9,
                        textColor=colors.HexColor('#3498DB'),
                        leftIndent=20
                    )
                    story.append(Paragraph(url, url_style))
        
        # Footer
        story.append(Spacer(1, 0.5*inch))
        footer_style = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#7F8C8D'),
            alignment=TA_CENTER
        )
        story.append(Paragraph(f"Generated by {APP_NAME} {APP_VERSION} | Advanced AI Research Assistant", footer_style))
        
        # Build PDF
        doc.build(story)
        return pdf_path
        
    except Exception as e:
        print(f"PDF generation error: {e}")
        return None

# Validate Gemini API key
def validate_api_key(api_key: str) -> tuple[bool, str]:
    """Validate if the Gemini API key is working"""
    if not api_key or not api_key.strip():
        return False, "❌ API key is empty. Please enter a valid Gemini API key."

    api_key = api_key.strip()

    # Basic format checks
    if len(api_key) < 20:
        return False, "❌ API key seems too short. Please check that you copied the complete key."

    if not api_key.replace('-', '').replace('_', '').isalnum():
        return False, "❌ API key contains invalid characters. Please check your key format."

    try:
        # Test the API key with a simple request
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.0-flash')

        # Try a minimal test generation with timeout
        response = model.generate_content("Test", generation_config={"max_output_tokens": 10})
        return True, "✅ API key is valid and working!"

    except Exception as e:
        error_msg = str(e).lower()
        print(f"API Key validation error: {e}")  # Debug info

        if "api key not valid" in error_msg or "api_key_invalid" in error_msg:
            return False, """❌ Invalid API key. Please check your Gemini API key and try again.

**Common issues:**
• Make sure you copied the ENTIRE key from https://aistudio.google.com/
• Check for extra spaces at the beginning or end
• Try refreshing the page and copying the key again
• Make sure you're using the correct API key (not mixing up with other services)"""

        elif "quota" in error_msg or "limit" in error_msg:
            return False, """❌ API quota exceeded. Your Gemini API usage limit has been reached.

**Solutions:**
• Check your usage at https://aistudio.google.com/
• Wait for the quota to reset (usually monthly)
• Consider upgrading your plan if needed"""

        elif "permission" in error_msg or "forbidden" in error_msg:
            return False, """❌ API key doesn't have required permissions.

**Solutions:**
• Regenerate your API key at https://aistudio.google.com/
• Make sure the API key is enabled for Gemini API
• Check if your Google Cloud project has the necessary permissions"""

        elif "network" in error_msg or "connection" in error_msg or "timeout" in error_msg:
            return False, """❌ Network error. Please check your internet connection and try again.

**Troubleshooting:**
• Check your internet connection
• Try again in a few minutes
• Disable VPN if you're using one
• Check if Google services are accessible in your region"""

        elif "model" in error_msg:
            return False, """❌ Model not available. The specified Gemini model might not be available.

**Solutions:**
• Try using a different model (like 'gemini-pro')
• Check Gemini API availability at https://status.cloud.google.com/"""

        else:
            return False, f"""❌ API key validation failed: {str(e)}

**Debugging tips:**
• Make sure you're using a valid Gemini API key from https://aistudio.google.com/
• Try creating a new API key if the current one doesn't work
• Check the Google Cloud Console for any billing or permission issues"""

# Search the web for relevant information using DuckDuckGo with enhanced targeting for diverse topics
def web_search(query: str, max_results: int = 15) -> List[Dict[str, str]]:
    """Enhanced search for diverse topics: Politics, History, Technology, Current Affairs, etc."""
    try:
        with DDGS() as ddgs:
            all_results = []
            
            # Detect topic category for specialized search
            topic_type = detect_topic_category(query.lower())
            print(f"Detected topic category: {topic_type}")
            
            # Strategy 1: Exact phrase search
            try:
                exact_results = list(ddgs.text(f'"{query}"', max_results=max_results//3))
                all_results.extend(exact_results)
                print(f"Found {len(exact_results)} results from exact search")
            except Exception as e:
                print(f"Exact search error: {e}")
            
            # Strategy 2: Topic-specific domain searches
            specialized_domains = get_specialized_domains(topic_type)
            for domain in specialized_domains:
                try:
                    domain_results = list(ddgs.text(f'{query} site:{domain}', max_results=2))
                    all_results.extend(domain_results)
                    if len(all_results) >= max_results:
                        break
                except Exception as e:
                    print(f"Domain search error for {domain}: {e}")
                    continue
            
            # Strategy 3: Enhanced keyword searches based on topic
            enhanced_keywords = get_topic_keywords(query, topic_type)
            for keyword in enhanced_keywords[:5]:
                try:
                    keyword_results = list(ddgs.text(f'{query} {keyword}', max_results=2))
                    all_results.extend(keyword_results)
                    if len(all_results) >= max_results:
                        break
                except Exception as e:
                    print(f"Keyword search error for {keyword}: {e}")
                    continue
            
            # Strategy 4: Time-based searches for current affairs
            if topic_type in ['current_affairs', 'politics', 'technology', 'news']:
                time_modifiers = ['2024', '2025', 'latest', 'recent', 'current', 'today', 'this year']
                for modifier in time_modifiers[:3]:
                    try:
                        time_results = list(ddgs.text(f'{query} {modifier}', max_results=2))
                        all_results.extend(time_results)
                        if len(all_results) >= max_results:
                            break
                    except Exception as e:
                        print(f"Time-based search error for {modifier}: {e}")
                        continue
            
            # Strategy 5: Academic and authoritative sources
            academic_modifiers = ['analysis', 'research', 'study', 'report', 'comprehensive', 'detailed']
            for modifier in academic_modifiers[:3]:
                try:
                    academic_results = list(ddgs.text(f'{query} {modifier}', max_results=2))
                    all_results.extend(academic_results)
                    if len(all_results) >= max_results:
                        break
                except Exception as e:
                    print(f"Academic search error for {modifier}: {e}")
                    continue
            
            # Strategy 6: Fallback comprehensive search
            if len(all_results) < 8:
                try:
                    general_results = list(ddgs.text(query, max_results=max_results//2))
                    all_results.extend(general_results)
                except Exception as e:
                    print(f"General search error: {e}")
            
            # Remove duplicates and prioritize authoritative domains
            seen_urls = set()
            unique_results = []
            priority_domains = get_priority_domains_for_topic(topic_type)
            
            # First, add results from priority domains
            for result in all_results:
                url = result.get('href', '')
                if url not in seen_urls and any(domain in url for domain in priority_domains):
                    seen_urls.add(url)
                    unique_results.append(result)
                    if len(unique_results) >= max_results:
                        break
            
            # Then add other unique results
            for result in all_results:
                url = result.get('href', '')
                if url not in seen_urls:
                    seen_urls.add(url)
                    unique_results.append(result)
                    if len(unique_results) >= max_results:
                        break
            
            print(f"Total unique results found: {len(unique_results)}")
            return unique_results[:max_results]
            
    except Exception as e:
        print(f"Search error: {e}")
        # Final fallback - simple search
        try:
            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=min(max_results, 5)))
                print(f"Fallback search found: {len(results)} results")
                return results
        except Exception as e2:
            print(f"Fallback search error: {e2}")
            return []

# Fetch and extract content from a URL with better error handling
def fetch_url_content(url: str) -> str:
    """Fetch content from a URL and extract meaningful text with enhanced error handling"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
        # Increase timeout and add retries
        response = requests.get(url, headers=headers, timeout=15, allow_redirects=True)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remove unwanted elements
        for element in soup(['script', 'style', 'nav', 'footer', 'header', 'aside', 'iframe', 'noscript']):
            element.decompose()
        
        # Try to get the main content area first
        main_content = soup.find('main') or soup.find('article') or soup.find('div', class_=['content', 'main', 'body'])
        if main_content:
            text = main_content.get_text()
        else:
            text = soup.get_text()
        
        # Clean up text more thoroughly
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk and len(chunk) > 2)
        
        # Remove excessive whitespace and clean up
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        
        # Return more content for better analysis - increased from 5000 to 8000
        return text[:8000] if text else ""
        
    except requests.exceptions.Timeout:
        print(f"Timeout error for {url} - trying with shorter timeout")
        try:
            # Retry with shorter timeout
            response = requests.get(url, headers=headers, timeout=8, allow_redirects=True)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            text = soup.get_text()
            text = re.sub(r'\s+', ' ', text.strip())
            return text[:5000] if text else ""
        except Exception as retry_error:
            print(f"Retry failed for {url}: {retry_error}")
            return ""
            
    except requests.exceptions.RequestException as e:
        print(f"Request error fetching {url}: {e}")
        return ""
    except Exception as e:
        print(f"Unexpected error fetching {url}: {e}")
        return ""

# Research function using web search and content extraction with enhanced analysis for diverse topics
def perform_research(query: str, max_sources: int = 12) -> Dict[str, Any]:
    """Perform comprehensive research by searching and extracting content from multiple sources"""
    print(f"🔍 Starting comprehensive research for: {query}")
    
    # Detect topic category for better research strategy
    topic_type = detect_topic_category(query.lower())
    print(f"📊 Detected topic category: {topic_type}")
    
    # Search for relevant sources with more results to ensure we get at least 10 quality sources
    search_results = web_search(query, max_results=max_sources*4)  # Get more results initially
    print(f"📊 Found {len(search_results)} potential sources")
    
    sources = []
    content_chunks = []
    successful_fetches = 0
    failed_fetches = 0
    
    for i, result in enumerate(search_results):
        if successful_fetches >= max_sources:
            break
            
        url = result.get('href', '')
        title = result.get('title', 'No title')
        
        # Skip low-quality or duplicate sources
        if should_skip_source(url, title, sources):
            print(f"⏭️ Skipping {url} - low quality or duplicate")
            continue
        
        print(f"🌐 Fetching content from {url}")
        content = fetch_url_content(url)
        
        if content and len(content) > 150:  # Minimum content threshold
            # Validate content quality for the specific topic
            if is_relevant_content(content, query, topic_type):
                sources.append({
                    'title': title,
                    'url': url,
                    'content': content,
                    'topic_type': topic_type
                })
                content_chunks.append(f"SOURCE {successful_fetches + 1} [{topic_type.upper()}]:\nTITLE: {title}\nURL: {url}\nCONTENT:\n{content}\n{'='*100}\n")
                successful_fetches += 1
                print(f"✅ Successfully extracted {len(content)} characters from source {successful_fetches}")
            else:
                print(f"⚠️ Content not relevant for {query}")
                failed_fetches += 1
        else:
            print(f"⚠️ Skipped {url} - insufficient content ({len(content) if content else 0} chars)")
            failed_fetches += 1
        
        # Add small delay to be respectful
        time.sleep(0.3)
    
    # If we don't have enough sources, try a broader search
    if successful_fetches < 8:
        print(f"🔄 Only found {successful_fetches} quality sources, trying broader search...")
        broader_results = web_search(f"{query} comprehensive analysis", max_results=15)
        
        for result in broader_results:
            if successful_fetches >= max_sources:
                break
                
            url = result.get('href', '')
            title = result.get('title', 'No title')
            
            if should_skip_source(url, title, sources):
                continue
                
            content = fetch_url_content(url)
            if content and len(content) > 100:
                sources.append({
                    'title': title,
                    'url': url,
                    'content': content,
                    'topic_type': 'additional'
                })
                content_chunks.append(f"ADDITIONAL SOURCE {successful_fetches + 1}:\nTITLE: {title}\nURL: {url}\nCONTENT:\n{content}\n{'='*100}\n")
                successful_fetches += 1
                print(f"✅ Additional source {successful_fetches} added")
            
            time.sleep(0.3)
    
    research_context = "\n".join(content_chunks)
    
    print(f"📝 Research completed: {successful_fetches} sources processed, {failed_fetches} failed")
    print(f"📊 Total content length: {len(research_context)} characters")
    
    return {
        'sources': sources,
        'research_context': research_context,
        'query': query,
        'total_sources': successful_fetches,
        'topic_type': topic_type,
        'failed_sources': failed_fetches
    }

def should_skip_source(url: str, title: str, existing_sources: List[Dict]) -> bool:
    """Check if a source should be skipped based on quality and duplication"""
    # Skip if URL already exists
    existing_urls = [source['url'] for source in existing_sources]
    if url in existing_urls:
        return True
    
    # Skip low-quality domains
    low_quality_domains = ['pinterest.com', 'instagram.com', 'facebook.com', 'twitter.com', 'tiktok.com', 'reddit.com']
    if any(domain in url for domain in low_quality_domains):
        return True
    
    # Skip if title is too short or generic
    if len(title) < 10 or title.lower() in ['no title', 'untitled', 'page not found']:
        return True
    
    return False

def is_relevant_content(content: str, query: str, topic_type: str) -> bool:
    """Check if content is relevant to the query and topic type"""
    content_lower = content.lower()
    query_words = query.lower().split()
    
    # Check if at least 30% of query words appear in content
    matching_words = sum(1 for word in query_words if word in content_lower)
    word_relevance = matching_words / len(query_words) if query_words else 0
    
    # Topic-specific relevance keywords
    topic_relevance_keywords = get_topic_keywords(query, topic_type)
    topic_matches = sum(1 for keyword in topic_relevance_keywords if keyword.lower() in content_lower)
    
    # Content should have reasonable length and relevance
    return len(content) > 200 and (word_relevance >= 0.3 or topic_matches >= 2)

# Generate a research report using Gemini with enhanced topic handling
def generate_research_report(research_data: Dict[str, Any], gemini_api_key: str) -> str:
    """Generate a comprehensive research report using Gemini for diverse topics"""
    if not gemini_api_key:
        return "❌ Gemini API key is required to generate the report."
    
    # Validate API key first
    is_valid, validation_message = validate_api_key(gemini_api_key)
    if not is_valid:
        return f"❌ {validation_message}"
    
    try:
        # Initialize Gemini (already configured in validation)
        model = genai.GenerativeModel('gemini-2.0-flash')
        
        topic_type = research_data.get('topic_type', 'general')
        failed_sources = research_data.get('failed_sources', 0)
        
        # Create topic-specific prompt
        prompt = f"""
        RESEARCH QUERY: {research_data['query']}
        TOPIC CATEGORY: {topic_type.upper()}
        TOTAL SOURCES ANALYZED: {research_data.get('total_sources', len(research_data['sources']))}
        FAILED SOURCES: {failed_sources}
        
        COMPREHENSIVE RESEARCH DATA FROM MULTIPLE AUTHORITATIVE SOURCES:
        {research_data['research_context']}
        
        INSTRUCTIONS FOR {topic_type.upper()} RESEARCH REPORT:
        Based on the above research data, create a comprehensive, well-structured report analyzing ALL the information provided. This is a {topic_type} research topic, so focus on relevant aspects for this domain.
        
        Your report structure should include:
        
        1. **EXECUTIVE SUMMARY** 
           - Key findings and main points about {research_data['query']}
           - Critical insights and takeaways
           - Brief overview of what the research reveals
        
        2. **DETAILED ANALYSIS** 
           - In-depth examination of all collected information
           - Multiple perspectives and viewpoints found in sources
           - Connections between different pieces of information
           - Contradictions or debates if any exist
        
        3. **BACKGROUND & CONTEXT**
           - Historical background (if relevant)
           - Current situation and status
           - Relevant context that helps understand the topic
        
        4. **KEY FINDINGS & INSIGHTS**
           - Most important discoveries from the research
           - Patterns and trends identified
           - Significant facts and statistics
           - Expert opinions and analysis
        
        5. **CURRENT STATUS & DEVELOPMENTS** 
           - Latest information and recent developments
           - Current state of affairs
           - Recent changes or updates
        
        6. **DIFFERENT PERSPECTIVES**
           - Various viewpoints found in sources
           - Debates and discussions around the topic
           - Conflicting information (if any)
        
        7. **IMPLICATIONS & SIGNIFICANCE**
           - Why this topic matters
           - Impact and consequences
           - Future implications
        
        8. **DETAILED BREAKDOWN**
           - Specific details from each major source
           - Technical information (if applicable)
           - Statistics and data points
           - Quotes and specific information
        
        9. **CONCLUSIONS**
           - Summary of what was discovered
           - Final thoughts and analysis
           - Gaps in information (if any)
        
        10. **SOURCES & REFERENCES**
            - List all sources with proper attribution
            - Include URLs for verification
            - Note the reliability and type of each source
        
        FORMATTING REQUIREMENTS:
        - Use clear Markdown formatting with headers (##), subheaders (###), and bullet points
        - Make the content engaging, informative, and well-organized
        - Include specific details, examples, and quotes from the sources
        - Highlight important information with **bold text**
        - Use bullet points for lists and key points
        - Organize information logically and coherently
        - If information is conflicting, present both sides
        - If insufficient information is available for any section, clearly state what could not be determined
        
        CONTENT REQUIREMENTS:
        - Base your analysis ONLY on the provided source content
        - Do not make assumptions or add information not present in the sources
        - Include specific details and examples from multiple sources
        - Synthesize information from all sources, don't just summarize each one separately
        - Maintain objectivity and present facts as found in sources
        - If sources contradict each other, present both perspectives
        - Focus on creating a comprehensive understanding of {research_data['query']}
        
        TOPIC-SPECIFIC FOCUS FOR {topic_type.upper()}:
        {get_topic_specific_instructions(topic_type)}
        
        Remember: This report should be thorough, well-researched, and provide real value to someone wanting to understand {research_data['query']} comprehensively.
        """
        
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        error_msg = str(e).lower()
        print(f"Report generation error: {e}")  # Debug info

        if "api key not valid" in error_msg or "api_key_invalid" in error_msg:
            return """❌ Invalid API key during report generation.

**Common issues:**
• Your API key may have expired or been revoked
• Check if you copied the complete key
• Try regenerating your API key at https://aistudio.google.com/"""

        elif "quota" in error_msg or "limit" in error_msg:
            return """❌ API quota exceeded during report generation.

**Solutions:**
• Check your usage at https://aistudio.google.com/
• Wait for the quota to reset (usually monthly)
• Consider upgrading your plan if needed"""

        elif "permission" in error_msg or "forbidden" in error_msg:
            return """❌ API key doesn't have required permissions for report generation.

**Solutions:**
• Regenerate your API key at https://aistudio.google.com/
• Make sure the API key is enabled for Gemini API"""

        elif "network" in error_msg or "connection" in error_msg or "timeout" in error_msg:
            return """❌ Network error during report generation.

**Troubleshooting:**
• Check your internet connection
• Try again in a few minutes
• The report generation process may take some time"""

        elif "model" in error_msg:
            return """❌ Model not available for report generation.

**Solutions:**
• Try using a different model
• Check Gemini API availability at https://status.cloud.google.com/"""

        else:
            return f"""❌ Error generating report: {str(e)}

**Debugging tips:**
• Try with a shorter research topic
• Check your internet connection
• Make sure your API key has sufficient quota"""

def get_topic_specific_instructions(topic_type: str) -> str:
    """Get specific instructions based on topic category"""
    instructions = {
        'politics': """
        - Focus on political implications, policy details, and governmental aspects
        - Include information about key political figures, parties, and institutions
        - Analyze policy impacts and political consequences
        - Present multiple political perspectives objectively
        - Include information about voting patterns, polls, or public opinion if available
        """,
        'history': """
        - Provide chronological context and timeline of events
        - Include historical significance and long-term impacts
        - Mention key historical figures, dates, and places
        - Analyze causes and effects of historical events
        - Connect historical events to modern implications
        """,
        'geography': """
        - Include specific geographical data, coordinates, and locations
        - Provide demographic, climate, and physical geography information
        - Discuss economic geography and natural resources
        - Include maps, borders, and territorial information
        - Analyze geographical impacts on society and economy
        """,
        'current_affairs': """
        - Focus on the most recent developments and breaking news
        - Include timeline of recent events
        - Analyze immediate impacts and short-term consequences
        - Provide context for why this is currently significant
        - Include quotes from recent statements or press releases
        """,
        'technology': """
        - Focus on technical specifications, capabilities, and limitations
        - Include information about development timeline and key innovators
        - Analyze technological implications and future potential
        - Discuss adoption rates, market impact, and competitive landscape
        - Include technical details and how the technology works
        """,
        'war': """
        - Provide strategic analysis and military context
        - Include information about forces, tactics, and equipment involved
        - Analyze geopolitical implications and international responses
        - Discuss humanitarian impacts and civilian consequences
        - Present timeline of conflict development
        """,
        'economics': """
        - Include specific economic data, statistics, and indicators
        - Analyze market trends, financial impacts, and economic consequences
        - Discuss effects on different sectors and stakeholders
        - Include information about economic policies and their outcomes
        - Provide context about economic significance and implications
        """,
        'science': """
        - Focus on scientific methodology, research findings, and evidence
        - Include information about research institutions and scientists involved
        - Explain scientific concepts and their implications
        - Discuss peer review status and scientific consensus
        - Analyze potential applications and future research directions
        """
    }
    return instructions.get(topic_type, "Focus on providing comprehensive, factual information with proper context and analysis.")

# Main research function
def run_research(topic: str, gemini_api_key: str, download_format: str = "markdown"):
    """Run the complete research process"""
    if not gemini_api_key.strip():
        return "❌ Please enter your Gemini API key.", None, None, gr.update(visible=False), gr.update(visible=False)
    
    if not topic.strip():
        return "❌ Please enter a research topic.", None, None, gr.update(visible=False), gr.update(visible=False)
    
    # First validate the API key
    is_valid, validation_message = validate_api_key(gemini_api_key)
    if not is_valid:
        return f"❌ {validation_message}", None, None, gr.update(visible=False), gr.update(visible=False)
    
    try:
        # Perform research
        print(f"Starting research for: {topic}")
        research_data = perform_research(topic)
        
        if not research_data['sources']:
            return "❌ No relevant sources found. Please try a different search term.", None, None, gr.update(visible=False), gr.update(visible=False)
        
        print(f"Found {len(research_data['sources'])} sources, generating report...")
        
        # Generate report
        report = generate_research_report(research_data, gemini_api_key)
        
        # Check if report generation was successful
        if report.startswith("❌"):
            return report, None, None, gr.update(visible=False), gr.update(visible=False)
        
        # Create safe downloadable filenames from the TOPIC, not the report content
        base_filename = sanitize_filename(topic)
        if not base_filename.endswith('.md'):
            base_filename = base_filename.replace('.md', '') + '_report.md'
        
        pdf_path = None
        try:
            # Generate PDF using the original topic for filename
            pdf_path = create_pdf_report(report, topic, research_data['sources'], base_filename)
            print(f"PDF generated successfully: {pdf_path}")
        except Exception as pdf_error:
            print(f"PDF generation failed: {pdf_error}")
            # Continue without PDF if it fails
        
        print(f"Research completed successfully. MD: {base_filename}")
        
        return report, base_filename, pdf_path, gr.update(visible=True), gr.update(visible=True)
        
    except Exception as e:
        print(f"Research error: {e}")  # Debug info
        error_msg = f"❌ An error occurred during research: {str(e)}"
        return error_msg, None, None, gr.update(visible=False), gr.update(visible=False)

# Gradio interface with dark theme
def create_interface():
    # Dark theme CSS
    dark_css = """
    /* Dark theme base */
    .gradio-container {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%) !important;
        min-height: 100vh;
        color: white !important;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    /* All blocks and containers */
    .block, .gr-box, .gr-form, .gr-panel {
        background: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 15px !important;
        backdrop-filter: blur(10px) !important;
        padding: 1.5rem !important;
        margin: 0.5rem !important;
    }
    
    /* Text colors - ALL WHITE */
    body, p, span, div, label, h1, h2, h3, h4, h5, h6 {
        color: white !important;
    }
    
    .gr-markdown, .gr-markdown * {
        color: white !important;
        background: transparent !important;
    }
    
    .gr-markdown h1, .gr-markdown h2, .gr-markdown h3 {
        color: #64b5f6 !important;
        border-bottom: 1px solid rgba(255, 255, 255, 0.2) !important;
    }
    
    /* Input fields */
    .gr-textbox, .gr-textbox input, .gr-textbox textarea {
        background: rgba(255, 255, 255, 0.1) !important;
        border: 1px solid rgba(255, 255, 255, 0.3) !important;
        border-radius: 10px !important;
        color: white !important;
        padding: 12px !important;
    }
    
    .gr-textbox input::placeholder, .gr-textbox textarea::placeholder {
        color: rgba(255, 255, 255, 0.6) !important;
    }
    
    .gr-textbox input:focus, .gr-textbox textarea:focus {
        border-color: #64b5f6 !important;
        box-shadow: 0 0 10px rgba(100, 181, 246, 0.3) !important;
        background: rgba(255, 255, 255, 0.15) !important;
    }
    
    /* Buttons */
    .gr-button {
        border-radius: 25px !important;
        padding: 12px 24px !important;
        font-weight: 600 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.5px !important;
        transition: all 0.3s ease !important;
        border: none !important;
        color: white !important;
    }
    
    .gr-button-primary {
        background: linear-gradient(135deg, #64b5f6, #42a5f5) !important;
        box-shadow: 0 4px 15px rgba(100, 181, 246, 0.4) !important;
    }
    
    .gr-button-primary:hover {
        background: linear-gradient(135deg, #42a5f5, #2196f3) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(100, 181, 246, 0.6) !important;
    }
    
    .gr-button-secondary {
        background: linear-gradient(135deg, #546e7a, #37474f) !important;
        box-shadow: 0 4px 15px rgba(84, 110, 122, 0.4) !important;
    }
    
    .gr-button-secondary:hover {
        background: linear-gradient(135deg, #37474f, #263238) !important;
        transform: translateY(-2px) !important;
    }
    
    /* Accordion */
    .gr-accordion {
        background: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 12px !important;
    }
    
    .gr-accordion summary {
        color: white !important;
        background: rgba(255, 255, 255, 0.1) !important;
        padding: 1rem !important;
        border-radius: 10px !important;
    }
    
    /* Feature cards */
    .feature-card {
        background: rgba(100, 181, 246, 0.1) !important;
        border: 1px solid rgba(100, 181, 246, 0.3) !important;
        border-radius: 12px !important;
        padding: 1.5rem !important;
        margin: 1rem 0 !important;
        border-left: 4px solid #64b5f6 !important;
        backdrop-filter: blur(10px) !important;
    }
    
    .feature-card h3, .feature-card h4 {
        color: #64b5f6 !important;
        margin-bottom: 1rem !important;
    }
    
    .feature-card ul li {
        color: rgba(255, 255, 255, 0.9) !important;
        margin-bottom: 0.5rem !important;
    }
    
    /* Status indicators */
    .status-success {
        background: rgba(76, 175, 80, 0.2) !important;
        border: 1px solid #4caf50 !important;
        border-left: 4px solid #4caf50 !important;
        color: #a5d6a7 !important;
    }
    
    .status-error {
        background: rgba(244, 67, 54, 0.2) !important;
        border: 1px solid #f44336 !important;
        border-left: 4px solid #f44336 !important;
        color: #ef9a9a !important;
    }
    
    /* Hero section */
    .hero-section {
        background: linear-gradient(135deg, #1565c0, #1976d2, #1e88e5) !important;
        border-radius: 15px !important;
        padding: 2rem !important;
        margin-bottom: 2rem !important;
        color: white !important;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3) !important;
        text-align: center !important;
    }
    
    /* Download section */
    .download-section {
        background: rgba(100, 181, 246, 0.1) !important;
        border: 1px solid rgba(100, 181, 246, 0.3) !important;
        border-radius: 12px !important;
        padding: 1.5rem !important;
        text-align: center !important;
        color: white !important;
    }
    
    /* Markdown content area */
    .gr-markdown {
        background: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 10px !important;
        padding: 1.5rem !important;
        max-height: 500px !important;
        overflow-y: auto !important;
    }
    
    /* Responsive design */
    @media (max-width: 768px) {
        .gradio-container {
            padding: 0.5rem !important;
        }
        
        .block {
            margin: 0.25rem !important;
            padding: 1rem !important;
        }
        
        .hero-section {
            padding: 1rem !important;
        }
        
        .feature-card {
            padding: 1rem !important;
            margin: 0.5rem 0 !important;
        }
    }
    
    /* Scrollbar styling */
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: rgba(100, 181, 246, 0.6);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: rgba(100, 181, 246, 0.8);
    }
    """
    
    with gr.Blocks(
        title=f"{APP_NAME} | Advanced AI Research Assistant",
        theme=gr.themes.Base(
            primary_hue="blue",
            secondary_hue="gray",
            neutral_hue="slate",
            text_size="md",
            radius_size="lg",
            spacing_size="lg"
        ).set(
            body_background_fill="linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%)",
            block_background_fill="rgba(255, 255, 255, 0.05)",
            block_border_color="rgba(255, 255, 255, 0.1)",
            block_radius="15px",
            button_primary_background_fill="linear-gradient(135deg, #64b5f6, #42a5f5)",
            button_primary_text_color="white",
            input_background_fill="rgba(255, 255, 255, 0.1)",
            input_border_color="rgba(255, 255, 255, 0.3)",
            body_text_color="white",
            block_label_text_color="white"
        ),
        css=dark_css
    ) as demo:
        
        # Hero Section
        with gr.Row():
            with gr.Column():
                gr.HTML(f"""
                <div class="hero-section">
                    <h1 style="font-size: 3rem; font-weight: bold; margin: 0; text-shadow: 2px 2px 4px rgba(0,0,0,0.3);">
                        🔬 {APP_NAME}
                    </h1>
                    <h2 style="font-size: 1.5rem; margin: 0.5rem 0; opacity: 0.9;">
                        {APP_DESCRIPTION}
                    </h2>
                    <p style="font-size: 1.1rem; margin: 1rem 0; opacity: 0.8;">
                        Powered by Google Gemini AI & Advanced Web Research
                    </p>
                </div>
                """)
        
        # Features Overview
        with gr.Row():
            with gr.Column():
                gr.HTML("""
                <div class="feature-card">
                    <h3>🎯 What this tool does:</h3>
                    <ul style="margin: 1rem 0;">
                        <li><strong>🔍 Intelligent Search:</strong> Uses DuckDuckGo to find the most relevant sources</li>
                        <li><strong>📊 Content Analysis:</strong> Extracts and processes content from multiple websites</li>
                        <li><strong>🤖 AI Synthesis:</strong> Uses Google Gemini to create comprehensive reports</li>
                        <li><strong>📄 Professional Output:</strong> Generates both Markdown and PDF reports</li>
                        <li><strong>⚡ Fast & Reliable:</strong> Automated research in minutes, not hours</li>
                    </ul>
                </div>
                """)
        
        # Simple API Key Section
        with gr.Row():
            with gr.Column():
                gr.HTML("""
                <div class="feature-card">
                    <h3>� API Key Setup</h3>
                    <p>Get your free Gemini API key from <a href="https://aistudio.google.com/" target="_blank" style="color: #64b5f6;">Google AI Studio</a></p>
                </div>
                """)
                
                with gr.Row():
                    with gr.Column(scale=3):
                        gemini_key = gr.Textbox(
                            label="🔐 Enter your Gemini API Key",
                            type="password",
                            placeholder="Paste your API key here...",
                            container=True
                        )
                    with gr.Column(scale=1):
                        validate_btn = gr.Button(
                            "🔍 Validate",
                            variant="secondary",
                            size="lg"
                        )
                
                validation_output = gr.HTML(visible=False)
        
        # Main Research Interface
        gr.HTML("<h2 style='text-align: center; color: #2c3e50; margin: 2rem 0;'>🔬 Start Your Research</h2>")
        
        with gr.Row():
            with gr.Column(scale=2):
                research_topic = gr.Textbox(
                    label="🎯 Research Topic",
                    placeholder="Enter your research topic here... (e.g., 'Latest developments in quantum computing', 'Climate change solutions 2024', 'AI trends in healthcare')",
                    lines=3,
                    container=True
                )
                
                with gr.Row():
                    research_btn = gr.Button(
                        "🚀 Start Deep Research",
                        variant="primary",
                        size="lg",
                        scale=2
                    )
                    with gr.Column(scale=1):
                        gr.HTML("<div style='padding: 1rem;'></div>")
            
            with gr.Column(scale=1):
                gr.HTML("""
                <div class="feature-card">
                    <h4>💡 Research Tips:</h4>
                    <ul style="font-size: 0.9rem;">
                        <li><strong>Be Specific:</strong> "AI in healthcare 2024" vs "AI"</li>
                        <li><strong>Include Context:</strong> Add year, location, or specific aspect</li>
                        <li><strong>Ask Questions:</strong> "What is the impact of...?"</li>
                        <li><strong>Current Events:</strong> Include "latest" or "current"</li>
                        <li><strong>Multiple Angles:</strong> "Causes and solutions of..."</li>
                    </ul>
                    <div style="margin-top: 1rem; padding: 0.8rem; background: rgba(76, 175, 80, 0.1); border-radius: 6px; border-left: 3px solid #4caf50;">
                        <strong>📊 Research Power:</strong><br>
                        <small>10+ sources • Topic categorization • Authoritative domains • AI synthesis</small>
                    </div>
                </div>
                """)
        
        # Progress and Results Section
        with gr.Row():
            with gr.Column():
                progress_html = gr.HTML(visible=False)
                
                output = gr.Markdown(
                    value="Your comprehensive research report will appear here...",
                    label="📊 Research Report",
                    container=True,
                    height=400
                )
        
        # Download Section
        with gr.Row():
            with gr.Column():
                download_section = gr.HTML(visible=False)
                
                with gr.Row():
                    with gr.Column():
                        download_md_btn = gr.DownloadButton(
                            "📝 Download Markdown",
                            visible=False,
                            variant="secondary",
                            size="lg"
                        )
                    with gr.Column():
                        download_pdf_btn = gr.DownloadButton(
                            "📄 Download PDF Report",
                            visible=False,
                            variant="primary",
                            size="lg"
                        )
        
        # Footer
        gr.HTML(f"""
        <div style="text-align: center; padding: 2rem; color: #7f8c8d; border-top: 1px solid #ecf0f1; margin-top: 3rem;">
            <p>🔬 <strong>{APP_NAME} {APP_VERSION}</strong> | Advanced AI Research Assistant</p>
            <p>Powered by Google Gemini AI • Built with ❤️ for researchers worldwide</p>
        </div>
        """)
        
        # Event Handlers
        def validate_key_handler(api_key):
            if not api_key:
                return gr.update(
                    visible=True, 
                    value='<div class="status-error"><h4>❌ API Key Required</h4><p>Please enter your Gemini API key above.</p></div>'
                )
            
            is_valid, message = validate_api_key(api_key)
            if is_valid:
                return gr.update(
                    visible=True,
                    value=f'<div class="status-success"><h4>✅ API Key Valid!</h4><p>{message}</p><p>You\'re ready to start researching!</p></div>'
                )
            else:
                return gr.update(
                    visible=True,
                    value=f'<div class="status-error"><h4>❌ API Key Issue</h4><div style="white-space: pre-line;">{message}</div></div>'
                )
        
        def research_handler(topic, api_key):
            if not api_key.strip():
                return (
                    "❌ Please enter and validate your Gemini API key first.",
                    None, None,
                    gr.update(visible=False),
                    gr.update(visible=False),
                    gr.update(visible=False)
                )
            
            if not topic.strip():
                return (
                    "❌ Please enter a research topic.",
                    None, None,
                    gr.update(visible=False),
                    gr.update(visible=False),
                    gr.update(visible=False)
                )
            
            # Show progress
            progress_msg = f"""
            <div class="feature-card">
                <h4>🔄 Research in Progress...</h4>
                <p>📊 Analyzing: <strong>{topic}</strong></p>
                <p>⏳ This may take 1-2 minutes. Please wait...</p>
            </div>
            """
            
            return run_research(topic, api_key)
        
        # Wire up events
        validate_btn.click(
            fn=validate_key_handler,
            inputs=[gemini_key],
            outputs=[validation_output]
        )
        
        research_btn.click(
            fn=run_research,
            inputs=[research_topic, gemini_key],
            outputs=[output, download_md_btn, download_pdf_btn, download_md_btn, download_pdf_btn]
        )
        
        # Download handlers
        def create_md_file(content):
            if content and content.strip():
                return content
            return "No content available"
        
        def get_pdf_file(pdf_path):
            if pdf_path and os.path.exists(pdf_path):
                return pdf_path
            return None
        
        download_md_btn.click(
            fn=create_md_file,
            inputs=[output],
            outputs=[download_md_btn]
        )
        
        download_pdf_btn.click(
            fn=get_pdf_file,
            inputs=[download_pdf_btn],
            outputs=[download_pdf_btn]
        )
    
    return demo

# Main execution
if __name__ == "__main__":
    demo = create_interface()
    demo.launch()
