#!/usr/bin/env python3
"""
Image Search Module

This module provides functionality to search and download images automatically
based on card content using various image sources.
"""

import requests
import os
import hashlib
from pathlib import Path
from urllib.parse import quote_plus
import time
import random
from typing import Optional, List, Dict


class ImageSearcher:
    """Class to handle automatic image searching and downloading."""
    
    def __init__(self, cache_dir="image_cache"):
        """
        Initialize the image searcher.
        
        Args:
            cache_dir: Directory to cache downloaded images
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        
        # Headers to mimic a real browser
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # Rate limiting
        self.last_request_time = 0
        self.min_request_interval = 1.0  # 1 second between requests
    
    def _rate_limit(self):
        """Implement simple rate limiting."""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.min_request_interval:
            time.sleep(self.min_request_interval - time_since_last)
        self.last_request_time = time.time()
    
    def _generate_cache_key(self, search_query: str, card_data: Dict = None) -> str:
        """
        Generate a cache key for the search query and card content.
        This ensures that identical cards use the same image.
        """
        if card_data:
            # Create a stable key based on card content, not just search query
            title = card_data.get('title', '').lower().strip()
            body = card_data.get('body', {})
            
            # Create a content signature
            content_parts = [title]
            
            # Add body content in a consistent order
            for key in sorted(body.keys()):
                if body[key] and str(body[key]).lower().strip() != 'none':
                    content_parts.append(f"{key}:{body[key].lower().strip()}")
            
            content_signature = '|'.join(content_parts)
            return hashlib.md5(content_signature.encode()).hexdigest()
        else:
            # Fallback to search query based key
            return hashlib.md5(search_query.encode()).hexdigest()
    
    def _get_cached_image(self, search_query: str, card_data: Dict = None) -> Optional[str]:
        """Check if we have a cached image for this search query or card content."""
        cache_key = self._generate_cache_key(search_query, card_data)
        
        # Check for various image formats
        for ext in ['.jpg', '.jpeg', '.png', '.webp']:
            cached_file = self.cache_dir / f"{cache_key}{ext}"
            if cached_file.exists():
                return str(cached_file)
        return None
    
    def generate_search_query(self, card_data: Dict) -> str:
        """
        Generate a search query based on card content.
        
        Args:
            card_data: Dictionary containing card information
            
        Returns:
            Search query string
        """
        title = card_data.get('title', '').lower().strip()
        body = card_data.get('body', {})
        
        # Extract key terms from title and body
        search_terms = []
        
        # Add title (normalize for consistency)
        if title:
            # Remove common words and normalize
            title_words = [w for w in title.split() if len(w) > 2]
            search_terms.extend(title_words[:2])  # Take first 2 words from title
        
        # Add key terms from body in consistent order
        for key in ['effect', 'target']:  # Prioritize these fields
            value = body.get(key, '')
            if value and str(value).lower().strip() != 'none':
                # Extract meaningful words (skip common words)
                words = str(value).lower().split()
                meaningful_words = [w for w in words if len(w) > 3 and w not in 
                                  ['the', 'and', 'are', 'with', 'have', 'that', 'this', 'from', 'your', 'all']]
                search_terms.extend(meaningful_words[:1])  # Take 1 word from each field
        
        # Create consistent search query (limit to 3-4 main terms)
        search_query = ' '.join(search_terms[:3])
        
        # Add context for better results
        if search_query:
            search_query += ' fantasy game art'
        
        return search_query.strip()
    
    def search_unsplash(self, query: str, width: int = 400, height: int = 300) -> Optional[str]:
        """
        Search for images on Unsplash.
        
        Args:
            query: Search query
            width: Desired image width
            height: Desired image height
            
        Returns:
            URL of the first suitable image, or None if not found
        """
        try:
            self._rate_limit()
            
            # Unsplash random image URL with search query
            # This uses the unsplash.com/photos/random endpoint which doesn't require API key
            url = f"https://source.unsplash.com/{width}x{height}/?{quote_plus(query)}"
            
            response = requests.head(url, headers=self.headers, timeout=10, allow_redirects=True)
            
            if response.status_code == 200:
                return response.url
            else:
                print(f"Unsplash search failed for '{query}': {response.status_code}")
                return None
                
        except Exception as e:
            print(f"Error searching Unsplash for '{query}': {e}")
            return None
    
    def search_picsum(self, width: int = 400, height: int = 300) -> Optional[str]:
        """
        Get a random image from Lorem Picsum as fallback.
        
        Args:
            width: Desired image width
            height: Desired image height
            
        Returns:
            URL of a random image
        """
        try:
            # Use Lorem Picsum for random images
            image_id = random.randint(1, 1000)
            url = f"https://picsum.photos/{width}/{height}?random={image_id}"
            return url
        except Exception as e:
            print(f"Error getting Picsum image: {e}")
            return None
    
    def download_image(self, url: str, filename: str) -> bool:
        """
        Download image from URL.
        
        Args:
            url: Image URL
            filename: Local filename to save to
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self._rate_limit()
            
            response = requests.get(url, headers=self.headers, timeout=15, stream=True)
            response.raise_for_status()
            
            with open(filename, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            return True
            
        except Exception as e:
            print(f"Error downloading image from '{url}': {e}")
            return False
    
    def get_image_for_card(self, card_data: Dict) -> Optional[str]:
        """
        Get an image for a card, either from cache or by searching and downloading.
        Identical cards will always use the same image.
        
        Args:
            card_data: Dictionary containing card information
            
        Returns:
            Path to the image file, or None if not found
        """
        # Generate search query
        search_query = self.generate_search_query(card_data)
        if not search_query:
            print("Warning: Could not generate search query for card")
            return None
        
        card_title = card_data.get('title', 'Unknown')
        print(f"Searching for image for '{card_title}': '{search_query}'")
        
        # Check cache first (using both search query and card content)
        cached_image = self._get_cached_image(search_query, card_data)
        if cached_image:
            print(f"Using cached image for '{card_title}': {cached_image}")
            return cached_image
        
        # Search for new image
        image_url = self.search_unsplash(search_query)
        
        # If search fails, don't use random images as they can misleading
        if not image_url:
            print(f"Unsplash search failed for '{card_title}', "
                  f"no suitable image found")
            return None
        
        # Download image using card-based cache key
        cache_key = self._generate_cache_key(search_query, card_data)
        filename = self.cache_dir / f"{cache_key}.jpg"
        
        if self.download_image(image_url, str(filename)):
            print(f"Downloaded image for '{card_title}': {filename}")
            return str(filename)
        else:
            print(f"Error: Failed to download image for '{card_title}'")
            return None


def main():
    """Test the image searcher."""
    searcher = ImageSearcher()
    
    # Test card
    test_card = {
        "title": "Lightning Bolt",
        "body": {
            "effect": "Deal 3 damage to any target",
            "target": "Choose any target"
        }
    }
    
    image_path = searcher.get_image_for_card(test_card)
    if image_path:
        print(f"Success! Image saved to: {image_path}")
    else:
        print("Failed to get image")


if __name__ == '__main__':
    main()