#!/usr/bin/env python3
"""
Demo script for Adjacency List, Edge Selection, and Edge Ranges functionality
"""

import sys
import os
sys.path.append('src')

from network_queries import MusicNetworkQuerySystem

def demo_adjacency_list():
    """Demo adjacency list functionality"""
    print("=== DANH SÁCH CẠNH KỀ (ADJACENCY LIST) ===")

    query_system = MusicNetworkQuerySystem(
        network_file='data/processed/music_network.gexf',
        json_file='data/processed/music_network_network.json'
    )

    # Test with The Beatles
    print("\n1. Danh sách cạnh kề của The Beatles:")
    adj_list = query_system.get_adjacency_list("The Beatles", include_edge_data=True)
    if 'error' not in adj_list:
        print(f"   Node: {adj_list['node']}")
        print(f"   Degree: {adj_list['degree']} connections")
        print("   Top 5 neighbors (sorted by edge weight):")

        for i, neighbor in enumerate(adj_list['neighbors'][:5], 1):
            edge_info = neighbor.get('edge', {})
            print(f"   {i}. {neighbor['name']} ({neighbor['type']})")
            print(f"      Edge: {edge_info.get('type', 'N/A')} (weight: {edge_info.get('weight', 'N/A')})")
    else:
        print(f"   Error: {adj_list['error']}")

    # Test with a genre node
    print("\n2. Danh sách cạnh kề của thể loại 'Rock':")
    rock_adj = query_system.get_adjacency_list("genre_Rock", include_edge_data=True)
    if 'error' not in rock_adj:
        print(f"   Node: {rock_adj['node']}")
        print(f"   Degree: {rock_adj['degree']} connections")
        print("   Sample artists connected to Rock:")
        for i, neighbor in enumerate(rock_adj['neighbors'][:3], 1):
            print(f"   {i}. {neighbor['name']} ({neighbor['type']})")
    else:
        print(f"   Error: {rock_adj['error']}")

def demo_edge_selection():
    """Demo edge selection functionality"""
    print("\n=== LỰA CHỌN CẠNH (EDGE SELECTION) ===")

    query_system = MusicNetworkQuerySystem(
        network_file='data/processed/music_network.gexf',
        json_file='data/processed/music_network_network.json'
    )

    # Select collaboration edges
    print("\n1. Top 5 cạnh hợp tác (collaborates_with):")
    collab_edges = query_system.select_edges({'edge_type': 'collaborates_with'}, limit=5)
    for i, edge in enumerate(collab_edges, 1):
        print(f"   {i}. {edge['source']['name']} ↔ {edge['target']['name']}")
        print(f"      Weight: {edge['edge']['weight']}")

    # Select strong edges (high weight)
    print("\n2. Top 5 cạnh mạnh (weight >= 2.0):")
    strong_edges = query_system.select_edges({'min_weight': 2.0}, limit=5)
    for i, edge in enumerate(strong_edges, 1):
        print(f"   {i}. {edge['source']['name']} → {edge['target']['name']}")
        print(f"      Type: {edge['edge']['type']}, Weight: {edge['edge']['weight']}")

    # Select edges by source type
    print("\n3. Top 3 cạnh từ artist đến genre:")
    artist_genre_edges = query_system.select_edges({
        'source_type': 'artist',
        'target_type': 'genre'
    }, limit=3)
    for i, edge in enumerate(artist_genre_edges, 1):
        print(f"   {i}. {edge['source']['name']} → {edge['target']['name']}")
        print(f"      Weight: {edge['edge']['weight']}")

    # Select edges by name pattern
    print("\n4. Cạnh liên quan đến 'Coldplay':")
    coldplay_edges = query_system.select_edges({
        'source_name_contains': 'Coldplay'
    }, limit=3)
    for i, edge in enumerate(coldplay_edges, 1):
        print(f"   {i}. {edge['source']['name']} → {edge['target']['name']}")
        print(f"      Type: {edge['edge']['type']}, Weight: {edge['edge']['weight']}")

def demo_edge_ranges():
    """Demo edge ranges functionality"""
    print("\n=== TẠO RANGE CẠNH (EDGE RANGES) ===")

    query_system = MusicNetworkQuerySystem(
        network_file='data/processed/music_network.gexf',
        json_file='data/processed/music_network_network.json'
    )

    # Create weight ranges
    print("\n1. Phân chia cạnh theo trọng số (3 bins):")
    weight_ranges = query_system.create_edge_ranges({'by': 'weight', 'bins': 3})
    if 'error' not in weight_ranges:
        for range_name, edges in weight_ranges.items():
            print(f"   {range_name}: {len(edges)} cạnh")
            if len(edges) > 0:
                sample_edge = edges[0]
                print(f"      Ví dụ: {sample_edge['source_name']} → {sample_edge['target_name']} (w={sample_edge['weight']})")
    else:
        print(f"   Error: {weight_ranges['error']}")

    # Create edge type ranges
    print("\n2. Nhóm cạnh theo loại:")
    type_ranges = query_system.create_edge_ranges({'by': 'edge_type'})
    if 'error' not in type_ranges:
        for edge_type, edges in type_ranges.items():
            print(f"   {edge_type}: {len(edges)} cạnh")
    else:
        print(f"   Error: {type_ranges['error']}")

    # Create node type ranges (by source)
    print("\n3. Nhóm cạnh theo loại node nguồn:")
    source_type_ranges = query_system.create_edge_ranges({
        'by': 'node_type',
        'node_position': 'source'
    })
    if 'error' not in source_type_ranges:
        for node_type, edges in source_type_ranges.items():
            print(f"   Source {node_type}: {len(edges)} cạnh")
    else:
        print(f"   Error: {source_type_ranges['error']}")

def main():
    """Main demo function"""
    print("🎵 DEMO: DANH SÁCH CẠNH KỀ, LỰA CHỌN CẠNH & TẠO RANGE CẠNH")
    print("=" * 70)

    try:
        demo_adjacency_list()
        demo_edge_selection()
        demo_edge_ranges()

        print("\n" + "=" * 70)
        print("✅ Demo hoàn thành! Các tính năng đã sẵn sàng sử dụng.")
        print("\n📖 Cách sử dụng trong code:")
        print("   from network_queries import MusicNetworkQuerySystem")
        print("   query_system = MusicNetworkQuerySystem(...)")
        print("   adj_list = query_system.get_adjacency_list(node_id)")
        print("   edges = query_system.select_edges(criteria)")
        print("   ranges = query_system.create_edge_ranges(criteria)")

    except Exception as e:
        print(f"\n❌ Lỗi: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
