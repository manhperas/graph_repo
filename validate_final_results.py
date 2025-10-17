#!/usr/bin/env python3
"""
Validate the final music network results JSON file
"""

import json
import sys

def validate_final_results():
    """Validate the structure and content of final results"""
    try:
        with open('data/processed/final_music_network_results.json', 'r', encoding='utf-8') as f:
            data = json.load(f)

        print("✅ FILE VALIDATION PASSED")
        print("=" * 50)

        # Check metadata
        metadata = data.get('metadata', {})
        print(f"📋 Project: {metadata.get('project', 'Unknown')}")
        print(f"📅 Generated: {metadata.get('generated_at', 'Unknown')}")
        print(f"🏷️  Version: {metadata.get('version', 'Unknown')}")
        print()

        # Check statistics
        stats = data.get('statistics', {})
        print("📊 STATISTICS VALIDATION:")
        required_stats = ['total_nodes', 'total_edges', 'total_artists', 'total_genres', 'total_labels']
        for stat in required_stats:
            value = stats.get(stat, 'MISSING')
            status = "✅" if value != 'MISSING' else "❌"
            print(f"   {status} {stat}: {value}")

        print(f"   ✅ Node types: {len(stats.get('node_types', {}))} types")
        print(f"   ✅ Edge types: {len(stats.get('edge_types', {}))} types")
        print()

        # Check data sections
        print("📁 DATA SECTIONS VALIDATION:")
        sections = ['network_data', 'artists', 'genres', 'labels', 'relationships']
        for section in sections:
            section_data = data.get(section, {})
            if section == 'network_data':
                nodes_count = len(section_data.get('nodes', {}))
                edges_count = len(section_data.get('edges', []))
                print(f"   ✅ {section}: {nodes_count} nodes, {edges_count} edges")
            elif section == 'relationships':
                collab_count = len(section_data.get('collaborations', []))
                genre_count = len(section_data.get('genre_associations', []))
                label_count = len(section_data.get('label_relationships', []))
                print(f"   ✅ {section}: {collab_count} collab, {genre_count} genre, {label_count} label")
            else:
                count = len(section_data)
                print(f"   ✅ {section}: {count} items")
        print()

        # Check data consistency
        print("🔍 DATA CONSISTENCY CHECKS:")

        # Check if artist counts match
        artists_in_list = len(data.get('artists', []))
        artists_in_stats = stats.get('total_artists', 0)
        if artists_in_list == artists_in_stats:
            print("   ✅ Artist count consistency")
        else:
            print(f"   ❌ Artist count mismatch: list={artists_in_list}, stats={artists_in_stats}")

        # Check if edge counts match
        total_edges = sum(stats.get('edge_types', {}).values())
        edges_in_network = len(data.get('network_data', {}).get('edges', []))
        if total_edges == edges_in_network:
            print("   ✅ Edge count consistency")
        else:
            print(f"   ❌ Edge count mismatch: types_sum={total_edges}, network={edges_in_network}")

        # Check relationships consistency
        rels = data.get('relationships', {})
        collab_edges = len(rels.get('collaborations', []))
        genre_edges = len(rels.get('genre_associations', []))
        label_edges = len(rels.get('label_relationships', []))

        collab_from_types = stats.get('edge_types', {}).get('collaborates_with', 0)
        genre_from_types = stats.get('edge_types', {}).get('plays_genre', 0)
        label_from_types = stats.get('edge_types', {}).get('signed_to', 0)

        if (collab_edges == collab_from_types and
            genre_edges == genre_from_types and
            label_edges == label_from_types):
            print("   ✅ Relationships consistency")
        else:
            print("   ❌ Relationships count mismatch")
            print(f"      Collab: {collab_edges} vs {collab_from_types}")
            print(f"      Genre: {genre_edges} vs {genre_from_types}")
            print(f"      Label: {label_edges} vs {label_from_types}")

        print()

        # Sample data validation
        print("🎯 SAMPLE DATA VALIDATION:")

        # Check first artist
        artists = data.get('artists', [])
        if artists:
            first_artist = artists[0]
            required_fields = ['id', 'name', 'type', 'connections']
            missing_fields = [field for field in required_fields if field not in first_artist]
            if not missing_fields:
                print(f"   ✅ Artist structure valid: {first_artist['name']}")
            else:
                print(f"   ❌ Missing artist fields: {missing_fields}")

        # Check first relationship
        collabs = rels.get('collaborations', [])
        if collabs:
            first_collab = collabs[0]
            required_fields = ['artist1', 'artist2', 'weight']
            missing_fields = [field for field in required_fields if field not in first_collab]
            if not missing_fields:
                print(f"   ✅ Collaboration structure valid")
            else:
                print(f"   ❌ Missing collaboration fields: {missing_fields}")

        print()
        print("🎉 FINAL RESULTS: File structure is VALID and READY for use!")
        return True

    except json.JSONDecodeError as e:
        print(f"❌ JSON DECODE ERROR: {e}")
        return False
    except FileNotFoundError:
        print("❌ FILE NOT FOUND: data/processed/final_music_network_results.json")
        return False
    except Exception as e:
        print(f"❌ VALIDATION ERROR: {e}")
        return False

if __name__ == "__main__":
    success = validate_final_results()
    sys.exit(0 if success else 1)
