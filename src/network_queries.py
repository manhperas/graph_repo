#!/usr/bin/env python3
"""
Music Network Query System
Provides various query methods to analyze the music network.
"""

import json
import networkx as nx
from typing import Dict, List, Any, Tuple, Optional, Set
from collections import defaultdict, Counter
import re
from pathlib import Path

class MusicNetworkQuerySystem:
    """Query system for analyzing the music network"""
    
    def __init__(self, network_file: str = None, json_file: str = None):
        self.graph = None
        self.network_data = None
        
        if network_file and Path(network_file).exists():
            if network_file.endswith('.gexf'):
                self.graph = nx.read_gexf(network_file)
            elif network_file.endswith('.graphml'):
                self.graph = nx.read_graphml(network_file)
        
        if json_file and Path(json_file).exists():
            with open(json_file, 'r', encoding='utf-8') as f:
                self.network_data = json.load(f)
            
            # Build NetworkX graph from JSON if not loaded from file
            if self.graph is None:
                self.graph = self._build_graph_from_json()
    
    def _build_graph_from_json(self) -> nx.Graph:
        """Build NetworkX graph from JSON data"""
        graph = nx.Graph()
        
        # Add nodes
        for node_id, attrs in self.network_data['nodes'].items():
            graph.add_node(node_id, **attrs)
        
        # Add edges
        for edge in self.network_data['edges']:
            graph.add_edge(edge['source'], edge['target'], **{k: v for k, v in edge.items() if k not in ['source', 'target']})
        
        return graph
    
    def get_artist_info(self, artist_name: str) -> Dict[str, Any]:
        """Get detailed information about an artist"""
        artist_id = self._normalize_name(artist_name)
        
        if artist_id not in self.graph:
            return {'error': f'Artist {artist_name} not found in network'}
        
        node_data = self.graph.nodes[artist_id]
        
        # Get connections
        neighbors = list(self.graph.neighbors(artist_id))
        
        connections = {
            'collaborators': [],
            'genres': [],
            'labels': [],
            'other': []
        }
        
        for neighbor in neighbors:
            neighbor_data = self.graph.nodes[neighbor]
            edge_data = self.graph[artist_id][neighbor]
            
            connection_info = {
                'name': neighbor_data.get('name', neighbor),
                'id': neighbor,
                'edge_type': edge_data.get('edge_type', 'unknown'),
                'weight': edge_data.get('weight', 1.0)
            }
            
            if neighbor_data.get('type') == 'artist':
                connections['collaborators'].append(connection_info)
            elif neighbor_data.get('type') == 'genre':
                connections['genres'].append(connection_info)
            elif neighbor_data.get('type') == 'label':
                connections['labels'].append(connection_info)
            else:
                connections['other'].append(connection_info)
        
        return {
            'artist_info': node_data,
            'connections': connections,
            'total_connections': len(neighbors)
        }
    
    def find_shortest_path(self, artist1: str, artist2: str) -> Dict[str, Any]:
        """Find shortest path between two artists"""
        id1 = self._normalize_name(artist1)
        id2 = self._normalize_name(artist2)
        
        if id1 not in self.graph:
            return {'error': f'Artist {artist1} not found in network'}
        if id2 not in self.graph:
            return {'error': f'Artist {artist2} not found in network'}
        
        try:
            path = nx.shortest_path(self.graph, id1, id2)
            path_info = []
            
            for i in range(len(path)):
                node_data = self.graph.nodes[path[i]]
                path_info.append({
                    'id': path[i],
                    'name': node_data.get('name', path[i]),
                    'type': node_data.get('type', 'unknown')
                })
                
                # Add edge information
                if i < len(path) - 1:
                    edge_data = self.graph[path[i]][path[i + 1]]
                    path_info.append({
                        'connection_type': edge_data.get('edge_type', 'unknown'),
                        'weight': edge_data.get('weight', 1.0)
                    })
            
            return {
                'path_length': len(path) - 1,
                'path': path_info
            }
        except nx.NetworkXNoPath:
            return {'error': f'No path found between {artist1} and {artist2}'}
    
    def get_artists_by_genre(self, genre: str) -> List[Dict[str, Any]]:
        """Find all artists associated with a specific genre"""
        genre_id = f"genre_{self._normalize_name(genre)}"
        
        if genre_id not in self.graph:
            return []
        
        artists = []
        for neighbor in self.graph.neighbors(genre_id):
            node_data = self.graph.nodes[neighbor]
            if node_data.get('type') == 'artist' or node_data.get('type') in ['solo_artist', 'band']:
                edge_data = self.graph[genre_id][neighbor]
                
                artists.append({
                    'name': node_data.get('name', neighbor),
                    'id': neighbor,
                    'type': node_data.get('type', 'unknown'),
                    'weight': edge_data.get('weight', 1.0),
                    'origin': node_data.get('origin', ''),
                    'years_active': node_data.get('years_active', '')
                })
        
        # Sort by weight (primary genre first)
        artists.sort(key=lambda x: x['weight'], reverse=True)
        return artists
    
    def get_most_connected_artists(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Find the most connected artists in the network"""
        artist_connections = []
        
        for node_id, attrs in self.graph.nodes(data=True):
            if attrs.get('type') == 'artist' or attrs.get('type') in ['solo_artist', 'band']:
                degree = self.graph.degree(node_id)
                
                # Count different types of connections
                neighbors = list(self.graph.neighbors(node_id))
                connection_types = defaultdict(int)
                
                for neighbor in neighbors:
                    neighbor_type = self.graph.nodes[neighbor].get('type', 'unknown')
                    connection_types[neighbor_type] += 1
                
                artist_connections.append({
                    'name': attrs.get('name', node_id),
                    'id': node_id,
                    'total_connections': degree,
                    'collaborators': connection_types.get('artist', 0),
                    'genres': connection_types.get('genre', 0),
                    'labels': connection_types.get('label', 0),
                    'origin': attrs.get('origin', ''),
                    'type': attrs.get('type', 'unknown')
                })
        
        # Sort by total connections
        artist_connections.sort(key=lambda x: x['total_connections'], reverse=True)
        return artist_connections[:limit]
    
    def find_common_collaborators(self, artist1: str, artist2: str) -> List[Dict[str, Any]]:
        """Find common collaborators between two artists"""
        id1 = self._normalize_name(artist1)
        id2 = self._normalize_name(artist2)
        
        if id1 not in self.graph or id2 not in self.graph:
            return []
        
        neighbors1 = set(self.graph.neighbors(id1))
        neighbors2 = set(self.graph.neighbors(id2))
        
        common_neighbors = neighbors1.intersection(neighbors2)
        
        common_collaborators = []
        for neighbor in common_neighbors:
            node_data = self.graph.nodes[neighbor]
            if node_data.get('type') == 'artist' or node_data.get('type') in ['solo_artist', 'band']:
                common_collaborators.append({
                    'name': node_data.get('name', neighbor),
                    'id': neighbor,
                    'type': node_data.get('type', 'unknown'),
                    'origin': node_data.get('origin', '')
                })
        
        return common_collaborators
    
    def analyze_genre_network(self) -> Dict[str, Any]:
        """Analyze the genre network structure"""
        genre_stats = {}
        
        for node_id, attrs in self.graph.nodes(data=True):
            if attrs.get('type') == 'genre':
                genre_name = attrs.get('name', node_id)
                neighbors = list(self.graph.neighbors(node_id))
                
                # Count artists in this genre
                artist_count = sum(1 for n in neighbors 
                                 if self.graph.nodes[n].get('type') in ['artist', 'solo_artist', 'band'])
                
                genre_stats[genre_name] = {
                    'artist_count': artist_count,
                    'total_connections': len(neighbors)
                }
        
        # Sort by artist count
        sorted_genres = sorted(genre_stats.items(), key=lambda x: x[1]['artist_count'], reverse=True)
        
        return {
            'total_genres': len(genre_stats),
            'genre_rankings': sorted_genres,
            'top_genres': sorted_genres[:10]
        }
    
    def get_network_summary(self) -> Dict[str, Any]:
        """Get comprehensive network summary"""
        if not self.graph:
            return {'error': 'No network loaded'}
        
        # Basic statistics
        total_nodes = self.graph.number_of_nodes()
        total_edges = self.graph.number_of_edges()
        
        # Node type distribution
        node_types = defaultdict(int)
        for _, attrs in self.graph.nodes(data=True):
            node_types[attrs.get('type', 'unknown')] += 1
        
        # Edge type distribution
        edge_types = defaultdict(int)
        for _, _, attrs in self.graph.edges(data=True):
            edge_types[attrs.get('edge_type', 'unknown')] += 1
        
        # Network metrics
        density = nx.density(self.graph)
        components = nx.number_connected_components(self.graph)
        
        # Get most connected artists
        top_artists = self.get_most_connected_artists(5)
        
        # Genre analysis
        genre_analysis = self.analyze_genre_network()
        
        return {
            'basic_stats': {
                'total_nodes': total_nodes,
                'total_edges': total_edges,
                'density': density,
                'connected_components': components
            },
            'node_distribution': dict(node_types),
            'edge_distribution': dict(edge_types),
            'top_connected_artists': top_artists,
            'genre_analysis': genre_analysis
        }
    
    def _normalize_name(self, name: str) -> str:
        """Normalize artist/entity names for consistent identification"""
        if not name:
            return ""
        
        # Remove common Wikipedia suffixes
        name = re.sub(r'\s*\(.*?\)$', '', name)
        name = name.strip()
        name = re.sub(r'\s+', ' ', name)
        
        return name

def main():
    """Demo the query system"""
    print("=== MUSIC NETWORK QUERY SYSTEM DEMO ===\n")
    
    # Initialize query system
    query_system = MusicNetworkQuerySystem(
        network_file='data/processed/music_network.gexf',
        json_file='data/processed/music_network_network.json'
    )
    
    # Network summary
    print("1. NETWORK SUMMARY:")
    summary = query_system.get_network_summary()
    print(f"  Nodes: {summary['basic_stats']['total_nodes']}")
    print(f"  Edges: {summary['basic_stats']['total_edges']}")
    print(f"  Density: {summary['basic_stats']['density']:.4f}")
    print(f"  Components: {summary['basic_stats']['connected_components']}")
    
    print(f"\n  Node Types: {summary['node_distribution']}")
    print(f"  Edge Types: {summary['edge_distribution']}")
    
    # Top connected artists
    print("\n2. MOST CONNECTED ARTISTS:")
    for i, artist in enumerate(summary['top_connected_artists'][:5], 1):
        print(f"  {i}. {artist['name']} ({artist['total_connections']} connections)")
        print(f"     - Collaborators: {artist['collaborators']}, Genres: {artist['genres']}, Labels: {artist['labels']}")
    
    # Genre analysis
    print("\n3. TOP GENRES:")
    for genre, stats in summary['genre_analysis']['top_genres'][:5]:
        print(f"  {genre}: {stats['artist_count']} artists")
    
    # Example artist queries
    print("\n4. ARTIST DETAILS:")
    for artist in ['The Beatles', 'Taylor Swift']:
        info = query_system.get_artist_info(artist)
        if 'error' not in info:
            print(f"\n  {artist}:")
            print(f"    Origin: {info['artist_info'].get('origin', 'Unknown')}")
            print(f"    Type: {info['artist_info'].get('type', 'Unknown')}")
            print(f"    Collaborators: {len(info['connections']['collaborators'])}")
            print(f"    Genres: {len(info['connections']['genres'])}")
            print(f"    Labels: {len(info['connections']['labels'])}")
    
    # Path finding example
    print("\n5. CONNECTION PATHS:")
    path_result = query_system.find_shortest_path('The Beatles', 'Taylor Swift')
    if 'error' not in path_result:
        print(f"  The Beatles -> Taylor Swift: {path_result['path_length']} steps")
        path_names = [item['name'] for item in path_result['path'] if 'name' in item]
        print(f"  Path: {' -> '.join(path_names)}")
    else:
        print(f"  {path_result['error']}")
    
    # Genre-based queries
    print("\n6. ARTISTS BY GENRE:")
    rock_artists = query_system.get_artists_by_genre('Rock')
    if rock_artists:
        print(f"  Rock artists: {', '.join([a['name'] for a in rock_artists[:5]])}")
    
    pop_artists = query_system.get_artists_by_genre('Pop')
    if pop_artists:
        print(f"  Pop artists: {', '.join([a['name'] for a in pop_artists[:5]])}")

if __name__ == "__main__":
    main()
