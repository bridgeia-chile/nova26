"""
web_search.py
Provides basic web searching and URL fetching capabilities for Nova26.
"""
import urllib.request
import urllib.parse
from html.parser import HTMLParser

class SimpleHTMLStripper(HTMLParser):
    def __init__(self):
        super().__init__()
        self.reset()
        self.strict = False
        self.convert_charrefs = True
        self.text = []

    def handle_data(self, d):
        self.text.append(d)

    def get_data(self):
        return ''.join(self.text)

class WebSearch:
    def __init__(self):
        # We could use DuckDuckGo HTML Lite or an API like Serper/Tavily.
        # For this standalone tool, a simple DuckDuckGo HTML fetcher works as a baseline.
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Nova26/1.0'}

    def search_duckduckgo(self, query: str) -> dict:
        """Searches DuckDuckGo HTML lite version and returns snippets."""
        url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(query)}"
        req = urllib.request.Request(url, headers=self.headers)
        try:
            with urllib.request.urlopen(req) as response:
                html = response.read().decode('utf-8')
                # Simplistic extraction (In a real scenario, use BeautifulSoup)
                # This is just a proof of concept showing we can fetch the web
                return {"status": "success", "raw_html_hint": "Resultados recabados. Sugerimos usar una API formal para analisis estructurado.", "html_snippet": html[:1500]}
        except Exception as e:
            return {"error": str(e)}

    def fetch_url(self, url: str) -> dict:
        """Fetches the content of a URL and strips basic HTML to get text."""
        if not url.startswith('http'):
            return {"error": "La URL debe comenzar con http o https."}
            
        req = urllib.request.Request(url, headers=self.headers)
        try:
            with urllib.request.urlopen(req) as response:
                html = response.read().decode('utf-8', errors='ignore')
                stripper = SimpleHTMLStripper()
                stripper.feed(html)
                text_content = stripper.get_data()
                return {"status": "success", "content": text_content[:5000] + "\n...(truncado)"} # limit context size
        except Exception as e:
            return {"error": str(e)}
