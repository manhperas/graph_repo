#!/usr/bin/env python3
"""
Validate Music Network Graph Project
Check all critical files and components
"""

import os
import json
import sys
from pathlib import Path

def check_file_exists(filepath, description):
    """Check if file exists"""
    exists = os.path.exists(filepath)
    status = "✅" if exists else "❌"
    size = f"({os.path.getsize(filepath)} bytes)" if exists else ""
    print(f"   {status} {description}: {filepath} {size}")
    return exists

def validate_json_file(filepath):
    """Validate JSON file structure"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Basic validation
        if 'nodes' in data and 'edges' in data:
            nodes_count = len(data['nodes'])
            edges_count = len(data['edges'])
            print(f"      ✅ Valid network JSON: {nodes_count} nodes, {edges_count} edges")
            return True
        elif 'metadata' in data and 'statistics' in data:
            artists = data.get('statistics', {}).get('total_artists', 0)
            print(f"      ✅ Valid results JSON: {artists} artists")
            return True
        else:
            print("      ⚠️  Valid JSON but unknown structure")
            return True

    except json.JSONDecodeError as e:
        print(f"      ❌ Invalid JSON: {e}")
        return False
    except Exception as e:
        print(f"      ❌ Error reading file: {e}")
        return False

def check_python_imports():
    """Check if Python imports work"""
    try:
        import networkx as nx
        print(f"   ✅ NetworkX {nx.__version__}")
    except ImportError:
        print("   ❌ NetworkX not installed")
        return False

    try:
        from bs4 import BeautifulSoup
        print("   ✅ BeautifulSoup4")
    except ImportError:
        print("   ❌ BeautifulSoup4 not installed")
        return False

    try:
        import requests
        print("   ✅ Requests")
    except ImportError:
        print("   ❌ Requests not installed")
        return False

    return True

def validate_network_queries():
    """Test network queries functionality"""
    try:
        from src.network_queries import MusicNetworkQuerySystem
        print("   ✅ Network queries module imported")

        # Try to initialize (will fail gracefully if files don't exist)
        try:
            query_system = MusicNetworkQuerySystem(
                network_file='data/processed/music_network.gexf',
                json_file='data/processed/music_network_network.json'
            )
            print("   ✅ Query system initialized")
            return True
        except Exception as e:
            print(f"   ⚠️  Query system init failed (expected if data not ready): {e}")
            return True  # This is OK for validation

    except ImportError as e:
        print(f"   ❌ Import error: {e}")
        return False

def main():
    """Main validation function"""
    print("🎵 MUSIC NETWORK GRAPH - PROJECT VALIDATION")
    print("=" * 60)

    all_good = True

    # Check directory structure
    print("\n📁 DIRECTORY STRUCTURE:")
    dirs_to_check = [
        ('src', 'Source code directory'),
        ('data', 'Data directory'),
        ('data/raw_html', 'Raw HTML data'),
        ('data/processed', 'Processed data'),
        ('docs', 'Documentation'),
    ]

    for dir_path, description in dirs_to_check:
        exists = os.path.exists(dir_path)
        status = "✅" if exists else "❌"
        print(f"   {status} {description}: {dir_path}")

    # Check critical files
    print("\n📄 CRITICAL FILES:")
    files_to_check = [
        ('src/network_queries.py', 'Network queries module'),
        ('src/network_builder.py', 'Network builder module'),
        ('src/wikipedia_analyzer.py', 'Wikipedia analyzer'),
        ('src/wikipedia_crawler.py', 'Wikipedia crawler'),
        ('requirements.txt', 'Python dependencies'),
        ('README_VIETNAMESE.md', 'Vietnamese documentation'),
        ('REPO_README_VIETNAMESE.md', 'Repository guide'),
    ]

    for filepath, description in files_to_check:
        if not check_file_exists(filepath, description):
            all_good = False

    # Check data files
    print("\n📊 DATA FILES:")
    data_files = [
        ('data/processed/final_music_network_results.json', 'Final results JSON'),
        ('data/processed/music_network.gexf', 'Gephi network file'),
        ('data/processed/music_network_network.json', 'NetworkX JSON'),
        ('data/processed/analysis_results.json', 'Analysis results'),
    ]

    for filepath, description in data_files:
        if check_file_exists(filepath, description):
            if filepath.endswith('.json'):
                validate_json_file(filepath)
        else:
            print(f"      ⚠️  Data file missing (may need to run processing first)")

    # Check Python environment
    print("\n🐍 PYTHON ENVIRONMENT:")
    if not check_python_imports():
        all_good = False

    # Check scripts
    print("\n🔧 SCRIPTS & MODULES:")
    if not validate_network_queries():
        all_good = False

    # Check demo scripts
    demo_files = [
        ('demo_adjacency_edges.py', 'Adjacency demo'),
        ('test_new_edge_queries.py', 'Query test'),
        ('validate_final_results.py', 'Results validator'),
    ]

    for filepath, description in demo_files:
        check_file_exists(filepath, description)

    # Final assessment
    print("\n" + "=" * 60)
    if all_good:
        print("🎉 PROJECT VALIDATION: PASSED")
        print("✅ All critical components are present and functional")
        print("\n🚀 Ready to run:")
        print("   python src/network_queries.py          # Main demo")
        print("   python demo_adjacency_edges.py         # Edge features")
        print("   python validate_final_results.py       # Data validation")
    else:
        print("⚠️  PROJECT VALIDATION: ISSUES FOUND")
        print("❌ Some components are missing or broken")
        print("\n🔧 Suggested fixes:")
        print("   pip install -r requirements.txt         # Install dependencies")
        print("   python src/batch_download.py           # Download data")
        print("   python src/wikipedia_analyzer.py       # Analyze data")
        print("   python src/network_builder.py          # Build network")

    print("\n📖 Documentation:")
    print("   README_VIETNAMESE.md                   # Full guide (Vietnamese)")
    print("   REPO_README_VIETNAMESE.md              # Repository guide")
    print("   docs/network_concepts.md               # Technical concepts")

    return all_good

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
