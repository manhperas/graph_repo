#!/usr/bin/env python3
"""
Simple Artist Crawler Script
Easy-to-use script for downloading Wikipedia data about specific artists or discovering new ones.
"""

import argparse
import sys
from pathlib import Path
from wikipedia_crawler import WikipediaCrawler, CrawlerConfig

def crawl_specific_artists(artist_names: list, config: CrawlerConfig = None):
    """Crawl specific artists by name"""
    crawler = WikipediaCrawler(config or CrawlerConfig())
    
    print(f"Starting to crawl {len(artist_names)} artists...")
    results = {}
    
    for i, artist in enumerate(artist_names, 1):
        print(f"\n[{i}/{len(artist_names)}] Crawling: {artist}")
        result = crawler.crawl_artist(artist)
        results[artist] = result
        
        status = result.get('status', 'unknown')
        if status == 'success':
            print(f"  ✓ Success - Found {len(result.get('related_artists', []))} related artists")
        elif status == 'not_music_related':
            print(f"  ! Not music-related")
        elif status == 'page_not_found':
            print(f"  ✗ Page not found")
        else:
            print(f"  ? Status: {status}")
    
    # Save session
    session_file = crawler.save_crawl_session({'manual_crawl': results})
    print(f"\nResults saved to: {session_file}")
    
    return results

def discover_and_crawl_genre(genre: str, limit: int = 10, config: CrawlerConfig = None):
    """Discover and crawl artists by genre"""
    crawler = WikipediaCrawler(config or CrawlerConfig())
    
    print(f"Discovering {genre} artists (limit: {limit})...")
    
    # Discover artists
    discovered = crawler.discover_artists_by_genre(genre, limit=limit*2)  # Get extra to filter
    print(f"Found {len(discovered)} potential {genre} artists")
    
    if not discovered:
        print("No artists found. Try a different genre or search term.")
        return {}
    
    # Show discovered artists
    print("\nDiscovered artists:")
    for i, artist in enumerate(discovered[:limit], 1):
        print(f"  {i}. {artist}")
    
    # Ask user which ones to crawl
    print(f"\nWould you like to crawl all {min(len(discovered), limit)} artists? (y/n): ", end="")
    response = input().strip().lower()
    
    if response == 'y':
        artists_to_crawl = discovered[:limit]
    else:
        # Let user choose specific ones
        print("Enter the numbers of artists to crawl (comma-separated, e.g., 1,3,5): ", end="")
        try:
            indices = [int(x.strip()) - 1 for x in input().split(',')]
            artists_to_crawl = [discovered[i] for i in indices if 0 <= i < len(discovered)]
        except:
            print("Invalid input. Crawling first 5 artists.")
            artists_to_crawl = discovered[:5]
    
    print(f"\nCrawling {len(artists_to_crawl)} selected artists...")
    
    # Crawl selected artists
    results = {}
    for i, artist in enumerate(artists_to_crawl, 1):
        print(f"\n[{i}/{len(artists_to_crawl)}] Crawling: {artist}")
        result = crawler.crawl_artist(artist)
        results[artist] = result
        
        status = result.get('status', 'unknown')
        if status == 'success':
            print(f"  ✓ Success")
        else:
            print(f"  Status: {status}")
    
    # Save session
    session_data = {
        'genre_discovery': {
            'genre': genre,
            'discovered_artists': discovered,
            'crawled_artists': list(results.keys()),
            'results': results
        }
    }
    
    session_file = crawler.save_crawl_session(session_data)
    print(f"\nResults saved to: {session_file}")
    
    return results

def network_crawl(seed_artists: list, max_depth: int = 2, max_total: int = 20, config: CrawlerConfig = None):
    """Perform network crawling starting from seed artists"""
    crawler = WikipediaCrawler(config or CrawlerConfig())
    
    print(f"Starting network crawl from {len(seed_artists)} seed artists...")
    print(f"Max depth: {max_depth}, Max total artists: {max_total}")
    
    results = crawler.crawl_artist_network(
        seed_artists=seed_artists,
        max_depth=max_depth,
        max_artists=max_total
    )
    
    print(f"\nNetwork crawl completed:")
    print(f"  Total attempted: {results['total_attempted']}")
    print(f"  Successful: {results['successful_crawls']}")
    print(f"  Failed: {results['failed_crawls']}")
    print(f"  Depths crawled: {results['depths_crawled']}")
    
    # Show successful crawls
    successful = [name for name, result in results['results'].items() 
                 if result.get('status') == 'success']
    
    if successful:
        print(f"\nSuccessfully crawled artists:")
        for i, artist in enumerate(successful, 1):
            print(f"  {i}. {artist}")
    
    session_file = crawler.save_crawl_session(results)
    print(f"\nNetwork crawl results saved to: {session_file}")
    
    return results

def main():
    parser = argparse.ArgumentParser(description="Crawl Wikipedia data for musicians and artists")
    
    # Add subcommands
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Crawl specific artists
    artists_parser = subparsers.add_parser('artists', help='Crawl specific artists by name')
    artists_parser.add_argument('names', nargs='+', help='Artist names to crawl')
    artists_parser.add_argument('--delay', type=float, default=1.5, help='Delay between requests (seconds)')
    
    # Discover by genre
    genre_parser = subparsers.add_parser('genre', help='Discover and crawl artists by genre')
    genre_parser.add_argument('genre', help='Musical genre to search for')
    genre_parser.add_argument('--limit', type=int, default=10, help='Maximum artists to discover')
    genre_parser.add_argument('--delay', type=float, default=1.5, help='Delay between requests (seconds)')
    
    # Network crawling
    network_parser = subparsers.add_parser('network', help='Perform network crawling from seed artists')
    network_parser.add_argument('seeds', nargs='+', help='Seed artist names')
    network_parser.add_argument('--depth', type=int, default=2, help='Maximum crawling depth')
    network_parser.add_argument('--max-artists', type=int, default=20, help='Maximum total artists to crawl')
    network_parser.add_argument('--delay', type=float, default=2.0, help='Delay between requests (seconds)')
    
    # Parse arguments
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Create config
    config = CrawlerConfig(
        min_delay=args.delay * 0.8,
        max_delay=args.delay * 1.2,
        save_html=True,
        save_api_data=True
    )
    
    try:
        if args.command == 'artists':
            crawl_specific_artists(args.names, config)
            
        elif args.command == 'genre':
            discover_and_crawl_genre(args.genre, args.limit, config)
            
        elif args.command == 'network':
            network_crawl(args.seeds, args.depth, args.max_artists, config)
            
        print("\n✓ Crawling completed successfully!")
        print("\nNext steps:")
        print("1. Run: python src/wikipedia_analyzer.py")
        print("2. Run: python src/network_builder.py")
        print("3. Run: python src/network_queries.py")
        
    except KeyboardInterrupt:
        print("\n\nCrawling interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\nError during crawling: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
