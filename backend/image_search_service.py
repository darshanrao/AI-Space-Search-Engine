"""
Image Search Service using SerpApi Google Images API.
Fetches relevant images based on keywords from RAG responses.
"""

import os
from typing import List, Optional
from serpapi import GoogleSearch
from settings import settings


class ImageSearchService:
    """Service for searching images using SerpApi."""
    
    def __init__(self):
        """Initialize the image search service."""
        self.api_key = getattr(settings, 'SERPAPI_API_KEY', None)
        if not self.api_key:
            print("Warning: SERPAPI_API_KEY not found in settings. Image search will be disabled.")
    
    def search_images(self, keywords: List[str], max_images: int = 2) -> List[str]:
        """
        Search for images using the provided keywords.
        
        Args:
            keywords: List of keywords to search for
            max_images: Maximum number of images to return
            
        Returns:
            List of image URLs
        """
        if not self.api_key:
            return []
        
        if not keywords:
            return []
        
        # Combine keywords into a search query
        search_query = " ".join(keywords[:3])  # Use first 3 keywords to avoid overly long queries
        
        try:
            # Search parameters
            params = {
                "q": search_query,
                "engine": "google_images",
                "api_key": self.api_key,
                "num": max_images,
                "safe": "active",  # Safe search for scientific content
                "gl": "us",  # Country
                "hl": "en"   # Language
            }
            
            # Perform the search
            search = GoogleSearch(params)
            results = search.get_dict()
            
            # Extract image URLs
            image_urls = []
            if "images_results" in results:
                for result in results["images_results"][:max_images]:
                    if "original" in result:
                        image_urls.append(result["original"])
            
            return image_urls
            
        except Exception as e:
            print(f"Error searching images: {str(e)}")
            return []
    
    def search_images_for_keywords(self, keywords: List[str]) -> List[str]:
        """
        Search for images for each keyword and combine results.
        
        Args:
            keywords: List of keywords to search for
            
        Returns:
            List of unique image URLs
        """
        if not keywords:
            return []
        
        all_image_urls = []
        seen_urls = set()
        
        # Search for each keyword (limit to first 2 keywords to avoid rate limits)
        for keyword in keywords[:2]:
            try:
                image_urls = self.search_images([keyword], max_images=2)
                for url in image_urls:
                    if url not in seen_urls:
                        all_image_urls.append(url)
                        seen_urls.add(url)
                        
                        # Stop if we have enough images
                        if len(all_image_urls) >= 2:
                            break
                            
            except Exception as e:
                print(f"Error searching for keyword '{keyword}': {str(e)}")
                continue
        
        return all_image_urls[:2]  # Return max 2 images


# Global image search service instance
image_search_service = ImageSearchService()
