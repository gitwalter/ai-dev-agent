# LangChain Web Scraping Integration

**Created:** 2025-10-10  
**Status:** ✅ Integrated into Research Swarm  
**Purpose:** Document LangChain web scraping and parsing capabilities

---

## 🎯 Overview

Our **Web Research Swarm** uses LangChain's powerful document loaders and transformers for robust web scraping and content extraction.

---

## 📦 LangChain Components Used

### **1. Document Loaders**

#### **AsyncHtmlLoader** ✅ (Currently Integrated)
```python
from langchain_community.document_loaders import AsyncHtmlLoader

# Load multiple URLs asynchronously
loader = AsyncHtmlLoader(["https://example.com/page1", "https://example.com/page2"])
docs = loader.load()
```

**Benefits:**
- ✅ Async loading for multiple URLs
- ✅ Efficient batch processing
- ✅ Built-in error handling
- ✅ Returns structured Document objects

#### **WebBaseLoader** (Alternative)
```python
from langchain_community.document_loaders import WebBaseLoader

# Simple single URL loading
loader = WebBaseLoader("https://example.com")
docs = loader.load()
```

**Benefits:**
- ✅ Simple API for single URLs
- ✅ BeautifulSoup integration
- ✅ CSS selector support

### **2. Document Transformers**

#### **Html2TextTransformer** ✅ (Currently Integrated)
```python
from langchain_community.document_transformers import Html2TextTransformer

# Transform HTML to clean markdown/text
html2text = Html2TextTransformer()
cleaned_docs = html2text.transform_documents(html_docs)
```

**Benefits:**
- ✅ Converts HTML to clean text
- ✅ Preserves structure (headers, lists)
- ✅ Removes scripts, styles, navigation
- ✅ Markdown output option

#### **BeautifulSoupTransformer** (Available)
```python
from langchain_community.document_transformers import BeautifulSoupTransformer

# Advanced HTML parsing with selectors
bs_transformer = BeautifulSoupTransformer()
transformed = bs_transformer.transform_documents(
    docs, 
    tags_to_extract=["article", "main", "div.content"]
)
```

**Benefits:**
- ✅ CSS selector-based extraction
- ✅ Flexible tag filtering
- ✅ Preserves semantic structure

### **3. Text Splitters**

#### **RecursiveCharacterTextSplitter** (Available for Integration)
```python
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Smart text chunking
splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
    separators=["\n\n", "\n", " ", ""]
)
chunks = splitter.split_documents(docs)
```

**Benefits:**
- ✅ Semantic-aware splitting
- ✅ Configurable chunk size
- ✅ Overlap for context preservation

---

## 🏗️ Current Implementation

### **ContentParserAgent** (agents/research/content_parser_agent.py)

```python
async def _extract_raw_content(self, result: Dict) -> str:
    """Extract content using LangChain loaders."""
    
    if LANGCHAIN_PARSING_AVAILABLE:
        # Use LangChain's async HTML loader
        loader = AsyncHtmlLoader([url])
        docs = loader.load()
        
        # Transform HTML to clean text
        html2text = Html2TextTransformer()
        transformed_docs = html2text.transform_documents(docs)
        
        # Extract cleaned content
        content = transformed_docs[0].page_content
        return self._clean_content(content)
```

**Fallback Hierarchy:**
1. ✅ **LangChain** (AsyncHtmlLoader + Html2TextTransformer)
2. ⚠️ **BeautifulSoup** (Direct HTML parsing)
3. 🔄 **Simulated** (For testing without network)

---

## 🚀 Advanced Features (Available for Future Integration)

### **1. JavaScript-Heavy Sites**

#### **AsyncChromiumLoader** (Requires Playwright)
```python
from langchain_community.document_loaders import AsyncChromiumLoader

# Load JavaScript-rendered pages
loader = AsyncChromiumLoader(["https://spa-website.com"])
docs = loader.load()
```

**Setup:**
```bash
pip install playwright
playwright install
```

### **2. Sitemap Scraping**

#### **SitemapLoader**
```python
from langchain_community.document_loaders import SitemapLoader

# Scrape entire sitemap
loader = SitemapLoader("https://example.com/sitemap.xml")
docs = loader.load()
```

### **3. Recursive Crawling**

#### **RecursiveUrlLoader**
```python
from langchain_community.document_loaders import RecursiveUrlLoader

# Recursively crawl website
loader = RecursiveUrlLoader(
    "https://example.com",
    max_depth=2,
    extractor=lambda html: BeautifulSoup(html).get_text()
)
docs = loader.load()
```

---

## 📊 Integration Status

| Component | Status | File | Notes |
|-----------|--------|------|-------|
| AsyncHtmlLoader | ✅ Integrated | content_parser_agent.py | Async URL loading |
| Html2TextTransformer | ✅ Integrated | content_parser_agent.py | HTML to clean text |
| BeautifulSoupTransformer | 📋 Available | - | For advanced parsing |
| RecursiveTextSplitter | 📋 Available | - | For chunking long content |
| AsyncChromiumLoader | 📋 Available | - | For JS-heavy sites |
| SitemapLoader | 📋 Available | - | For sitemap scraping |
| RecursiveUrlLoader | 📋 Available | - | For site crawling |

---

## 🔧 Configuration

### **Install Full LangChain Web Tools**
```bash
# Core LangChain web scraping
pip install langchain-community

# HTML parsing
pip install beautifulsoup4 html2text lxml

# JavaScript rendering (optional)
pip install playwright
playwright install chromium

# Advanced scraping (optional)
pip install selenium
```

### **Environment Variables**
```bash
# Optional: API keys for commercial scrapers
OXYLABS_API_KEY=your_key_here
BRIGHTDATA_API_KEY=your_key_here

# User agent for polite scraping
USER_AGENT="Mozilla/5.0 (Research Bot)"
```

---

## 🎯 Best Practices

### **1. Respectful Scraping**
- ✅ Check `robots.txt` before scraping
- ✅ Implement rate limiting (1-2 seconds between requests)
- ✅ Use meaningful User-Agent strings
- ✅ Cache results to avoid repeated requests

### **2. Error Handling**
```python
try:
    docs = loader.load()
except Exception as e:
    logger.error(f"Scraping failed: {e}")
    # Fallback to cached or simulated content
```

### **3. Content Quality**
- ✅ Remove navigation, ads, footers
- ✅ Extract main content only
- ✅ Preserve semantic structure
- ✅ Handle multiple encodings

### **4. Performance**
- ✅ Use async loaders for multiple URLs
- ✅ Batch process when possible
- ✅ Cache frequently accessed content
- ✅ Set reasonable timeouts

---

## 📚 Resources

- [LangChain Document Loaders](https://python.langchain.com/docs/modules/data_connection/document_loaders/)
- [LangChain Web Scraping Guide](https://python.langchain.com/docs/use_cases/web_scraping/)
- [BeautifulSoup Documentation](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)
- [Playwright for Python](https://playwright.dev/python/)

---

## 🔄 Next Steps

1. **Enhance WebSearchAgent** - Integrate real search APIs (Google, Bing, DuckDuckGo)
2. **Add JavaScript Support** - Integrate AsyncChromiumLoader for SPA sites
3. **Implement Caching** - Cache scraped content to reduce network calls
4. **Add Sitemap Support** - Enable full site scraping via sitemaps
5. **Quality Filters** - Implement content quality scoring and filtering

---

**Status:** ✅ LangChain web scraping successfully integrated into Research Swarm  
**Next:** Real search API integration and JavaScript rendering support

