# Music Network Graph - US-UK Artists

A network analysis system for mapping relationships between international US-UK musicians and singers using Wikipedia data.

## Overview

This project constructs and analyzes a network of musical artists, their collaborations, genres, and record labels by extracting structured data from Wikipedia pages. The system identifies relationships through infobox data, internal links, and textual analysis to create a comprehensive music network.

## Features

- **Automated Wikipedia Crawler**: Download artist data with multiple discovery methods
  - Specific artist downloads
  - Genre-based discovery
  - Network crawling (find related artists automatically)
  - Batch downloading of popular artist collections
- **Wikipedia Data Extraction**: Automated parsing of artist Wikipedia pages
- **Network Construction**: Build graph networks with artists, genres, and labels as nodes
- **Relationship Discovery**: Identify collaborations, influences, and connections
- **Query System**: Advanced network analysis and querying capabilities
- **Multiple Export Formats**: GEXF, GraphML, and JSON network formats
- **Rate-Limited Crawling**: Respectful data collection with configurable delays

## Project Structure

```
Music_Graph/
├── data/
│   ├── raw_html/              # Downloaded Wikipedia HTML pages
│   └── processed/             # Processed network data and results
├── src/
│   ├── wikipedia_crawler.py   # Automated Wikipedia data crawler
│   ├── crawl_artists.py       # Command-line interface for specific crawling
│   ├── batch_download.py      # Batch downloader for popular artists  
│   ├── wikipedia_analyzer.py  # Wikipedia page analysis and parsing
│   ├── network_builder.py     # Network construction from parsed data
│   └── network_queries.py     # Network query and analysis system
├── docs/
│   ├── network_concepts.md    # Detailed network design documentation
│   └── crawler_usage_guide.md # Complete crawler usage guide
├── requirements.txt           # Python dependencies
└── README.md                 # This file
```

## Installation

1. Clone or download this project
2. Install required dependencies:

```bash
pip install -r requirements.txt
```

## Quick Start

### 1. Download Artist Data

You have several options for downloading Wikipedia data:

**Option A: Quick Starter Pack (Recommended for beginners)**
```bash
python src/batch_download.py
# Choose option 1 for 16 diverse popular artists
```

**Option B: Download Specific Artists**
```bash
python src/crawl_artists.py artists "Radiohead" "Arctic Monkeys" "Coldplay"
```

**Option C: Discover Artists by Genre**
```bash
python src/crawl_artists.py genre "rock" --limit 10
```

**Option D: Network Discovery (Advanced)**
```bash
python src/crawl_artists.py network "The Beatles" --depth 2 --max-artists 20
```

The project also includes pre-downloaded sample pages for demonstration:
- The Beatles, Ed Sheeran, Taylor Swift, Nirvana

📖 **For detailed crawler instructions, see [docs/crawler_usage_guide.md](docs/crawler_usage_guide.md)**

### 2. Analyze Wikipedia Structure

```bash
python src/wikipedia_analyzer.py
```

This will:
- Parse HTML structure and infoboxes
- Extract artist information (genres, labels, collaborations)
- Save analysis results to `data/processed/analysis_results.json`

### 3. Build the Network

```bash
python src/network_builder.py
```

This will:
- Construct the network graph from analyzed data
- Create nodes for artists, genres, and labels
- Identify edges for collaborations and relationships
- Save network in multiple formats:
  - `data/processed/music_network.gexf` (GEXF format)
  - `data/processed/music_network_network.json` (JSON format)

### 4. Query the Network

```bash
python src/network_queries.py
```

This demonstrates various network analysis capabilities:
- Network statistics and summaries
- Artist connection analysis
- Path finding between artists
- Genre-based queries
- Most connected artists

## Network Design

### Node Types

1. **Artist Nodes**
   - Solo artists and bands/groups
   - Attributes: origin, genres, years active, instruments, labels

2. **Genre Nodes** 
   - Musical genres (Rock, Pop, Folk, etc.)
   - Connected to artists who play that genre

3. **Label Nodes**
   - Record labels
   - Connected to artists signed to that label

### Edge Types

1. **Collaboration Edges** (`collaborates_with`)
   - Direct musical collaborations between artists
   - Discovered from Wikipedia links and mentions

2. **Genre Edges** (`plays_genre`)
   - Artist association with musical genres
   - Weighted by primary vs secondary genres

3. **Label Edges** (`signed_to`)
   - Artist relationships with record labels

## Sample Results

From our initial analysis of 4 artists:

- **Network Size**: 77 nodes, 85 edges
- **Node Distribution**: 45 artists, 13 genres, 19 labels
- **Most Connected**: The Beatles (34 connections), Nirvana (25 connections)
- **Network Density**: 0.029 (sparse, typical for real-world networks)
- **Average Path Length**: ~3.1 steps between any two connected artists

## Key Queries and Analysis

### 1. Artist Information
```python
query_system.get_artist_info("The Beatles")
# Returns: origin, type, collaborators, genres, labels
```

### 2. Find Connections
```python
query_system.find_shortest_path("The Beatles", "Taylor Swift")
# Returns: path length and intermediate connections
```

### 3. Genre Analysis
```python
query_system.get_artists_by_genre("Rock")
# Returns: all artists associated with Rock genre
```

### 4. Network Statistics
```python
query_system.get_network_summary()
# Returns: comprehensive network metrics and top artists
```

## Extending the System

### Adding More Artists

1. Download additional Wikipedia pages:
```bash
curl -s "https://en.wikipedia.org/wiki/Artist_Name" -o data/raw_html/artist_name.html
```

2. Update the artist list in `wikipedia_analyzer.py`

3. Re-run the analysis and network building process

### Custom Queries

The `MusicNetworkQuerySystem` class can be extended with additional query methods:

```python
def your_custom_query(self, parameters):
    # Use self.graph (NetworkX graph) for analysis
    # Return structured results
```

## Data Sources and Methodology

### Wikipedia Data Extraction

- **Infobox Parsing**: Structured data extraction from Wikipedia infoboxes
- **Link Analysis**: Internal Wikipedia links to identify relationships
- **Text Mining**: Biographical sections for additional connections

### Network Construction Process

1. **Node Creation**: Artists, genres, and labels from infobox data
2. **Edge Detection**: Relationships from multiple sources:
   - Direct infobox references (associated acts, labels)
   - Wikipedia link analysis
   - Genre associations
3. **Data Validation**: Cleaning and normalization of entity names
4. **Network Assembly**: NetworkX graph construction with weighted edges

## Technical Details

### Dependencies

- `beautifulsoup4`: HTML parsing and data extraction
- `networkx`: Graph construction and analysis
- `requests`: HTTP requests for data download (future use)
- `matplotlib`: Network visualization capabilities
- `pandas`: Data manipulation and analysis
- `numpy`, `scipy`: Numerical computations

### Output Formats

- **GEXF**: Standard graph exchange format (compatible with Gephi)
- **GraphML**: XML-based graph format (compatible with yEd, Cytoscape)
- **JSON**: Custom format for easy programmatic access

### Performance Considerations

- Current implementation handles hundreds of nodes efficiently
- Memory usage scales linearly with network size
- Query performance is optimized for typical network analysis tasks

## Future Enhancements

### Planned Features

1. **Automated Wikipedia API Integration**
   - Real-time data fetching
   - Automatic discovery of related artists

2. **Enhanced Relationship Detection**
   - Album and song nodes
   - Producer and songwriter relationships
   - Influence network analysis

3. **Visualization Tools**
   - Interactive network visualization
   - Genre clustering visualization
   - Timeline-based analysis

4. **Advanced Analytics**
   - Community detection algorithms
   - Centrality measures (betweenness, closeness)
   - Network evolution over time

### Potential Applications

- **Music Recommendation**: Find similar artists through network proximity
- **Genre Evolution**: Track how musical genres spread and evolve
- **Influence Analysis**: Identify key influential artists in music history
- **Collaboration Prediction**: Predict likely future collaborations

## Contributing

To contribute to this project:

1. Fork the repository
2. Add new features or improvements
3. Test with additional Wikipedia data
4. Submit pull requests with detailed descriptions

## License

This project is for educational and research purposes. Wikipedia data is used under fair use for academic analysis.

## Contact

For questions, suggestions, or collaboration opportunities, please open an issue in the project repository.

---

**Note**: This system currently uses manually downloaded Wikipedia pages as samples. For production use, consider implementing the Wikipedia API for automated data collection while respecting rate limits and terms of service.
