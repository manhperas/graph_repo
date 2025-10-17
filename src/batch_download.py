#!/usr/bin/env python3
"""
Batch Download Script
Quick download of popular US-UK artists for music network analysis.
"""

from wikipedia_crawler import WikipediaCrawler, CrawlerConfig
import time

# Predefined lists of popular artists by category
POPULAR_ARTISTS = {
    'uk_classic_rock': [
        'The Beatles', 'Led Zeppelin', 'Queen', 'Pink Floyd', 'The Rolling Stones',
        'The Who', 'Black Sabbath', 'Deep Purple', 'Cream', 'The Kinks'
    ],
    
    'uk_modern_rock': [
        'Radiohead', 'Coldplay', 'Oasis', 'Blur', 'Arctic Monkeys',
        'Muse', 'Kasabian', 'The Smiths', 'Pulp', 'Suede'
    ],
    
    'uk_pop': [
        'Ed Sheeran', 'Adele', 'Sam Smith', 'Dua Lipa', 'Harry Styles',
        'Elton John', 'George Michael', 'Amy Winehouse', 'Robbie Williams', 'Sting'
    ],
    
    'us_classic_rock': [
        'Nirvana', 'Pearl Jam', 'Soundgarden', 'Alice in Chains', 'Red Hot Chili Peppers',
        'Guns N\' Roses', 'Metallica', 'AC/DC', 'Aerosmith', 'The Doors'
    ],
    
    'us_pop': [
        'Taylor Swift', 'Ariana Grande', 'Billie Eilish', 'The Weeknd', 'Bruno Mars',
        'Justin Timberlake', 'Beyoncé', 'Madonna', 'Michael Jackson', 'Prince'
    ],
    
    'us_hip_hop': [
        'Jay-Z', 'Kanye West', 'Eminem', 'Drake', 'Travis Scott',
        'Kendrick Lamar', 'J. Cole', 'Childish Gambino', 'Tyler, The Creator', 'Mac Miller'
    ],
    
    'alternative_indie': [
        'Vampire Weekend', 'The Strokes', 'Arcade Fire', 'Tame Impala', 'Foster the People',
        'MGMT', 'Two Door Cinema Club', 'The National', 'Interpol', 'Franz Ferdinand'
    ]
}

def show_available_categories():
    """Show all available artist categories"""
    print("Available artist categories:")
    for category, artists in POPULAR_ARTISTS.items():
        print(f"  {category}: {len(artists)} artists")
        print(f"    Sample: {', '.join(artists[:3])}...")
    print()

def download_category(category: str, crawler: WikipediaCrawler = None):
    """Download all artists from a specific category"""
    if category not in POPULAR_ARTISTS:
        print(f"Category '{category}' not found.")
        show_available_categories()
        return
    
    if crawler is None:
        config = CrawlerConfig(
            min_delay=1.0,
            max_delay=2.5,
            save_html=True,
            save_api_data=True
        )
        crawler = WikipediaCrawler(config)
    
    artists = POPULAR_ARTISTS[category]
    print(f"Downloading {len(artists)} artists from category: {category}")
    
    results = {}
    successful = 0
    
    for i, artist in enumerate(artists, 1):
        print(f"\n[{i}/{len(artists)}] Downloading: {artist}")
        
        result = crawler.crawl_artist(artist)
        results[artist] = result
        
        status = result.get('status', 'unknown')
        if status == 'success':
            successful += 1
            print(f"  ✓ Success")
        elif status == 'already_crawled':
            successful += 1
            print(f"  ✓ Already downloaded")
        else:
            print(f"  ✗ {status}")
    
    print(f"\nCategory '{category}' completed:")
    print(f"  Successful downloads: {successful}/{len(artists)}")
    
    # Save results
    session_data = {
        'batch_download': {
            'category': category,
            'artists': artists,
            'results': results,
            'successful_count': successful,
            'total_count': len(artists)
        }
    }
    
    session_file = crawler.save_crawl_session(session_data)
    print(f"  Results saved to: {session_file}")
    
    return results

def download_multiple_categories(categories: list):
    """Download artists from multiple categories"""
    config = CrawlerConfig(
        min_delay=1.5,
        max_delay=3.0,
        save_html=True,
        save_api_data=True
    )
    crawler = WikipediaCrawler(config)
    
    all_results = {}
    total_successful = 0
    total_artists = 0
    
    for category in categories:
        if category in POPULAR_ARTISTS:
            print(f"\n{'='*50}")
            print(f"DOWNLOADING CATEGORY: {category.upper()}")
            print(f"{'='*50}")
            
            results = download_category(category, crawler)
            all_results[category] = results
            
            # Count successes
            successful = len([r for r in results.values() 
                            if r.get('status') in ['success', 'already_crawled']])
            total_successful += successful
            total_artists += len(POPULAR_ARTISTS[category])
        else:
            print(f"Warning: Category '{category}' not found")
    
    print(f"\n{'='*50}")
    print("BATCH DOWNLOAD SUMMARY")
    print(f"{'='*50}")
    print(f"Categories processed: {len([c for c in categories if c in POPULAR_ARTISTS])}")
    print(f"Total artists: {total_artists}")
    print(f"Successful downloads: {total_successful}")
    print(f"Success rate: {total_successful/total_artists*100:.1f}%")
    
    # Save comprehensive results
    final_session_data = {
        'batch_download_multi': {
            'categories': categories,
            'results_by_category': all_results,
            'summary': {
                'total_artists': total_artists,
                'successful_downloads': total_successful,
                'success_rate': total_successful/total_artists if total_artists > 0 else 0
            }
        }
    }
    
    session_file = crawler.save_crawl_session(final_session_data)
    print(f"Final results saved to: {session_file}")
    
    return all_results

def quick_starter_pack():
    """Download a curated starter pack of diverse artists"""
    starter_artists = [
        # UK Classic
        'The Beatles', 'Queen', 'Led Zeppelin',
        # UK Modern
        'Radiohead', 'Coldplay', 'Arctic Monkeys',
        # UK Pop
        'Ed Sheeran', 'Adele',
        # US Rock
        'Nirvana', 'Pearl Jam',
        # US Pop
        'Taylor Swift', 'Bruno Mars',
        # US Hip-Hop
        'Kanye West', 'Drake',
        # Alternative
        'The Strokes', 'Vampire Weekend'
    ]
    
    config = CrawlerConfig(
        min_delay=1.0,
        max_delay=2.0,
        save_html=True,
        save_api_data=True
    )
    crawler = WikipediaCrawler(config)
    
    print("Downloading Music Network Starter Pack...")
    print(f"Artists included: {len(starter_artists)}")
    
    results = {}
    successful = 0
    
    for i, artist in enumerate(starter_artists, 1):
        print(f"\n[{i}/{len(starter_artists)}] Downloading: {artist}")
        
        result = crawler.crawl_artist(artist)
        results[artist] = result
        
        status = result.get('status', 'unknown')
        if status in ['success', 'already_crawled']:
            successful += 1
            print(f"  ✓ Success")
        else:
            print(f"  ✗ {status}")
    
    print(f"\nStarter pack completed:")
    print(f"  Successful downloads: {successful}/{len(starter_artists)}")
    
    # Save results
    session_data = {
        'starter_pack': {
            'artists': starter_artists,
            'results': results,
            'successful_count': successful,
            'total_count': len(starter_artists)
        }
    }
    
    session_file = crawler.save_crawl_session(session_data)
    print(f"  Results saved to: {session_file}")
    
    return results

def main():
    """Interactive batch download interface"""
    print("=== MUSIC NETWORK BATCH DOWNLOADER ===\n")
    
    while True:
        print("Choose an option:")
        print("1. Download starter pack (16 diverse artists)")
        print("2. Download specific category")
        print("3. Download multiple categories")
        print("4. Show available categories")
        print("5. Exit")
        
        choice = input("\nEnter your choice (1-5): ").strip()
        
        if choice == '1':
            print("\n" + "="*50)
            quick_starter_pack()
            break
            
        elif choice == '2':
            show_available_categories()
            category = input("Enter category name: ").strip()
            if category in POPULAR_ARTISTS:
                print(f"\n" + "="*50)
                download_category(category)
                break
            else:
                print("Invalid category name.")
                continue
                
        elif choice == '3':
            show_available_categories()
            categories_input = input("Enter category names (comma-separated): ").strip()
            categories = [c.strip() for c in categories_input.split(',')]
            valid_categories = [c for c in categories if c in POPULAR_ARTISTS]
            
            if valid_categories:
                download_multiple_categories(valid_categories)
                break
            else:
                print("No valid categories entered.")
                continue
                
        elif choice == '4':
            show_available_categories()
            continue
            
        elif choice == '5':
            print("Goodbye!")
            return
            
        else:
            print("Invalid choice. Please enter 1-5.")
            continue
    
    print("\n✓ Download completed!")
    print("\nNext steps:")
    print("1. Run: python src/wikipedia_analyzer.py")
    print("2. Run: python src/network_builder.py")
    print("3. Run: python src/network_queries.py")

if __name__ == "__main__":
    main()
