#!/usr/bin/env python3
"""
Test script for querying the new edge types
"""

import sys
import os
sys.path.append('src')

from network_queries import MusicNetworkQuerySystem

def test_new_edge_queries():
    """Test querying the new edge types"""
    print("🧪 TEST: TRUY VẤN CÁC LOẠI CẠNH MỚI")
    print("=" * 50)

    # Load the demo network
    query_system = MusicNetworkQuerySystem(
        network_file='data/processed/demo_new_edges.gexf',
        json_file='data/processed/demo_new_edges_network.json'
    )

    print("Đã tải mạng demo với các loại cạnh mới.")
    print()

    # Test adjacency list with new edge types
    print("1. DANH SÁCH CẠNH KỀ CỦA JOHN LENNON:")
    adj_list = query_system.get_adjacency_list("John Lennon", include_edge_data=True)
    if 'error' not in adj_list:
        print(f"   Degree: {adj_list['degree']}")
        for neighbor in adj_list['neighbors']:
            edge_info = neighbor.get('edge', {})
            print(f"   → {neighbor['name']} ({neighbor['type']}) - {edge_info.get('type', 'N/A')}")
    print()

    # Test selecting specific edge types
    print("2. CÁC CẠNH MEMBER_OF:")
    member_edges = query_system.select_edges({'edge_type': 'member_of'})
    for edge in member_edges:
        attrs = edge['edge']['attributes']
        print(f"   {edge['source']['name']} → {edge['target']['name']}")
        print(f"     Role: {attrs.get('role', 'N/A')}, Period: {attrs.get('period', 'N/A')}")
    print()

    print("3. CÁC CẠNH PRODUCED_BY:")
    producer_edges = query_system.select_edges({'edge_type': 'produced_by'})
    for edge in producer_edges:
        attrs = edge['edge']['attributes']
        print(f"   {edge['source']['name']} → {edge['target']['name']}")
        print(f"     Album: {attrs.get('album', 'N/A')}, Year: {attrs.get('year', 'N/A')}")
    print()

    print("4. CÁC CẠNH WON_AWARD:")
    award_edges = query_system.select_edges({'edge_type': 'won_award'})
    for edge in award_edges:
        attrs = edge['edge']['attributes']
        print(f"   {edge['source']['name']} → {edge['target']['name']}")
        print(f"     Year: {attrs.get('year', 'N/A')}, Work: {attrs.get('work', 'N/A')}")
    print()

    print("5. CÁC CẠNH CHARTED_ON:")
    chart_edges = query_system.select_edges({'edge_type': 'charted_on'})
    for edge in chart_edges:
        attrs = edge['edge']['attributes']
        print(f"   {edge['source']['name']} → {edge['target']['name']}")
        print(f"     Peak: #{attrs.get('peak_position', 'N/A')}, Work: {attrs.get('work', 'N/A')}")
    print()

    # Test edge ranges
    print("6. PHÂN CHIA THEO LOẠI CẠNH:")
    edge_ranges = query_system.create_edge_ranges({'by': 'edge_type'})
    for edge_type, edges in edge_ranges.items():
        print(f"   {edge_type}: {len(edges)} cạnh")
    print()

    # Test selecting edges by node type
    print("7. CẠNH TỪ ARTIST ĐẾN PRODUCER:")
    artist_producer_edges = query_system.select_edges({
        'source_type': 'artist',
        'target_type': 'producer'
    })
    for edge in artist_producer_edges:
        print(f"   {edge['source']['name']} → {edge['target']['name']}")
    print()

    # Network summary
    print("8. TÓM TẮT MẠNG:")
    summary = query_system.get_network_summary()
    print(f"   Nodes: {summary['basic_stats']['total_nodes']}")
    print(f"   Edges: {summary['basic_stats']['total_edges']}")
    print(f"   Node types: {summary['node_distribution']}")
    print(f"   Edge types: {summary['edge_distribution']}")

if __name__ == "__main__":
    test_new_edge_queries()
