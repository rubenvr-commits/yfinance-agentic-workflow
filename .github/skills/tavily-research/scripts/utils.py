#!/usr/bin/env python3
"""
Tavily API Client - Wrapper for invoking Tavily research tools via HTTP API

This module handles HTTP communication with Tavily's REST API and normalizes
results to a consistent schema.
"""

import json
import os
import sys
from typing import Dict, List, Optional, Any
import logging
import requests

# Fix encoding for Windows console (UTF-8 instead of charmap)
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TavilyAPIClient:
    """
    Client for invoking Tavily research tools via HTTP API.
    
    Communicates with Tavily REST API, handles search queries,
    and normalizes results to consistent schema.
    """
    
    API_ENDPOINT = "https://api.tavily.com/search"
    
    def __init__(self, timeout: int = 60):
        """
        Initialize Tavily API client.
        
        Args:
            timeout: Timeout in seconds for API requests.
        """
        self.timeout = timeout
        self.api_key = None
        self._initialize_client()
    
    
    def _initialize_client(self):
        """Initialize the API client and validate API key."""
        try:
            logger.info("Initializing Tavily API client...")
            
            # Get Tavily API key from environment
            self.api_key = os.environ.get('TAVILY_API_KEY')
            if not self.api_key:
                raise RuntimeError("TAVILY_API_KEY environment variable is required")
            
            logger.info("[OK] Tavily API client initialized successfully")
        except Exception as e:
            logger.error(f"[ERROR] Failed to initialize API client: {e}")
            raise
    
    
    def search_criterion(self, query: str, max_results: int = 3, search_depth: str = "basic") -> Dict[str, Any]:
        """
        Execute a search query using Tavily API.
        
        Args:
            query: Search query string
            max_results: Maximum number of results to return
            search_depth: Search depth ("basic" or "advanced")
        
        Returns:
            Dict with normalized results: {results: [{title, snippet, source, relevance_score}]}
        """
        results = {
            "results": [],
            "status": "pending",
            "query_used": query,
            "error": None
        }
        
        try:
            logger.info(f"Searching with Tavily API (depth={search_depth}): {query[:60]}...")
            
            # Prepare API request
            payload = {
                "api_key": self.api_key,
                "query": query,
                "include_answer": True,
                "search_depth": search_depth,
                "max_results": max_results
            }
            
            # Make HTTP request to Tavily API
            response = requests.post(
                self.API_ENDPOINT,
                json=payload,
                timeout=self.timeout
            )
            
            # Check for HTTP errors
            if response.status_code != 200:
                logger.warning(f"API returned status {response.status_code}: {response.text}")
                results["status"] = "error"
                results["error"] = f"HTTP {response.status_code}"
                return results
            
            # Parse response
            api_response = response.json()
            
            # Check for API-level errors
            if api_response.get('success') is False:
                logger.warning(f"API error: {api_response.get('error', 'Unknown error')}")
                results["status"] = "error"
                results["error"] = api_response.get('error', 'Unknown error')
                return results
            
            # Normalize results
            normalized_results = self._normalize_results(api_response)
            results["results"] = normalized_results
            results["status"] = "completed"
            logger.info(f"[OK] Found {len(normalized_results)} results")
        
        except requests.exceptions.Timeout:
            results["status"] = "error"
            results["error"] = f"Request timeout after {self.timeout}s"
            logger.error(f"Request timeout: {results['error']}")
        except requests.exceptions.RequestException as e:
            results["status"] = "error"
            results["error"] = str(e)
            logger.error(f"Network error: {e}")
        except json.JSONDecodeError as e:
            results["status"] = "error"
            results["error"] = "Invalid JSON response"
            logger.error(f"JSON decode error: {e}")
        except Exception as e:
            results["status"] = "error"
            results["error"] = str(e)
            logger.error(f"Search error: {e}")
        
        return results
    
    
    def _normalize_results(self, response: Any) -> List[Dict[str, Any]]:
        """
        Normalize Tavily API response to standard schema.
        
        Args:
            response: Response dict from Tavily API
        
        Returns:
            List of normalized results: [{title, snippet, source, relevance_score}]
        """
        normalized = []
        
        # Extract results from API response
        results_list = response.get('results', [])
        
        # Also include the answer if available
        if response.get('answer'):
            results_list.insert(0, {
                'title': 'AI Answer',
                'snippet': response.get('answer'),
                'source': '',
                'relevance_score': 1.0
            })
        
        # Normalize each result
        for item in results_list:
            if isinstance(item, dict):
                normalized_item = {
                    'title': item.get('title', 'Untitled'),
                    'snippet': item.get('content') or item.get('snippet') or '',
                    'source': item.get('url') or '',
                    'relevance_score': self._calculate_relevance_score(item.get('content') or item.get('snippet') or '')
                }
                
                if normalized_item['snippet']:
                    normalized.append(normalized_item)
        
        return normalized

    def _calculate_relevance_score(self, content: str) -> float:
        """
        Simple relevance score based on content length.
        
        Args:
            content: Text content
        
        Returns:
            Score between 0.0 and 1.0
        """
        if not content:
            return 0.0
        length = len(content)
        if length < 50:
            return 0.3
        elif length < 100:
            return 0.6
        elif length < 500:
            return 0.9
        else:
            return 1.0
    
    
    def close(self):
        """Close API client connection (no-op for HTTP client)."""
        logger.info("[OK] API client connection closed")


def create_client(timeout: int = 60) -> TavilyAPIClient:
    """
    Factory function to create and initialize TavilyAPIClient.
    
    Args:
        timeout: Timeout in seconds
    
    Returns:
        Initialized TavilyAPIClient instance
    """
    return TavilyAPIClient(timeout=timeout)
