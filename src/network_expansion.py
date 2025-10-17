#!/usr/bin/env python3
"""
Network Expansion Algorithms
Advanced algorithms for expanding music networks from seed artists using BFS, DFS, and hybrid approaches.
"""

import json
import time
from typing import Dict, List, Any, Set, Optional, Tuple
from collections import deque, defaultdict
from pathlib import Path
from wikipedia_crawler import WikipediaCrawler, CrawlerConfig
import argparse
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class NetworkExpansionEngine:
    """Engine for expanding music networks using various algorithms"""

    def __init__(self, crawler: Optional[WikipediaCrawler] = None):
        self.crawler = crawler or WikipediaCrawler(CrawlerConfig())
        self.expansion_history = []
        self.stats = {}

    def bfs_expansion(self,
                     seed_artists: List[str],
                     max_depth: int = 3,
                     max_artists: int = 50,
                     branching_factor: int = 3,
                     min_related_threshold: int = 2) -> Dict[str, Any]:
        """
        Breadth-First Search expansion from seed artists

        Args:
            seed_artists: Initial artists to start from
            max_depth: Maximum depth to explore
            max_artists: Maximum total artists to crawl
            branching_factor: Max related artists to explore per artist
            min_related_threshold: Minimum related artists needed to continue
        """
        logger.info(f"Starting BFS expansion from {len(seed_artists)} seed artists")
        logger.info(f"Parameters: depth={max_depth}, max_artists={max_artists}, branching={branching_factor}")

        # BFS queue: (artist_name, depth, parent_artist)
        queue = deque([(artist, 0, None) for artist in seed_artists])
        visited = set()
        crawl_results = {}
        depth_stats = defaultdict(int)

        while queue and len(crawl_results) < max_artists:
            current_artist, current_depth, parent = queue.popleft()

            if current_artist in visited or current_depth > max_depth:
                continue

            visited.add(current_artist)
            depth_stats[current_depth] += 1

            logger.info(f"Crawling: {current_artist} (depth {current_depth})")

            # Crawl the artist
            result = self.crawler.crawl_artist(current_artist)
            crawl_results[current_artist] = {
                **result,
                'depth': current_depth,
                'parent': parent,
                'expansion_method': 'bfs'
            }

            # Add to expansion history
            self.expansion_history.append({
                'artist': current_artist,
                'depth': current_depth,
                'parent': parent,
                'method': 'bfs',
                'timestamp': time.time(),
                'related_found': len(result.get('related_artists', []))
            })

            # If successful and not at max depth, add related artists to queue
            if (result.get('status') == 'success' and
                current_depth < max_depth and
                len(crawl_results) < max_artists):

                related_artists = result.get('related_artists', [])
                # Limit branching factor and filter out already visited
                related_to_explore = [
                    related for related in related_artists[:branching_factor]
                    if related not in visited and related not in self.crawler.crawled_artists
                ]

                if len(related_to_explore) >= min_related_threshold:
                    for related in related_to_explore:
                        queue.append((related, current_depth + 1, current_artist))
                else:
                    logger.info(f"  Stopping expansion from {current_artist}: only {len(related_to_explore)} unexplored related artists")

        # Calculate statistics
        stats = self._calculate_expansion_stats(crawl_results, depth_stats, 'bfs')
        stats.update({
            'algorithm': 'BFS',
            'max_depth': max_depth,
            'branching_factor': branching_factor,
            'min_related_threshold': min_related_threshold
        })

        return {
            'results': crawl_results,
            'stats': stats,
            'depth_distribution': dict(depth_stats)
        }

    def dfs_expansion(self,
                     seed_artists: List[str],
                     max_depth: int = 3,
                     max_artists: int = 50,
                     branching_factor: int = 2,
                     exploration_ratio: float = 0.7) -> Dict[str, Any]:
        """
        Depth-First Search expansion with smart backtracking

        Args:
            seed_artists: Initial artists to start from
            max_depth: Maximum depth to explore
            max_artists: Maximum total artists to crawl
            branching_factor: Max related artists to explore per artist
            exploration_ratio: Ratio of related artists to explore (0.0-1.0)
        """
        logger.info(f"Starting DFS expansion from {len(seed_artists)} seed artists")
        logger.info(f"Parameters: depth={max_depth}, max_artists={max_artists}, branching={branching_factor}, ratio={exploration_ratio}")

        crawl_results = {}
        depth_stats = defaultdict(int)
        visited = set()

        def dfs_recursive(artist: str, depth: int, parent: str = None):
            if (artist in visited or
                depth > max_depth or
                len(crawl_results) >= max_artists):
                return

            visited.add(artist)
            depth_stats[depth] += 1

            logger.info(f"Crawling: {artist} (depth {depth})")

            # Crawl the artist
            result = self.crawler.crawl_artist(artist)
            crawl_results[artist] = {
                **result,
                'depth': depth,
                'parent': parent,
                'expansion_method': 'dfs'
            }

            # Add to expansion history
            self.expansion_history.append({
                'artist': artist,
                'depth': depth,
                'parent': parent,
                'method': 'dfs',
                'timestamp': time.time(),
                'related_found': len(result.get('related_artists', []))
            })

            # If successful and not at max depth, explore related artists
            if (result.get('status') == 'success' and
                depth < max_depth and
                len(crawl_results) < max_artists):

                related_artists = result.get('related_artists', [])
                # Sort by some criteria (for now, just take first N based on exploration_ratio)
                num_to_explore = max(1, int(len(related_artists) * exploration_ratio))
                related_to_explore = related_artists[:min(branching_factor, num_to_explore)]

                for related in related_to_explore:
                    if (related not in visited and
                        related not in self.crawler.crawled_artists and
                        len(crawl_results) < max_artists):
                        dfs_recursive(related, depth + 1, artist)

        # Start DFS from each seed artist
        for seed in seed_artists:
            if len(crawl_results) < max_artists:
                dfs_recursive(seed, 0)

        # Calculate statistics
        stats = self._calculate_expansion_stats(crawl_results, depth_stats, 'dfs')
        stats.update({
            'algorithm': 'DFS',
            'max_depth': max_depth,
            'branching_factor': branching_factor,
            'exploration_ratio': exploration_ratio
        })

        return {
            'results': crawl_results,
            'stats': stats,
            'depth_distribution': dict(depth_stats)
        }

    def iterative_expansion(self,
                           seed_artists: List[str],
                           iterations: int = 3,
                           artists_per_iteration: int = 10,
                           method: str = 'bfs',
                           **kwargs) -> Dict[str, Any]:
        """
        Iterative expansion with multiple rounds of discovery

        Args:
            seed_artists: Initial artists
            iterations: Number of expansion iterations
            artists_per_iteration: Artists to add per iteration
            method: 'bfs' or 'dfs'
            **kwargs: Additional parameters for the chosen method
        """
        logger.info(f"Starting iterative expansion with {iterations} iterations")
        logger.info(f"Method: {method}, artists_per_iteration: {artists_per_iteration}")

        current_artists = set(seed_artists)
        all_results = {}
        iteration_stats = []

        for iteration in range(iterations):
            logger.info(f"\n=== ITERATION {iteration + 1}/{iterations} ===")

            # Expand from current artists
            if method == 'bfs':
                expansion_result = self.bfs_expansion(
                    list(current_artists),
                    max_artists=len(current_artists) + artists_per_iteration,
                    **kwargs
                )
            elif method == 'dfs':
                expansion_result = self.dfs_expansion(
                    list(current_artists),
                    max_artists=len(current_artists) + artists_per_iteration,
                    **kwargs
                )
            else:
                raise ValueError(f"Unknown method: {method}")

            # Add new results
            new_artists = set(expansion_result['results'].keys()) - current_artists
            current_artists.update(new_artists)
            all_results.update(expansion_result['results'])

            # Track iteration statistics
            iteration_stats.append({
                'iteration': iteration + 1,
                'new_artists': len(new_artists),
                'total_artists': len(current_artists),
                'stats': expansion_result['stats']
            })

            logger.info(f"Iteration {iteration + 1}: Added {len(new_artists)} new artists, total: {len(current_artists)}")

            if len(new_artists) == 0:
                logger.info("No new artists found, stopping early")
                break

        return {
            'results': all_results,
            'iterations': iteration_stats,
            'final_stats': self._calculate_expansion_stats(all_results, {}, f'iterative_{method}')
        }

    def _calculate_expansion_stats(self, results: Dict, depth_stats: Dict, method: str) -> Dict[str, Any]:
        """Calculate comprehensive expansion statistics"""
        successful = [r for r in results.values() if r.get('status') == 'success']
        failed = [r for r in results.values() if r.get('status') not in ['success', 'already_crawled']]

        stats = {
            'total_artists': len(results),
            'successful_crawls': len(successful),
            'failed_crawls': len(failed),
            'success_rate': len(successful) / len(results) if results else 0,
            'max_depth_reached': max((r.get('depth', 0) for r in results.values()), default=0),
            'method': method,
            'timestamp': time.time()
        }

        if depth_stats:
            stats['depth_distribution'] = dict(depth_stats)
            stats['avg_artists_per_depth'] = len(results) / len(depth_stats) if depth_stats else 0

        return stats

    def save_expansion_results(self, results: Dict[str, Any], filename: str = None) -> str:
        """Save expansion results to file"""
        if not filename:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"network_expansion_{timestamp}.json"

        # Save crawler session and get filename
        session_file = self.crawler.save_crawl_session(results.get('results', {}))

        output_data = {
            'expansion_results': results,
            'expansion_history': self.expansion_history,
            'crawler_session_file': str(session_file)  # Convert Path to string
        }

        with open(f"data/processed/{filename}", 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)

        logger.info(f"Expansion results saved to: data/processed/{filename}")
        return filename


def load_seed_sets() -> Dict[str, List[str]]:
    """Load available seed sets from batch_download.py"""
    # Import the seed sets directly
    seed_sets = {
        'quick_starter': [
            'The Beatles', 'Queen', 'Led Zeppelin', 'Radiohead', 'Coldplay', 'Arctic Monkeys',
            'Ed Sheeran', 'Adele', 'Nirvana', 'Pearl Jam', 'Taylor Swift', 'Bruno Mars',
            'Kanye West', 'Drake', 'The Strokes', 'Vampire Weekend'
        ],
        'uk_classic_rock': ['The Beatles', 'Led Zeppelin', 'Queen', 'Pink Floyd', 'The Rolling Stones'],
        'uk_modern_rock': ['Radiohead', 'Coldplay', 'Oasis', 'Blur', 'Arctic Monkeys'],
        'us_classic_rock': ['Nirvana', 'Pearl Jam', 'Soundgarden', 'Alice in Chains', 'Red Hot Chili Peppers'],
        'us_pop': ['Taylor Swift', 'Ariana Grande', 'Billie Eilish', 'The Weeknd', 'Bruno Mars'],
        'us_hip_hop': ['Jay-Z', 'Kanye West', 'Eminem', 'Drake', 'Travis Scott'],
        'alternative_indie': ['Vampire Weekend', 'The Strokes', 'Arcade Fire', 'Tame Impala', 'Foster the People']
    }
    return seed_sets


def main():
    """Main function for network expansion demonstration"""
    parser = argparse.ArgumentParser(description="Network Expansion Algorithms for Music Graph")
    parser.add_argument('--algorithm', choices=['bfs', 'dfs', 'iterative'], default='bfs',
                       help='Expansion algorithm to use')
    parser.add_argument('--seed-set', choices=['quick_starter', 'uk_classic_rock', 'uk_modern_rock',
                                              'us_classic_rock', 'us_pop', 'us_hip_hop', 'alternative_indie'],
                       default='quick_starter', help='Seed set to start from')
    parser.add_argument('--max-depth', type=int, default=2, help='Maximum depth for expansion')
    parser.add_argument('--max-artists', type=int, default=30, help='Maximum artists to crawl')
    parser.add_argument('--iterations', type=int, default=3, help='Number of iterations for iterative method')
    parser.add_argument('--branching-factor', type=int, default=3, help='Branching factor for BFS/DFS')
    parser.add_argument('--delay', type=float, default=1.5, help='Delay between requests')

    args = parser.parse_args()

    # Load seed sets
    seed_sets = load_seed_sets()
    seed_artists = seed_sets[args.seed_set]

    print("🎵 MUSIC NETWORK EXPANSION ENGINE")
    print(f"Algorithm: {args.algorithm.upper()}")
    print(f"Seed Set: {args.seed_set} ({len(seed_artists)} artists)")
    print(f"Parameters: depth={args.max_depth}, max_artists={args.max_artists}")
    print(f"Seeds: {', '.join(seed_artists[:5])}{'...' if len(seed_artists) > 5 else ''}")
    print("-" * 60)

    # Initialize crawler and engine
    config = CrawlerConfig(min_delay=args.delay, max_delay=args.delay*1.2)
    engine = NetworkExpansionEngine(WikipediaCrawler(config))

    start_time = time.time()

    try:
        if args.algorithm == 'bfs':
            results = engine.bfs_expansion(
                seed_artists=seed_artists,
                max_depth=args.max_depth,
                max_artists=args.max_artists,
                branching_factor=args.branching_factor
            )

        elif args.algorithm == 'dfs':
            results = engine.dfs_expansion(
                seed_artists=seed_artists,
                max_depth=args.max_depth,
                max_artists=args.max_artists,
                branching_factor=args.branching_factor
            )

        elif args.algorithm == 'iterative':
            results = engine.iterative_expansion(
                seed_artists=seed_artists,
                iterations=args.iterations,
                artists_per_iteration=max(5, args.max_artists // args.iterations),
                method='bfs',
                max_depth=args.max_depth,
                branching_factor=args.branching_factor
            )

        # Save results
        filename = engine.save_expansion_results(results)

        # Print summary
        elapsed = time.time() - start_time
        stats = results.get('stats', {})

        print("\n" + "="*60)
        print("EXPANSION COMPLETED")
        print("="*60)
        print(f"Time elapsed: {elapsed:.1f} seconds")
        print(f"Total artists crawled: {stats.get('total_artists', 0)}")
        print(f"Successful: {stats.get('successful_crawls', 0)}")
        print(f"Success rate: {stats.get('success_rate', 0)*100:.1f}%")
        print(f"Max depth reached: {stats.get('max_depth_reached', 0)}")
        print(f"Results saved to: data/processed/{filename}")

        if 'depth_distribution' in results:
            print("\nDepth Distribution:")
            for depth, count in sorted(results['depth_distribution'].items()):
                print(f"  Depth {depth}: {count} artists")

        print("\nNext steps:")
        print("1. Run: python src/wikipedia_analyzer.py")
        print("2. Run: python src/network_builder.py")
        print("3. Run: python src/network_queries.py")

    except KeyboardInterrupt:
        print("\n\nExpansion interrupted by user.")
    except Exception as e:
        print(f"\nError during expansion: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
