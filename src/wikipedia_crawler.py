#!/usr/bin/env python3
"""
Wikipedia Music Data Crawler
Automated system for discovering and downloading Wikipedia data about musicians and artists.
"""

import time
import requests
import json
import re
import os
from typing import Dict, List, Any, Optional, Set, Tuple
from pathlib import Path
from urllib.parse import quote, unquote
from bs4 import BeautifulSoup
from dataclasses import dataclass
import logging
from datetime import datetime
import random

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data/crawler.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class CrawlerConfig:
    """Configuration for the Wikipedia crawler"""
    min_delay: float = 1.0  # Minimum delay between requests (seconds)
    max_delay: float = 3.0  # Maximum delay between requests (seconds)
    max_retries: int = 3    # Maximum retries for failed requests
    timeout: int = 30       # Request timeout (seconds)
    user_agent: str = "MusicNetworkCrawler/1.0 (Educational Research)"
    max_artists_per_session: int = 100  # Limit for single crawling session
    save_html: bool = True  # Whether to save raw HTML
    save_api_data: bool = True  # Whether to save API responses

class WikipediaCrawler:
    """Main crawler class for Wikipedia music data"""
    
    def __init__(self, config: CrawlerConfig = None):
        self.config = config or CrawlerConfig()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': self.config.user_agent
        })
        
        # Track crawled artists to avoid duplicates
        self.crawled_artists = set()
        self.failed_artists = set()
        
        # Create directories
        self.html_dir = Path("data/raw_html")
        self.api_dir = Path("data/api_responses")
        self.html_dir.mkdir(parents=True, exist_ok=True)
        self.api_dir.mkdir(parents=True, exist_ok=True)
        
        # Wikipedia API endpoints
        self.api_base = "https://en.wikipedia.org/api/rest_v1"
        self.wiki_api_base = "https://en.wikipedia.org/w/api.php"
        
    def _delay(self):
        """Add random delay between requests"""
        delay = random.uniform(self.config.min_delay, self.config.max_delay)
        time.sleep(delay)
    
    def _make_request(self, url: str, params: Dict = None) -> Optional[requests.Response]:
        """Make HTTP request with retries and error handling"""
        for attempt in range(self.config.max_retries):
            try:
                self._delay()
                response = self.session.get(
                    url, 
                    params=params,
                    timeout=self.config.timeout
                )
                
                if response.status_code == 200:
                    return response
                elif response.status_code == 429:  # Rate limited
                    wait_time = int(response.headers.get('Retry-After', 60))
                    logger.warning(f"Rate limited. Waiting {wait_time} seconds...")
                    time.sleep(wait_time)
                    continue
                else:
                    logger.warning(f"HTTP {response.status_code} for {url}")
                    
            except requests.RequestException as e:
                logger.error(f"Request failed (attempt {attempt + 1}): {e}")
                if attempt < self.config.max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
        
        return None
    
    def search_artists(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search for artists using Wikipedia API"""
        params = {
            'action': 'query',
            'format': 'json',
            'list': 'search',
            'srsearch': f'"{query}" incategory:"American musicians" OR incategory:"British musicians" OR incategory:"English musicians"',
            'srlimit': limit
        }
        
        response = self._make_request(self.wiki_api_base, params)
        if not response:
            return []
        
        try:
            data = response.json()
            results = []
            
            for item in data.get('query', {}).get('search', []):
                results.append({
                    'title': item['title'],
                    'snippet': item.get('snippet', ''),
                    'size': item.get('size', 0),
                    'wordcount': item.get('wordcount', 0)
                })
            
            return results
            
        except Exception as e:
            logger.error(f"Error parsing search results: {e}")
            return []
    
    def get_page_info(self, title: str) -> Optional[Dict[str, Any]]:
        """Get detailed page information using Wikipedia API"""
        params = {
            'action': 'query',
            'format': 'json',
            'titles': title,
            'prop': 'info|categories|links|extracts',
            'inprop': 'url',
            'exintro': True,
            'explaintext': True,
            'exlimit': 1
        }
        
        response = self._make_request(self.wiki_api_base, params)
        if not response:
            return None
        
        try:
            data = response.json()
            pages = data.get('query', {}).get('pages', {})
            
            for page_id, page_data in pages.items():
                if page_id != '-1':  # Page exists
                    return {
                        'pageid': page_data.get('pageid'),
                        'title': page_data.get('title'),
                        'url': page_data.get('fullurl'),
                        'extract': page_data.get('extract', ''),
                        'categories': [cat['title'] for cat in page_data.get('categories', [])],
                        'links': [link['title'] for link in page_data.get('links', [])]
                    }
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting page info for {title}: {e}")
            return None
    
    def download_page_html(self, title: str) -> Optional[str]:
        """Download raw HTML of Wikipedia page"""
        url = f"https://en.wikipedia.org/wiki/{quote(title)}"
        
        response = self._make_request(url)
        if not response:
            return None
        
        return response.text
    
    def is_music_related_page(self, page_info: Dict[str, Any]) -> bool:
        """Check if a Wikipedia page is music-related"""
        if not page_info:
            return False
        
        # Check categories
        categories = [cat.lower() for cat in page_info.get('categories', [])]
        music_categories = [
            'musicians', 'singers', 'bands', 'artists', 'composers',
            'songwriters', 'music', 'albums', 'songs', 'record producers'
        ]
        
        category_match = any(
            any(music_cat in cat for music_cat in music_categories)
            for cat in categories
        )
        
        # Check extract text
        extract = page_info.get('extract', '').lower()
        music_keywords = [
            'musician', 'singer', 'band', 'artist', 'album', 'song',
            'music', 'guitarist', 'drummer', 'vocalist', 'songwriter',
            'composer', 'record', 'tour', 'concert'
        ]
        
        text_match = any(keyword in extract for keyword in music_keywords)
        
        return category_match or text_match
    
    def extract_related_artists(self, page_info: Dict[str, Any]) -> List[str]:
        """Extract names of related artists from page information"""
        if not page_info:
            return []
        
        related_artists = []
        
        # Extract from links
        links = page_info.get('links', [])
        for link in links:
            # Skip non-artist pages
            if any(skip in link.lower() for skip in [
                'category:', 'list of', 'discography', 'album', 'song',
                'tour', 'concert', 'festival', 'award', 'year in music'
            ]):
                continue
            
            # Look for patterns that suggest artist pages
            if re.search(r'\((band|singer|musician|artist|group)\)', link.lower()):
                related_artists.append(link)
        
        # Extract from categories
        categories = page_info.get('categories', [])
        for category in categories:
            # Extract artists from band member categories
            if 'members' in category.lower():
                # This would need more sophisticated parsing
                pass
        
        return list(set(related_artists))  # Remove duplicates
    
    def crawl_artist(self, artist_name: str) -> Dict[str, Any]:
        """Crawl a single artist's Wikipedia page"""
        if artist_name in self.crawled_artists:
            logger.info(f"Already crawled: {artist_name}")
            return {'status': 'already_crawled'}
        
        if artist_name in self.failed_artists:
            logger.info(f"Previously failed: {artist_name}")
            return {'status': 'previously_failed'}
        
        logger.info(f"Crawling artist: {artist_name}")
        
        try:
            # Get page information
            page_info = self.get_page_info(artist_name)
            if not page_info:
                logger.warning(f"Page not found: {artist_name}")
                self.failed_artists.add(artist_name)
                return {'status': 'page_not_found'}
            
            # Check if it's music-related
            if not self.is_music_related_page(page_info):
                logger.info(f"Not music-related: {artist_name}")
                return {'status': 'not_music_related'}
            
            result = {
                'status': 'success',
                'artist_name': artist_name,
                'page_info': page_info,
                'related_artists': [],
                'html_saved': False,
                'api_saved': False
            }
            
            # Download HTML if requested
            if self.config.save_html:
                html_content = self.download_page_html(artist_name)
                if html_content:
                    # Save HTML file
                    filename = re.sub(r'[^\w\s-]', '', artist_name).strip()
                    filename = re.sub(r'[-\s]+', '_', filename).lower()
                    html_path = self.html_dir / f"{filename}.html"
                    
                    with open(html_path, 'w', encoding='utf-8') as f:
                        f.write(html_content)
                    
                    result['html_saved'] = True
                    result['html_path'] = str(html_path)
                    logger.info(f"HTML saved: {html_path}")
            
            # Save API data if requested
            if self.config.save_api_data:
                filename = re.sub(r'[^\w\s-]', '', artist_name).strip()
                filename = re.sub(r'[-\s]+', '_', filename).lower()
                api_path = self.api_dir / f"{filename}.json"
                
                with open(api_path, 'w', encoding='utf-8') as f:
                    json.dump(page_info, f, indent=2, ensure_ascii=False)
                
                result['api_saved'] = True
                result['api_path'] = str(api_path)
                logger.info(f"API data saved: {api_path}")
            
            # Extract related artists
            related_artists = self.extract_related_artists(page_info)
            result['related_artists'] = related_artists
            
            self.crawled_artists.add(artist_name)
            return result
            
        except Exception as e:
            logger.error(f"Error crawling {artist_name}: {e}")
            self.failed_artists.add(artist_name)
            return {'status': 'error', 'error': str(e)}
    
    def discover_artists_by_genre(self, genre: str, limit: int = 20) -> List[str]:
        """Discover artists by searching for a specific genre"""
        search_queries = [
            f"{genre} musicians",
            f"{genre} bands",
            f"{genre} singers",
            f"American {genre}",
            f"British {genre}",
            f"English {genre}"
        ]
        
        discovered_artists = set()
        
        for query in search_queries:
            results = self.search_artists(query, limit=limit//len(search_queries))
            for result in results:
                title = result['title']
                # Filter out non-artist pages
                if not any(skip in title.lower() for skip in [
                    'category:', 'list of', 'discography', 'album',
                    'tour', 'concert', 'festival', 'year in'
                ]):
                    discovered_artists.add(title)
        
        return list(discovered_artists)[:limit]
    
    def crawl_artist_network(self, seed_artists: List[str], max_depth: int = 2, max_artists: int = 50) -> Dict[str, Any]:
        """Crawl a network of artists starting from seed artists"""
        logger.info(f"Starting network crawl with {len(seed_artists)} seed artists")
        
        artists_to_crawl = set(seed_artists)
        crawl_results = {}
        current_depth = 0
        
        while current_depth < max_depth and artists_to_crawl and len(self.crawled_artists) < max_artists:
            current_batch = list(artists_to_crawl)
            artists_to_crawl.clear()
            
            logger.info(f"Crawling depth {current_depth + 1}: {len(current_batch)} artists")
            
            for artist in current_batch:
                if len(self.crawled_artists) >= max_artists:
                    break
                
                result = self.crawl_artist(artist)
                crawl_results[artist] = result
                
                # Add related artists for next depth level
                if result.get('status') == 'success' and current_depth < max_depth - 1:
                    related = result.get('related_artists', [])
                    # Limit related artists to avoid explosion
                    related = related[:5]  # Top 5 related artists
                    
                    for related_artist in related:
                        if (related_artist not in self.crawled_artists and 
                            related_artist not in self.failed_artists):
                            artists_to_crawl.add(related_artist)
            
            current_depth += 1
        
        summary = {
            'total_attempted': len(crawl_results),
            'successful_crawls': len([r for r in crawl_results.values() if r.get('status') == 'success']),
            'failed_crawls': len([r for r in crawl_results.values() if r.get('status') not in ['success', 'already_crawled']]),
            'depths_crawled': current_depth,
            'results': crawl_results
        }
        
        return summary
    
    def save_crawl_session(self, results: Dict[str, Any], filename: str = None):
        """Save crawling session results"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"crawl_session_{timestamp}.json"
        
        filepath = Path("data/processed") / filename
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        session_data = {
            'timestamp': datetime.now().isoformat(),
            'config': {
                'min_delay': self.config.min_delay,
                'max_delay': self.config.max_delay,
                'max_artists_per_session': self.config.max_artists_per_session
            },
            'crawled_artists': list(self.crawled_artists),
            'failed_artists': list(self.failed_artists),
            'results': results
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(session_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Crawl session saved: {filepath}")
        return filepath

def main():
    """Demo the crawler functionality"""
    print("=== WIKIPEDIA MUSIC CRAWLER DEMO ===\n")
    
    # Configure crawler
    config = CrawlerConfig(
        min_delay=1.0,
        max_delay=2.0,
        max_artists_per_session=20,
        save_html=True,
        save_api_data=True
    )
    
    crawler = WikipediaCrawler(config)
    
    # Example 1: Search for artists
    print("1. SEARCHING FOR ROCK ARTISTS:")
    rock_artists = crawler.discover_artists_by_genre("rock", limit=10)
    print(f"Found {len(rock_artists)} rock-related pages:")
    for artist in rock_artists[:5]:
        print(f"  - {artist}")
    
    # Example 2: Crawl specific artists
    print("\n2. CRAWLING SPECIFIC ARTISTS:")
    seed_artists = ["Radiohead", "Arctic Monkeys", "Coldplay"]
    
    for artist in seed_artists:
        print(f"\nCrawling: {artist}")
        result = crawler.crawl_artist(artist)
        print(f"Status: {result.get('status')}")
        
        if result.get('status') == 'success':
            print(f"Related artists found: {len(result.get('related_artists', []))}")
            if result.get('related_artists'):
                print(f"Sample related: {', '.join(result['related_artists'][:3])}")
    
    # Example 3: Network crawling
    print("\n3. NETWORK CRAWLING:")
    network_results = crawler.crawl_artist_network(
        seed_artists=["Oasis"],
        max_depth=2,
        max_artists=10
    )
    
    print(f"Network crawl summary:")
    print(f"  Total attempted: {network_results['total_attempted']}")
    print(f"  Successful: {network_results['successful_crawls']}")
    print(f"  Failed: {network_results['failed_crawls']}")
    print(f"  Depths crawled: {network_results['depths_crawled']}")
    
    # Save session
    session_file = crawler.save_crawl_session(network_results)
    print(f"\nSession saved to: {session_file}")
    
    print("\n=== CRAWLING COMPLETE ===")
    print("Check the following directories for downloaded data:")
    print(f"  HTML files: {crawler.html_dir}")
    print(f"  API responses: {crawler.api_dir}")
    print("  Session data: data/processed/")

if __name__ == "__main__":
    main()
