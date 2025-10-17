#!/usr/bin/env python3
"""
Music Network Builder
Constructs a network graph from Wikipedia artist data.
"""

import json
import networkx as nx
from typing import Dict, List, Any, Tuple, Optional, Set
from dataclasses import dataclass
from pathlib import Path
import re
from collections import defaultdict

@dataclass
class NetworkNode:
    """Represents a node in the music network"""
    id: str
    type: str  # 'artist', 'album', 'song', 'label', 'genre'
    name: str
    attributes: Dict[str, Any]

@dataclass
class NetworkEdge:
    """Represents an edge in the music network"""
    source: str
    target: str
    type: str  # 'collaborates_with', 'member_of', 'signed_to', 'plays_genre', etc.
    weight: float = 1.0
    attributes: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.attributes is None:
            self.attributes = {}

class MusicNetworkBuilder:
    """Builds a network graph from Wikipedia music data"""
    
    def __init__(self):
        self.graph = nx.Graph()
        self.nodes = {}  # node_id -> NetworkNode
        self.edges = []  # List of NetworkEdge
        self.artist_aliases = defaultdict(set)  # Handle different name variations
        
    def load_analysis_data(self, filepath: str) -> Dict[str, Any]:
        """Load analysis results from JSON file"""
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def normalize_name(self, name: str) -> str:
        """Normalize artist/entity names for consistent identification"""
        if not name:
            return ""
        
        # Remove common Wikipedia suffixes
        name = re.sub(r'\s*\(.*?\)$', '', name)  # Remove (band), (singer), etc.
        
        # Clean up common variations
        name = name.strip()
        name = re.sub(r'\s+', ' ', name)  # Normalize whitespace
        
        return name
    
    def create_artist_node(self, artist_name: str, artist_data: Dict[str, Any]) -> NetworkNode:
        """Create an artist node from Wikipedia data"""
        info = artist_data['artist_info']
        
        # Determine artist type
        artist_type = 'band' if info.get('members') or info.get('past_members') else 'solo_artist'
        
        # Create node attributes
        attributes = {
            'origin': info.get('origin', ''),
            'genres': info.get('genres', []),
            'years_active': info.get('years_active', ''),
            'labels': info.get('labels', []),
            'instruments': info.get('instruments', []),
            'website': info.get('website', ''),
            'type': artist_type
        }
        
        # Additional attributes for bands
        if artist_type == 'band':
            attributes['members'] = info.get('members', [])
            attributes['past_members'] = info.get('past_members', [])
        
        node_id = self.normalize_name(artist_name)
        return NetworkNode(
            id=node_id,
            type='artist',
            name=artist_name,
            attributes=attributes
        )
    
    def create_genre_nodes(self, genres: List[str]) -> List[NetworkNode]:
        """Create genre nodes"""
        genre_nodes = []
        for genre in genres:
            if genre:
                normalized_genre = self.normalize_name(genre)
                genre_nodes.append(NetworkNode(
                    id=f"genre_{normalized_genre}",
                    type='genre',
                    name=genre,
                    attributes={'category': 'musical_genre'}
                ))
        return genre_nodes
    
    def create_label_nodes(self, labels: List[str]) -> List[NetworkNode]:
        """Create record label nodes"""
        label_nodes = []
        for label in labels:
            if label:
                normalized_label = self.normalize_name(label)
                label_nodes.append(NetworkNode(
                    id=f"label_{normalized_label}",
                    type='label',
                    name=label,
                    attributes={'category': 'record_label'}
                ))
        return label_nodes
    
    def extract_collaborations_from_links(self, artist_name: str, music_links: List[str]) -> List[str]:
        """Extract potential collaborations from music-related links"""
        collaborators = []
        
        # Common patterns that indicate other artists
        artist_patterns = [
            r'(.+?)\s*\((band|singer|musician|artist|group)\)',
            r'(.+?)\s*(band|duo|trio|quartet)',
            r'(.+?)\s*discography',
            r'List of (.+?) songs'
        ]
        
        for link in music_links:
            for pattern in artist_patterns:
                match = re.match(pattern, link, re.IGNORECASE)
                if match:
                    potential_artist = match.group(1).strip()
                    # Avoid self-references and common false positives
                    if (potential_artist.lower() != artist_name.lower() 
                        and len(potential_artist) > 2
                        and not potential_artist.lower().startswith('list of')
                        and not potential_artist.lower().startswith('category')):
                        collaborators.append(potential_artist)
        
        return list(set(collaborators))  # Remove duplicates
    
    def create_collaboration_edges(self, artist_name: str, collaborators: List[str]) -> List[NetworkEdge]:
        """Create collaboration edges between artists"""
        edges = []
        artist_id = self.normalize_name(artist_name)
        
        for collaborator in collaborators:
            collaborator_id = self.normalize_name(collaborator)
            
            # Create bidirectional collaboration edge
            edge = NetworkEdge(
                source=artist_id,
                target=collaborator_id,
                type='collaborates_with',
                weight=1.0,
                attributes={'detected_from': 'wikipedia_links'}
            )
            edges.append(edge)
        
        return edges
    
    def create_genre_edges(self, artist_name: str, genres: List[str]) -> List[NetworkEdge]:
        """Create edges between artists and genres"""
        edges = []
        artist_id = self.normalize_name(artist_name)
        
        for i, genre in enumerate(genres):
            if genre:
                genre_id = f"genre_{self.normalize_name(genre)}"
                
                # Primary genre gets higher weight
                weight = 2.0 if i == 0 else 1.0
                
                edge = NetworkEdge(
                    source=artist_id,
                    target=genre_id,
                    type='plays_genre',
                    weight=weight,
                    attributes={'genre_priority': i + 1}
                )
                edges.append(edge)
        
        return edges
    
    def create_label_edges(self, artist_name: str, labels: List[str]) -> List[NetworkEdge]:
        """Create edges between artists and record labels"""
        edges = []
        artist_id = self.normalize_name(artist_name)
        
        for label in labels:
            if label:
                label_id = f"label_{self.normalize_name(label)}"
                
                edge = NetworkEdge(
                    source=artist_id,
                    target=label_id,
                    type='signed_to',
                    weight=1.0,
                    attributes={'relationship': 'record_label'}
                )
                edges.append(edge)
        
        return edges
    
    def build_network_from_analysis(self, analysis_data: Dict[str, Any]) -> nx.Graph:
        """Build the complete network from analysis data"""
        all_nodes = {}
        all_edges = []
        
        # Process each artist
        for artist_name, data in analysis_data.items():
            if 'error' in data:
                print(f"Skipping {artist_name}: {data['error']}")
                continue
            
            print(f"Processing {artist_name}...")
            
            # Create artist node
            artist_node = self.create_artist_node(artist_name, data)
            all_nodes[artist_node.id] = artist_node
            
            # Create genre nodes and edges
            genres = data['artist_info'].get('genres', [])
            if genres:
                genre_nodes = self.create_genre_nodes(genres)
                for genre_node in genre_nodes:
                    all_nodes[genre_node.id] = genre_node
                
                genre_edges = self.create_genre_edges(artist_name, genres)
                all_edges.extend(genre_edges)
            
            # Create label nodes and edges
            labels = data['artist_info'].get('labels', [])
            if labels:
                label_nodes = self.create_label_nodes(labels)
                for label_node in label_nodes:
                    all_nodes[label_node.id] = label_node
                
                label_edges = self.create_label_edges(artist_name, labels)
                all_edges.extend(label_edges)
            
            # Extract collaborations from Wikipedia links
            music_links = data.get('music_related_links', [])
            collaborators = self.extract_collaborations_from_links(artist_name, music_links)
            
            if collaborators:
                # Create placeholder nodes for collaborators (to be filled in later if we get their data)
                for collaborator in collaborators:
                    collab_id = self.normalize_name(collaborator)
                    if collab_id not in all_nodes:
                        all_nodes[collab_id] = NetworkNode(
                            id=collab_id,
                            type='artist',
                            name=collaborator,
                            attributes={'placeholder': True}
                        )
                
                collab_edges = self.create_collaboration_edges(artist_name, collaborators)
                all_edges.extend(collab_edges)
        
        # Build NetworkX graph
        graph = nx.Graph()
        
        # Add nodes
        for node in all_nodes.values():
            graph.add_node(node.id, **{
                'name': node.name,
                'type': node.type,
                **node.attributes
            })
        
        # Add edges
        for edge in all_edges:
            if edge.source in all_nodes and edge.target in all_nodes:
                graph.add_edge(edge.source, edge.target, 
                              edge_type=edge.type, 
                              weight=edge.weight,
                              **edge.attributes)
        
        self.graph = graph
        return graph
    
    def get_network_statistics(self) -> Dict[str, Any]:
        """Get basic statistics about the network"""
        if not self.graph:
            return {}
        
        # Node statistics by type
        node_types = defaultdict(int)
        for node_id, attrs in self.graph.nodes(data=True):
            node_types[attrs.get('type', 'unknown')] += 1
        
        # Edge statistics by type
        edge_types = defaultdict(int)
        for _, _, attrs in self.graph.edges(data=True):
            edge_types[attrs.get('edge_type', 'unknown')] += 1
        
        # Network metrics
        stats = {
            'total_nodes': self.graph.number_of_nodes(),
            'total_edges': self.graph.number_of_edges(),
            'node_types': dict(node_types),
            'edge_types': dict(edge_types),
            'density': nx.density(self.graph),
            'connected_components': nx.number_connected_components(self.graph)
        }
        
        if self.graph.number_of_nodes() > 0:
            # Only calculate these if we have nodes
            largest_component = max(nx.connected_components(self.graph), key=len)
            stats['largest_component_size'] = len(largest_component)
            
            if len(largest_component) > 1:
                subgraph = self.graph.subgraph(largest_component)
                stats['average_path_length'] = nx.average_shortest_path_length(subgraph)
                stats['clustering_coefficient'] = nx.average_clustering(subgraph)
        
        return stats
    
    def save_network(self, filepath: str):
        """Save the network to a file"""
        try:
            # Clean node attributes to avoid GEXF export issues
            clean_graph = self.graph.copy()
            for node_id, attrs in clean_graph.nodes(data=True):
                # Convert lists to strings for GEXF compatibility
                for key, value in attrs.items():
                    if isinstance(value, list):
                        attrs[key] = ', '.join(map(str, value))
                    elif isinstance(value, dict):
                        attrs[key] = str(value)
            
            nx.write_gexf(clean_graph, filepath)
            print(f"Network saved to {filepath}")
        except Exception as e:
            print(f"Error saving GEXF format: {e}")
            # Save as GraphML instead
            graphml_path = filepath.replace('.gexf', '.graphml')
            nx.write_graphml(clean_graph, graphml_path)
            print(f"Network saved as GraphML to {graphml_path}")
            
        # Also save as JSON for easy inspection
        json_path = filepath.replace('.gexf', '_network.json')
        self.save_network_as_json(json_path)
    
    def save_network_as_json(self, filepath: str):
        """Save network data as JSON for inspection"""
        network_data = {
            'nodes': {},
            'edges': []
        }
        
        # Export nodes
        for node_id, attrs in self.graph.nodes(data=True):
            network_data['nodes'][node_id] = attrs
        
        # Export edges
        for source, target, attrs in self.graph.edges(data=True):
            edge_data = {
                'source': source,
                'target': target,
                **attrs
            }
            network_data['edges'].append(edge_data)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(network_data, f, indent=2, ensure_ascii=False)
        
        print(f"Network JSON saved to {filepath}")
    
    def find_artist_connections(self, artist_name: str, max_depth: int = 2) -> Dict[str, Any]:
        """Find connections from a specific artist"""
        artist_id = self.normalize_name(artist_name)
        
        if artist_id not in self.graph:
            return {'error': f'Artist {artist_name} not found in network'}
        
        # Get direct neighbors
        direct_neighbors = list(self.graph.neighbors(artist_id))
        
        # Categorize connections by type
        connections = {
            'direct_collaborators': [],
            'genres': [],
            'labels': [],
            'other_connections': []
        }
        
        for neighbor in direct_neighbors:
            neighbor_data = self.graph.nodes[neighbor]
            edge_data = self.graph[artist_id][neighbor]
            
            connection_info = {
                'name': neighbor_data.get('name', neighbor),
                'type': neighbor_data.get('type', 'unknown'),
                'edge_type': edge_data.get('edge_type', 'unknown'),
                'weight': edge_data.get('weight', 1.0)
            }
            
            if neighbor_data.get('type') == 'artist':
                connections['direct_collaborators'].append(connection_info)
            elif neighbor_data.get('type') == 'genre':
                connections['genres'].append(connection_info)
            elif neighbor_data.get('type') == 'label':
                connections['labels'].append(connection_info)
            else:
                connections['other_connections'].append(connection_info)
        
        return connections

def main():
    """Main function to build and analyze the network"""
    # Load analysis data
    builder = MusicNetworkBuilder()
    
    print("Loading analysis data...")
    analysis_data = builder.load_analysis_data('data/processed/analysis_results.json')
    
    print("Building network...")
    graph = builder.build_network_from_analysis(analysis_data)
    
    print("Network Statistics:")
    stats = builder.get_network_statistics()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    # Save network
    builder.save_network('data/processed/music_network.gexf')
    
    # Example queries
    print("\n=== EXAMPLE NETWORK QUERIES ===")
    for artist in ['The Beatles', 'Taylor Swift']:
        print(f"\nConnections for {artist}:")
        connections = builder.find_artist_connections(artist)
        if 'error' not in connections:
            print(f"  Genres: {len(connections['genres'])}")
            print(f"  Labels: {len(connections['labels'])}")
            print(f"  Collaborators: {len(connections['direct_collaborators'])}")
            
            if connections['genres']:
                print(f"  Top genres: {', '.join([g['name'] for g in connections['genres'][:3]])}")

if __name__ == "__main__":
    main()
