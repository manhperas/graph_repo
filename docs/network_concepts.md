# Music Network Concepts and Design

## Overview
This document defines the concepts, data model, and relationships for building a network of US-UK musicians and singers using Wikipedia data.

## Network Components

### 1. NODES (Vertices)

#### Primary Node Types

**Artist Nodes**
- **Definition**: Individual musicians, singers, or musical groups
- **Sources**: Wikipedia artist pages (bands, solo artists, groups)
- **Unique Identifier**: Normalized Wikipedia page title
- **Attributes**:
  - `name`: Official artist name
  - `type`: "solo_artist" | "band" | "group"
  - `origin`: Geographic origin (city, country)
  - `genres`: List of musical genres
  - `years_active`: Period of activity
  - `instruments`: Instruments played (for solo artists)
  - `labels`: Record labels
  - `website`: Official website

**Album Nodes**
- **Definition**: Music albums, EPs, compilations
- **Sources**: Wikipedia album pages, discography sections
- **Attributes**:
  - `title`: Album title
  - `artist`: Primary artist(s)
  - `release_date`: Release date
  - `genres`: Musical genres
  - `label`: Record label
  - `chart_positions`: Peak chart positions

**Song Nodes**
- **Definition**: Individual songs/tracks
- **Sources**: Wikipedia song pages, track listings
- **Attributes**:
  - `title`: Song title
  - `artist`: Performing artist(s)
  - `writers`: Songwriters/composers
  - `album`: Parent album (if applicable)
  - `release_date`: Release date
  - `chart_positions`: Peak chart positions

#### Node Classification Rules

**Finding Nodes**:
1. **Artist Pages**: Wikipedia pages with infoboxes containing:
   - Musical genres
   - Years active
   - Record labels
   - Origin information
2. **Album Pages**: Pages with album infoboxes containing:
   - Artist information
   - Release dates
   - Track listings
3. **Song Pages**: Pages identified by:
   - Song infoboxes
   - References to performing artists
   - Chart position data

**Node Classification**:
- **Solo Artist**: Individual person with musical occupation
- **Band**: Group with multiple members (current/past)
- **Album**: Released collection of songs
- **Song**: Individual musical composition

### 2. EDGES (Relationships)

#### Edge Types and Definitions

**Collaboration Edges**
- **artist_collaborates_with_artist**: Direct musical collaboration
  - Sources: "Associated acts", featured performances, joint albums
  - Weight: Number of collaborations
  - Attributes: `collaboration_type`, `years`, `songs/albums`

**Membership Edges**
- **artist_member_of_band**: Current or past band membership
  - Sources: Band member lists, "Past members" sections
  - Attributes: `period`, `role`, `status` (current/former)

**Musical Influence Edges**
- **artist_influences_artist**: Musical influence relationship
  - Sources: "Influences" sections, biographical text analysis
  - Weight: Strength of influence (if quantifiable)

**Production Edges**
- **artist_performs_song**: Artist performs a song
- **artist_releases_album**: Artist releases an album
- **song_appears_on_album**: Song is part of an album

**Label Relationships**
- **artist_signed_to_label**: Record label relationships
  - Sources: Infobox "labels" field
  - Attributes: `period`, `status` (current/former)

**Genre Connections**
- **artist_plays_genre**: Artist associated with musical genre
  - Sources: Infobox "genres" field
  - Weight: Primary vs secondary genre association

#### Edge Discovery Methods

1. **Infobox Parsing**:
   - Extract "Associated acts" lists
   - Parse "Members" and "Past members"
   - Identify record labels
   - Extract genre associations

2. **Link Analysis**:
   - Internal Wikipedia links to other artist pages
   - Links in discography sections
   - Cross-references in song/album pages

3. **Text Mining**:
   - Biographical sections mentioning other artists
   - Collaboration descriptions
   - Influence statements

#### Edge Classification Rules

**Strong Connections** (High confidence):
- Direct mentions in infoboxes
- Documented collaborations with specific songs/albums
- Confirmed band memberships

**Weak Connections** (Lower confidence):
- General mentions in biographical text
- Shared genre classifications
- Indirect associations through other artists

### 3. NETWORK QUERIES AND ANALYSIS

#### Query Types

**Node-Centric Queries**:
```python
# Find all collaborators of an artist
get_collaborators(artist_name) -> List[Artist]

# Get artist's discography
get_discography(artist_name) -> List[Album, Song]

# Find artists by genre
get_artists_by_genre(genre_name) -> List[Artist]

# Get artist's influence network
get_influence_network(artist_name, depth=2) -> NetworkGraph
```

**Network Analysis Queries**:
```python
# Find shortest path between two artists
get_connection_path(artist1, artist2) -> List[Connection]

# Identify influential artists (high centrality)
get_most_influential_artists(metric="betweenness") -> List[Artist]

# Find communities/clusters of related artists
detect_music_communities() -> List[Community]

# Analyze genre evolution over time
analyze_genre_evolution(genre, time_period) -> Timeline
```

**Relationship Queries**:
```python
# Find common collaborators between artists
get_common_collaborators(artist1, artist2) -> List[Artist]

# Get all artists from same origin
get_artists_by_origin(location) -> List[Artist]

# Find cross-genre collaborations
get_cross_genre_collaborations() -> List[Collaboration]
```

## Data Model Structure

```python
class MusicNetwork:
    nodes: Dict[str, Node]  # node_id -> Node
    edges: List[Edge]       # All relationships
    indexes: Dict[str, Any] # Search indexes
    
class Node:
    id: str
    type: NodeType
    attributes: Dict[str, Any]
    
class Edge:
    source_id: str
    target_id: str
    type: EdgeType
    weight: float
    attributes: Dict[str, Any]
```

## Implementation Priorities

### Phase 1: Data Collection
1. ✅ **Sample Data Analysis**: Analyze Wikipedia structure (COMPLETED)
2. **Infobox Extraction**: Parse structured data from Wikipedia pages
3. **Link Discovery**: Extract internal Wikipedia links and relationships

### Phase 2: Network Construction
1. **Node Creation**: Build artist, album, and song nodes
2. **Edge Detection**: Identify and classify relationships
3. **Data Validation**: Clean and verify extracted relationships

### Phase 3: Analysis Tools
1. **Query Interface**: Implement network query functions
2. **Visualization**: Create network visualization tools
3. **Analytics**: Implement centrality and community detection

## Quality Metrics

**Data Quality**:
- Node completeness (% of attributes filled)
- Edge accuracy (manual verification sample)
- Network connectivity (giant component size)

**Network Properties**:
- Average path length between artists
- Clustering coefficient
- Degree distribution
- Community modularity

This framework provides a comprehensive approach to building and analyzing the music network using Wikipedia data as the primary source.
