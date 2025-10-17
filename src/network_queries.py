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

    def get_adjacency_list(self, node_id: str, include_edge_data: bool = False) -> Dict[str, Any]:
        """Get adjacency list for a node with optional edge information"""
        if node_id not in self.graph:
            return {'error': f'Node {node_id} not found in network'}

        neighbors = list(self.graph.neighbors(node_id))
        adjacency_list = {
            'node': node_id,
            'degree': len(neighbors),
            'neighbors': []
        }

        for neighbor in neighbors:
            neighbor_info = {
                'id': neighbor,
                'name': self.graph.nodes[neighbor].get('name', neighbor),
                'type': self.graph.nodes[neighbor].get('type', 'unknown')
            }

            if include_edge_data:
                edge_data = self.graph[node_id][neighbor]
                neighbor_info['edge'] = {
                    'type': edge_data.get('edge_type', 'unknown'),
                    'weight': edge_data.get('weight', 1.0),
                    'attributes': {k: v for k, v in edge_data.items()
                                 if k not in ['edge_type', 'weight']}
                }

            adjacency_list['neighbors'].append(neighbor_info)

        # Sort neighbors by edge weight (if available)
        if include_edge_data:
            adjacency_list['neighbors'].sort(key=lambda x: x['edge']['weight'], reverse=True)

        return adjacency_list

    def select_edges(self, criteria: Dict[str, Any] = None, limit: int = None) -> List[Dict[str, Any]]:
        """Select edges based on criteria (edge_type, weight, source/target types, etc.)"""
        if criteria is None:
            criteria = {}

        selected_edges = []

        for source, target, edge_data in self.graph.edges(data=True):
            # Check criteria
            match = True

            # Filter by edge type
            if 'edge_type' in criteria:
                if edge_data.get('edge_type') != criteria['edge_type']:
                    match = False

            # Filter by minimum weight
            if 'min_weight' in criteria:
                if edge_data.get('weight', 1.0) < criteria['min_weight']:
                    match = False

            # Filter by maximum weight
            if 'max_weight' in criteria:
                if edge_data.get('weight', 1.0) > criteria['max_weight']:
                    match = False

            # Filter by source node type
            if 'source_type' in criteria:
                source_type = self.graph.nodes[source].get('type', 'unknown')
                if source_type != criteria['source_type']:
                    match = False

            # Filter by target node type
            if 'target_type' in criteria:
                target_type = self.graph.nodes[target].get('type', 'unknown')
                if target_type != criteria['target_type']:
                    match = False

            # Filter by source node name pattern
            if 'source_name_contains' in criteria:
                source_name = self.graph.nodes[source].get('name', source)
                if criteria['source_name_contains'].lower() not in source_name.lower():
                    match = False

            # Filter by target node name pattern
            if 'target_name_contains' in criteria:
                target_name = self.graph.nodes[target].get('name', target)
                if criteria['target_name_contains'].lower() not in target_name.lower():
                    match = False

            if match:
                edge_info = {
                    'source': {
                        'id': source,
                        'name': self.graph.nodes[source].get('name', source),
                        'type': self.graph.nodes[source].get('type', 'unknown')
                    },
                    'target': {
                        'id': target,
                        'name': self.graph.nodes[target].get('name', target),
                        'type': self.graph.nodes[target].get('type', 'unknown')
                    },
                    'edge': {
                        'type': edge_data.get('edge_type', 'unknown'),
                        'weight': edge_data.get('weight', 1.0),
                        'attributes': {k: v for k, v in edge_data.items()
                                     if k not in ['edge_type', 'weight']}
                    }
                }
                selected_edges.append(edge_info)

        # Sort by weight (highest first)
        selected_edges.sort(key=lambda x: x['edge']['weight'], reverse=True)

        # Apply limit if specified
        if limit:
            selected_edges = selected_edges[:limit]

        return selected_edges

    def create_edge_ranges(self, range_criteria: Dict[str, Any] = None) -> Dict[str, List[Dict[str, Any]]]:
        """Create ranges of edges based on criteria (weight ranges, type groups, etc.)"""
        if range_criteria is None:
            range_criteria = {'by': 'weight', 'bins': 5}

        all_edges = []
        for source, target, edge_data in self.graph.edges(data=True):
            all_edges.append({
                'source': source,
                'target': target,
                'source_name': self.graph.nodes[source].get('name', source),
                'target_name': self.graph.nodes[target].get('name', target),
                'edge_type': edge_data.get('edge_type', 'unknown'),
                'weight': edge_data.get('weight', 1.0),
                'attributes': edge_data
            })

        if range_criteria.get('by') == 'weight':
            # Create weight ranges
            weights = [edge['weight'] for edge in all_edges]
            if not weights:
                return {'error': 'No edges found'}

            min_weight = min(weights)
            max_weight = max(weights)
            bins = range_criteria.get('bins', 5)

            if max_weight == min_weight:
                # All weights are the same
                return {
                    f'weight_range_{min_weight}': all_edges
                }

            # Create bins
            bin_size = (max_weight - min_weight) / bins
            ranges = {}

            for i in range(bins):
                range_min = min_weight + (i * bin_size)
                range_max = min_weight + ((i + 1) * bin_size)

                if i == bins - 1:  # Last bin includes max
                    range_max = max_weight + 0.001  # Small epsilon for floating point

                range_name = ".2f"
                range_edges = [edge for edge in all_edges
                             if range_min <= edge['weight'] < range_max]

                ranges[range_name] = range_edges

            return ranges

        elif range_criteria.get('by') == 'edge_type':
            # Group by edge type
            type_ranges = {}
            for edge in all_edges:
                edge_type = edge['edge_type']
                if edge_type not in type_ranges:
                    type_ranges[edge_type] = []
                type_ranges[edge_type].append(edge)

            return type_ranges

        elif range_criteria.get('by') == 'node_type':
            # Group by source or target node type
            type_ranges = {}
            node_type_key = range_criteria.get('node_position', 'source')  # 'source' or 'target'

            for edge in all_edges:
                node_id = edge[node_type_key]
                node_type = self.graph.nodes[node_id].get('type', 'unknown')

                if node_type not in type_ranges:
                    type_ranges[node_type] = []
                type_ranges[node_type].append(edge)

            return type_ranges

        else:
            return {'error': f'Unsupported range criteria: {range_criteria.get("by")}'}

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

    # New: Adjacency List Demo
    print("\n7. ADJACENCY LIST:")
    adj_list = query_system.get_adjacency_list("The Beatles", include_edge_data=True)
    if 'error' not in adj_list:
        print(f"  {adj_list['node']} has {adj_list['degree']} connections:")
        for i, neighbor in enumerate(adj_list['neighbors'][:5], 1):
            edge_info = neighbor.get('edge', {})
            weight = edge_info.get('weight', 'N/A')
            edge_type = edge_info.get('type', 'N/A')
            print(f"    {i}. {neighbor['name']} ({neighbor['type']}) - {edge_type} (w={weight})")

    # New: Edge Selection Demo
    print("\n8. EDGE SELECTION:")
    collab_edges = query_system.select_edges({'edge_type': 'collaborates_with'}, limit=5)
    print(f"  Top 5 collaboration edges:")
    for i, edge in enumerate(collab_edges, 1):
        print(f"    {i}. {edge['source']['name']} ↔ {edge['target']['name']} (w={edge['edge']['weight']})")

    strong_edges = query_system.select_edges({'min_weight': 2.0}, limit=3)
    print(f"  Top 3 strong edges (weight >= 2.0):")
    for i, edge in enumerate(strong_edges, 1):
        print(f"    {i}. {edge['source']['name']} → {edge['target']['name']} ({edge['edge']['type']}, w={edge['edge']['weight']})")

    # New: Edge Ranges Demo
    print("\n9. EDGE RANGES:")
    weight_ranges = query_system.create_edge_ranges({'by': 'weight', 'bins': 3})
    print(f"  Weight ranges:")
    for range_name, edges in weight_ranges.items():
        print(f"    {range_name}: {len(edges)} edges")

    edge_type_ranges = query_system.create_edge_ranges({'by': 'edge_type'})
    print(f"  Edge type groups:")
    for edge_type, edges in edge_type_ranges.items():
        print(f"    {edge_type}: {len(edges)} edges")

if __name__ == "__main__":
    main()
