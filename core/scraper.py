import requests

def scrape_job_description(url: str) -> str:
    """Uses Jina Reader API to get clean markdown from a URL without installing a browser engine."""
    jina_url = f"https://r.jina.ai/{url}"
    headers = {
        "X-Return-Format": "markdown"
    }
    try:
        print(f"Scraping URL via Jina Reader: {url}...")
        response = requests.get(jina_url, headers=headers)
        response.raise_for_status()
        return response.text
    except Exception as e:
        print(f"Error scraping URL {url}: {e}")
        return ""
