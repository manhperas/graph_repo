#!/usr/bin/env python3
"""
Demo script for new edge types: member_of, produced_by, won_award, charted_on, nominated_for
"""

import sys
import os
sys.path.append('src')

from network_builder import MusicNetworkBuilder, NetworkNode, NetworkEdge
import networkx as nx
import json

def create_demo_network_with_new_edges():
    """Create a demo network with the new edge types"""

    builder = MusicNetworkBuilder()

    # Sample data for demonstration
    demo_data = {
        'The Beatles': {
            'band_memberships': [
                {'band': 'The Beatles', 'period': '1960-1970', 'role': 'lead_guitarist', 'status': 'former'}
            ],
            'producers': [
                {'producer': 'George Martin', 'album': 'Abbey Road', 'year': '1969', 'weight': 2.0}
            ],
            'awards_won': [
                {'award': 'Grammy Award for Album of the Year', 'year': '1968', 'category': 'Album of the Year', 'work': 'Sgt. Pepper\'s Lonely Hearts Club Band'},
                {'award': 'Rock and Roll Hall of Fame', 'year': '1988', 'category': 'Induction'}
            ],
            'awards_nominated': [
                {'award': 'Grammy Award for Album of the Year', 'year': '1967', 'category': 'Album of the Year', 'work': 'Revolver'}
            ],
            'charts': [
                {'chart': 'Billboard Hot 100', 'peak_position': '1', 'weeks_on_chart': '9', 'work': 'Hey Jude', 'weight': 3.0}
            ]
        },
        'John Lennon': {
            'band_memberships': [
                {'band': 'The Beatles', 'period': '1960-1970', 'role': 'rhythm_guitarist', 'status': 'former'}
            ],
            'producers': [
                {'producer': 'Phil Spector', 'album': 'Imagine', 'year': '1971', 'weight': 2.0}
            ],
            'awards_won': [
                {'award': 'Grammy Award for Song of the Year', 'year': '1972', 'category': 'Song of the Year', 'work': 'Imagine'}
            ],
            'charts': [
                {'chart': 'UK Singles Chart', 'peak_position': '1', 'weeks_on_chart': '6', 'work': 'Imagine', 'weight': 2.0}
            ]
        },
        'Paul McCartney': {
            'band_memberships': [
                {'band': 'The Beatles', 'period': '1960-1970', 'role': 'bassist', 'status': 'former'}
            ],
            'producers': [
                {'producer': 'George Martin', 'album': 'Band on the Run', 'year': '1973', 'weight': 2.0}
            ],
            'awards_won': [
                {'award': 'Grammy Award for Song of the Year', 'year': '1966', 'category': 'Song of the Year', 'work': 'Michelle'}
            ],
            'charts': [
                {'chart': 'Billboard Hot 100', 'peak_position': '1', 'weeks_on_chart': '3', 'work': 'Ebony and Ivory', 'weight': 2.0}
            ]
        }
    }

    # Create artist nodes
    for artist_name in demo_data.keys():
        artist_node = builder.create_artist_node(artist_name, {
            'artist_info': {
                'name': artist_name,
                'origin': 'Liverpool, England' if 'Beatles' in artist_name else 'Unknown',
                'genres': ['Rock', 'Pop'],
                'years_active': '1960-1970',
                'labels': ['Parlophone', 'Capitol'],
                'members': [] if 'Beatles' not in artist_name else ['John Lennon', 'Paul McCartney', 'George Harrison', 'Ringo Starr']
            }
        })
        builder.nodes[artist_node.id] = artist_node

    # Create edges for each artist
    all_edges = []

    for artist_name, data in demo_data.items():
        # Member of edges
        if 'band_memberships' in data:
            member_edges = builder.create_member_of_edges(artist_name, data['band_memberships'])
            all_edges.extend(member_edges)

        # Produced by edges
        if 'producers' in data:
            producer_edges = builder.create_produced_by_edges(artist_name, data['producers'])
            all_edges.extend(producer_edges)

        # Won award edges
        if 'awards_won' in data:
            award_edges = builder.create_award_edges(artist_name, data['awards_won'], 'won_award')
            all_edges.extend(award_edges)

        # Nominated for edges
        if 'awards_nominated' in data:
            nominated_edges = builder.create_award_edges(artist_name, data['awards_nominated'], 'nominated_for')
            all_edges.extend(nominated_edges)

        # Charted on edges
        if 'charts' in data:
            chart_edges = builder.create_chart_edges(artist_name, data['charts'])
            all_edges.extend(chart_edges)

    # Build NetworkX graph
    graph = nx.Graph()

    # Add nodes
    for node in builder.nodes.values():
        graph.add_node(node.id, **{
            'name': node.name,
            'type': node.type,
            **node.attributes
        })

    # Add edges
    for edge in all_edges:
        if edge.source in builder.nodes and edge.target in builder.nodes:
            graph.add_edge(edge.source, edge.target,
                          edge_type=edge.type,
                          weight=edge.weight,
                          **edge.attributes)

    return graph, builder.nodes, all_edges

def demo_new_edge_types():
    """Demo the new edge types"""
    print("🎵 DEMO: CÁC LOẠI CẠNH MỚI")
    print("=" * 60)

    graph, nodes, edges = create_demo_network_with_new_edges()

    print(f"Mạng demo: {len(nodes)} nodes, {len(edges)} edges")
    print()

    # Count edge types
    edge_types = {}
    for edge in edges:
        edge_type = edge.type
        edge_types[edge_type] = edge_types.get(edge_type, 0) + 1

    print("CÁC LOẠI CẠNH MỚI:")
    for edge_type, count in edge_types.items():
        print(f"  • {edge_type}: {count} cạnh")

    print()
    print("VÍ DỤ CHI TIẾT:")

    # Show member_of edges
    print("\n1. MEMBER_OF EDGES:")
    member_edges = [e for e in edges if e.type == 'member_of']
    for edge in member_edges:
        source_name = nodes[edge.source].name
        target_name = nodes[edge.target].name
        period = edge.attributes.get('period', '')
        role = edge.attributes.get('role', '')
        print(f"   {source_name} → {target_name} (period: {period}, role: {role})")

    # Show produced_by edges
    print("\n2. PRODUCED_BY EDGES:")
    producer_edges = [e for e in edges if e.type == 'produced_by']
    for edge in producer_edges:
        source_name = nodes[edge.source].name
        target_name = nodes[edge.target].name
        album = edge.attributes.get('album', '')
        year = edge.attributes.get('year', '')
        print(f"   {source_name} → {target_name} (album: {album}, year: {year})")

    # Show award edges
    print("\n3. AWARD EDGES:")
    award_edges = [e for e in edges if e.type in ['won_award', 'nominated_for']]
    for edge in award_edges:
        source_name = nodes[edge.source].name
        target_name = nodes[edge.target].name
        year = edge.attributes.get('year', '')
        work = edge.attributes.get('work', '')
        result = edge.attributes.get('result', '')
        print(f"   {source_name} → {target_name} ({result}, {year})")
        if work:
            print(f"      Work: {work}")

    # Show chart edges
    print("\n4. CHART EDGES:")
    chart_edges = [e for e in edges if e.type == 'charted_on']
    for edge in chart_edges:
        source_name = nodes[edge.source].name
        target_name = nodes[edge.target].name
        peak = edge.attributes.get('peak_position', '')
        work = edge.attributes.get('work', '')
        print(f"   {source_name} → {target_name} (peak: #{peak}, work: {work})")

    print()
    print("NODE TYPES MỚI:")
    node_types = {}
    for node in nodes.values():
        node_type = node.type
        node_types[node_type] = node_types.get(node_type, 0) + 1

    for node_type, count in node_types.items():
        print(f"  • {node_type}: {count} nodes")

    return graph, nodes, edges

def save_demo_network():
    """Save the demo network for further analysis"""
    graph, nodes, edges = create_demo_network_with_new_edges()

    # Clean node attributes for GEXF export
    clean_graph = graph.copy()
    for node_id, attrs in clean_graph.nodes(data=True):
        for key, value in attrs.items():
            if isinstance(value, list):
                attrs[key] = ', '.join(map(str, value))
            elif isinstance(value, dict):
                attrs[key] = str(value)

    # Save as GEXF
    nx.write_gexf(clean_graph, 'data/processed/demo_new_edges.gexf')

    # Save as JSON
    network_data = {
        'nodes': {node_id: {
            'name': node.name,
            'type': node.type,
            **node.attributes
        } for node_id, node in nodes.items()},
        'edges': [{
            'source': edge.source,
            'target': edge.target,
            'type': edge.type,
            'weight': edge.weight,
            **edge.attributes
        } for edge in edges]
    }

    with open('data/processed/demo_new_edges_network.json', 'w', encoding='utf-8') as f:
        json.dump(network_data, f, indent=2, ensure_ascii=False)

    print("Demo network saved to:")
    print("  - data/processed/demo_new_edges.gexf")
    print("  - data/processed/demo_new_edges_network.json")

if __name__ == "__main__":
    demo_new_edge_types()
    print()
    save_demo_network()
