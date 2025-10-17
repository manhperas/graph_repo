# Wikipedia Music Crawler Usage Guide

This guide explains how to use the automated Wikipedia crawler system to download and analyze artist data for your music network.

## Overview

The crawler system provides three main ways to collect artist data:

1. **Specific Artist Crawler** - Download data for specific artists you name
2. **Batch Downloader** - Download curated collections of popular artists
3. **Network Crawler** - Automatically discover related artists through connections

## Installation and Setup

Make sure you have all dependencies installed:

```bash
pip install -r requirements.txt
```

The crawler will automatically create necessary directories:
- `data/raw_html/` - Downloaded Wikipedia HTML pages
- `data/api_responses/` - Structured API responses
- `data/processed/` - Analysis results and session logs

## Method 1: Download Specific Artists

Use this when you know exactly which artists you want to analyze.

### Basic Usage

```bash
python src/crawl_artists.py artists "Artist Name 1" "Artist Name 2" "Artist Name 3"
```

### Examples

```bash
# Download a few specific artists
python src/crawl_artists.py artists "Radiohead" "Arctic Monkeys" "Coldplay"

# Download with custom delay (slower = more polite)
python src/crawl_artists.py artists "Green Day" "Foo Fighters" --delay 2.0

# Download many artists at once
python src/crawl_artists.py artists "Pink Floyd" "Led Zeppelin" "Queen" "The Who" "Black Sabbath"
```

### What it does:
- Downloads Wikipedia HTML page for each artist
- Extracts structured data via Wikipedia API
- Saves both raw HTML and JSON data
- Provides success/failure status for each artist
- Respects rate limits with configurable delays

## Method 2: Batch Download Popular Artists

Use this for quick setup with curated lists of popular artists.

### Interactive Mode

```bash
python src/batch_download.py
```

This will show you a menu with options:
1. **Starter Pack** - 16 diverse artists (recommended for beginners)
2. **Specific Category** - Choose from predefined categories
3. **Multiple Categories** - Download several categories at once

### Available Categories

- **uk_classic_rock**: The Beatles, Led Zeppelin, Queen, Pink Floyd, Rolling Stones...
- **uk_modern_rock**: Radiohead, Coldplay, Oasis, Blur, Arctic Monkeys...
- **uk_pop**: Ed Sheeran, Adele, Sam Smith, Dua Lipa, Harry Styles...
- **us_classic_rock**: Nirvana, Pearl Jam, Soundgarden, Alice in Chains...
- **us_pop**: Taylor Swift, Ariana Grande, Billie Eilish, The Weeknd...
- **us_hip_hop**: Jay-Z, Kanye West, Eminem, Drake, Travis Scott...
- **alternative_indie**: Vampire Weekend, The Strokes, Arcade Fire...

### Examples

Quick start with diverse artists:
```bash
# Option 1 in the menu downloads these 16 artists:
# The Beatles, Queen, Led Zeppelin, Radiohead, Coldplay, Arctic Monkeys,
# Ed Sheeran, Adele, Nirvana, Pearl Jam, Taylor Swift, Bruno Mars,
# Kanye West, Drake, The Strokes, Vampire Weekend
```

## Method 3: Network Discovery Crawling

Use this to automatically discover related artists through Wikipedia connections.

### Basic Network Crawling

```bash
python src/crawl_artists.py network "Seed Artist 1" "Seed Artist 2"
```

### Advanced Options

```bash
# Deeper crawling (more discovery levels)
python src/crawl_artists.py network "Radiohead" --depth 3 --max-artists 50

# Faster crawling
python src/crawl_artists.py network "The Beatles" --depth 2 --max-artists 20 --delay 1.0
```

### Parameters Explained

- **--depth**: How many "levels" of connections to follow (default: 2)
  - Depth 1: Only direct connections to seed artists
  - Depth 2: Connections of connections
  - Depth 3: Even more distant relationships
  
- **--max-artists**: Maximum total artists to download (default: 20)
- **--delay**: Delay between requests in seconds (default: 2.0)

### How Network Discovery Works

1. **Level 1**: Analyze seed artist pages and extract related artists from:
   - Wikipedia links to other artist pages
   - Associated acts mentioned in infoboxes
   - Collaboration references

2. **Level 2**: Analyze the discovered artists and find their connections

3. **Continue** until reaching max depth or artist limit

## Genre-Based Discovery

Discover artists by musical genre:

```bash
python src/crawl_artists.py genre "rock" --limit 15
python src/crawl_artists.py genre "electronic" --limit 10
python src/crawl_artists.py genre "jazz" --limit 12
```

This will:
1. Search Wikipedia for artists in that genre
2. Show you the discovered artists
3. Let you choose which ones to download

## Complete Workflow

Here's the recommended workflow for building your music network:

### Step 1: Download Artist Data

Choose one of these approaches:

```bash
# Option A: Quick start with diverse artists
python src/batch_download.py
# Choose option 1 (Starter Pack)

# Option B: Specific artists you're interested in
python src/crawl_artists.py artists "Your" "Favorite" "Artists"

# Option C: Network discovery from seeds
python src/crawl_artists.py network "Starting Artist" --depth 2 --max-artists 30
```

### Step 2: Analyze the Downloaded Data

```bash
python src/wikipedia_analyzer.py
```

This processes all HTML files and extracts:
- Artist information (origin, genres, years active)
- Record labels
- Musical instruments
- Potential collaborations

### Step 3: Build the Network Graph

```bash
python src/network_builder.py
```

This creates:
- Network nodes (artists, genres, labels)
- Relationship edges (collaborations, genre associations, label signings)
- Graph files in multiple formats (GEXF, JSON)

### Step 4: Query and Analyze

```bash
python src/network_queries.py
```

This demonstrates various network analysis capabilities:
- Find connections between artists
- Identify most influential artists
- Analyze genre distributions
- Path finding through the network

## Configuration Options

### Crawler Politeness Settings

```python
# In your scripts, you can customize these settings:
config = CrawlerConfig(
    min_delay=1.0,        # Minimum delay between requests
    max_delay=3.0,        # Maximum delay between requests
    max_retries=3,        # Retry failed requests
    timeout=30,           # Request timeout
    save_html=True,       # Save raw HTML files
    save_api_data=True    # Save structured API responses
)
```

### Rate Limiting Best Practices

- **Academic/Research Use**: 1-3 second delays are appropriate
- **Large Scale Crawling**: Use 2-5 second delays
- **Respectful Crawling**: The crawler automatically handles rate limiting

## Troubleshooting

### Common Issues

**"Page not found" errors:**
- Check spelling of artist names
- Try variations (e.g., "The Beatles" vs "Beatles")
- Some artists may not have Wikipedia pages

**"Not music-related" warnings:**
- The crawler filters out non-music pages automatically
- Some disambiguation pages may be filtered out
- Try more specific artist names

**Rate limiting:**
- The crawler automatically handles this
- If you see many 429 errors, increase the delay settings

### Checking Your Data

View downloaded files:
```bash
ls -la data/raw_html/      # HTML files
ls -la data/api_responses/  # API data
ls -la data/processed/      # Analysis results
```

Check crawler logs:
```bash
tail -f data/crawler.log
```

## Performance Guidelines

### Recommended Limits

- **Starter Pack**: 16 artists (~5 minutes)
- **Single Category**: 10-20 artists (~10-15 minutes)
- **Network Crawling**: 20-50 artists (~20-45 minutes)
- **Large Scale**: 100+ artists (1-3 hours)

### Memory and Storage

- **HTML files**: ~500KB - 2MB per artist
- **API responses**: ~3-10KB per artist
- **Network files**: Scales with number of connections
- **RAM usage**: ~50-200MB for analysis

## Advanced Usage

### Programmatic Access

You can use the crawler classes directly in your Python code:

```python
from src.wikipedia_crawler import WikipediaCrawler, CrawlerConfig

# Create custom crawler
config = CrawlerConfig(min_delay=0.5, save_html=True)
crawler = WikipediaCrawler(config)

# Download specific artist
result = crawler.crawl_artist("Artist Name")

# Network crawling
results = crawler.crawl_artist_network(
    seed_artists=["Seed1", "Seed2"],
    max_depth=2,
    max_artists=30
)
```

### Custom Analysis

After downloading, you can create custom analysis scripts using the raw data:

```python
from src.wikipedia_analyzer import WikipediaAnalyzer
from src.network_builder import MusicNetworkBuilder

# Custom analysis workflow
analyzer = WikipediaAnalyzer()
results = analyzer.analyze_all_samples()

# Custom network building
builder = MusicNetworkBuilder()
graph = builder.build_network_from_analysis(results)
```

## Data Ethics and Legal Notes

- **Educational Use**: This tool is designed for academic and research purposes
- **Rate Limiting**: Always respect Wikipedia's servers with appropriate delays
- **Fair Use**: Downloaded data should be used under fair use principles
- **Attribution**: Consider citing Wikipedia as your data source in research

## Getting Help

- Check the crawler logs in `data/crawler.log`
- Review session files in `data/processed/`
- Examine the API responses for debugging
- Use smaller test runs before large-scale crawling

This crawler system provides a flexible foundation for building comprehensive music networks from Wikipedia data while respecting the platform's usage guidelines.
