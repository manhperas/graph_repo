#!/usr/bin/env python3
"""
Wikipedia Music Network Analyzer
Analyzes Wikipedia pages of musicians and singers to extract network information.
"""

import os
import re
from bs4 import BeautifulSoup
from typing import Dict, List, Any, Optional
import json
from dataclasses import dataclass
from pathlib import Path

@dataclass
class ArtistInfo:
    """Data class for storing artist information"""
    name: str
    origin: str = ""
    genres: List[str] = None
    instruments: List[str] = None
    years_active: str = ""
    labels: List[str] = None
    associated_acts: List[str] = None
    members: List[str] = None
    past_members: List[str] = None
    website: str = ""
    
    def __post_init__(self):
        if self.genres is None:
            self.genres = []
        if self.instruments is None:
            self.instruments = []
        if self.labels is None:
            self.labels = []
        if self.associated_acts is None:
            self.associated_acts = []
        if self.members is None:
            self.members = []
        if self.past_members is None:
            self.past_members = []

class WikipediaAnalyzer:
    """Analyzes Wikipedia pages to extract musician network data"""
    
    def __init__(self, data_dir: str = "data/raw_html/"):
        self.data_dir = Path(data_dir)
        self.artists = {}
        
    def load_html_file(self, filename: str) -> BeautifulSoup:
        """Load and parse HTML file"""
        file_path = self.data_dir / filename
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return BeautifulSoup(content, 'html.parser')
    
    def extract_infobox_data(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract data from Wikipedia infobox"""
        infobox_data = {}
        
        # Find the infobox table
        infobox = soup.find('table', class_=re.compile(r'infobox'))
        if not infobox:
            return infobox_data
        
        # Extract all rows from infobox
        rows = infobox.find_all('tr')
        
        for row in rows:
            # Look for rows with both th (header) and td (data) elements
            header = row.find('th')
            data = row.find('td')
            
            if header and data:
                key = header.get_text(strip=True).lower()
                value = data.get_text(separator='|', strip=True)
                
                # Clean up the value
                value = re.sub(r'\[\d+\]', '', value)  # Remove citation numbers
                value = re.sub(r'\s+', ' ', value)     # Normalize whitespace
                
                infobox_data[key] = value
        
        return infobox_data
    
    def parse_list_field(self, value: str) -> List[str]:
        """Parse comma or pipe-separated values into list"""
        if not value:
            return []
        
        # Split by common separators
        items = re.split(r'[,|•·]', value)
        
        # Clean each item
        cleaned_items = []
        for item in items:
            cleaned = item.strip()
            if cleaned and cleaned not in ['', 'various']:
                cleaned_items.append(cleaned)
        
        return cleaned_items
    
    def extract_artist_info(self, soup: BeautifulSoup, artist_name: str) -> ArtistInfo:
        """Extract structured artist information from Wikipedia page"""
        infobox_data = self.extract_infobox_data(soup)
        
        # Map infobox fields to our data structure
        artist_info = ArtistInfo(name=artist_name)
        
        # Extract origin
        for key in ['origin', 'background', 'birth_place']:
            if key in infobox_data:
                artist_info.origin = infobox_data[key]
                break
        
        # Extract genres
        for key in ['genre', 'genres', 'style']:
            if key in infobox_data:
                artist_info.genres = self.parse_list_field(infobox_data[key])
                break
        
        # Extract instruments
        for key in ['instrument', 'instruments']:
            if key in infobox_data:
                artist_info.instruments = self.parse_list_field(infobox_data[key])
                break
        
        # Extract years active
        for key in ['years_active', 'years active', 'active']:
            if key in infobox_data:
                artist_info.years_active = infobox_data[key]
                break
        
        # Extract labels
        for key in ['label', 'labels', 'record_label']:
            if key in infobox_data:
                artist_info.labels = self.parse_list_field(infobox_data[key])
                break
        
        # Extract associated acts
        for key in ['associated_acts', 'associated acts', 'related']:
            if key in infobox_data:
                artist_info.associated_acts = self.parse_list_field(infobox_data[key])
                break
        
        # Extract members (for bands)
        for key in ['members', 'current_members']:
            if key in infobox_data:
                artist_info.members = self.parse_list_field(infobox_data[key])
                break
        
        # Extract past members
        for key in ['past_members', 'former_members']:
            if key in infobox_data:
                artist_info.past_members = self.parse_list_field(infobox_data[key])
                break
        
        # Extract website
        for key in ['website', 'url']:
            if key in infobox_data:
                artist_info.website = infobox_data[key]
                break
        
        return artist_info
    
    def extract_internal_links(self, soup: BeautifulSoup) -> List[str]:
        """Extract internal Wikipedia links that might represent connections"""
        links = []
        
        # Find all internal Wikipedia links
        for link in soup.find_all('a', href=True):
            href = link.get('href')
            if href and href.startswith('/wiki/') and ':' not in href:
                # Extract the page title from the URL
                page_title = href[6:].replace('_', ' ')  # Remove '/wiki/' and replace underscores
                links.append(page_title)
        
        return list(set(links))  # Remove duplicates
    
    def analyze_artist_page(self, filename: str, artist_name: str) -> Dict[str, Any]:
        """Analyze a single artist Wikipedia page"""
        soup = self.load_html_file(filename)
        
        # Extract structured artist information
        artist_info = self.extract_artist_info(soup, artist_name)
        
        # Extract internal links for potential connections
        internal_links = self.extract_internal_links(soup)
        
        # Filter links to likely music-related pages
        music_related_links = self.filter_music_related_links(internal_links)
        
        return {
            'artist_info': artist_info,
            'raw_infobox': self.extract_infobox_data(soup),
            'music_related_links': music_related_links[:50],  # Limit to first 50
            'total_links': len(internal_links)
        }
    
    def filter_music_related_links(self, links: List[str]) -> List[str]:
        """Filter links to those likely related to music"""
        music_keywords = [
            'album', 'single', 'song', 'band', 'musician', 'singer', 'artist',
            'record', 'music', 'tour', 'concert', 'festival', 'label',
            'producer', 'songwriter', 'composer', 'discography'
        ]
        
        filtered_links = []
        for link in links:
            link_lower = link.lower()
            # Check if link contains music-related keywords
            if any(keyword in link_lower for keyword in music_keywords):
                filtered_links.append(link)
            # Also include if it looks like an artist name (contains parentheses with "band", "singer", etc.)
            elif re.search(r'\(.*(?:band|singer|musician|artist|group).*\)', link_lower):
                filtered_links.append(link)
        
        return filtered_links
    
    def analyze_all_samples(self) -> Dict[str, Any]:
        """Analyze all HTML files in the data directory"""
        html_files = list(self.data_dir.glob("*.html"))
        
        if not html_files:
            print("No HTML files found in data directory!")
            return {}
        
        results = {}
        for html_file in html_files:
            filename = html_file.name
            # Convert filename to artist name
            artist_name = self.filename_to_artist_name(filename)
            
            try:
                print(f"Analyzing {artist_name} ({filename})...")
                results[artist_name] = self.analyze_artist_page(filename, artist_name)
            except Exception as e:
                print(f"Error analyzing {artist_name}: {str(e)}")
                results[artist_name] = {'error': str(e)}
        
        return results
    
    def filename_to_artist_name(self, filename: str) -> str:
        """Convert HTML filename to readable artist name"""
        # Remove .html extension
        name = filename.replace('.html', '')
        
        # Replace underscores with spaces and title case
        name = name.replace('_', ' ').title()
        
        # Handle special cases
        name_mapping = {
            'The Beatles': 'The Beatles',
            'Ed Sheeran': 'Ed Sheeran',
            'Taylor Swift': 'Taylor Swift',
            'Arctic Monkeys': 'Arctic Monkeys',
            'Green Day': 'Green Day',
            'Foo Fighters': 'Foo Fighters'
        }
        
        return name_mapping.get(name, name)
    
    def save_analysis_results(self, results: Dict[str, Any], output_file: str = "data/processed/analysis_results.json"):
        """Save analysis results to JSON file"""
        # Convert dataclasses to dictionaries for JSON serialization
        serializable_results = {}
        for artist, data in results.items():
            if 'error' in data:
                serializable_results[artist] = data
            else:
                serializable_results[artist] = {
                    'artist_info': {
                        'name': data['artist_info'].name,
                        'origin': data['artist_info'].origin,
                        'genres': data['artist_info'].genres,
                        'instruments': data['artist_info'].instruments,
                        'years_active': data['artist_info'].years_active,
                        'labels': data['artist_info'].labels,
                        'associated_acts': data['artist_info'].associated_acts,
                        'members': data['artist_info'].members,
                        'past_members': data['artist_info'].past_members,
                        'website': data['artist_info'].website
                    },
                    'raw_infobox': data['raw_infobox'],
                    'music_related_links': data['music_related_links'],
                    'total_links': data['total_links']
                }
        
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(serializable_results, f, indent=2, ensure_ascii=False)
        
        print(f"Results saved to {output_file}")

def main():
    """Main function to run the analysis"""
    analyzer = WikipediaAnalyzer()
    results = analyzer.analyze_all_samples()
    analyzer.save_analysis_results(results)
    
    # Print summary
    print("\n=== ANALYSIS SUMMARY ===")
    for artist, data in results.items():
        if 'error' in data:
            print(f"{artist}: ERROR - {data['error']}")
        else:
            info = data['artist_info']
            print(f"\n{artist}:")
            print(f"  Origin: {info.origin}")
            print(f"  Genres: {', '.join(info.genres[:3])}{'...' if len(info.genres) > 3 else ''}")
            print(f"  Years Active: {info.years_active}")
            print(f"  Associated Acts: {len(info.associated_acts)} found")
            print(f"  Music-related Links: {len(data['music_related_links'])}")

if __name__ == "__main__":
    main()
