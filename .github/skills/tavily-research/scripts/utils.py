#!/usr/bin/env python3
"""
MCP Tavily Client - Wrapper for invoking Tavily research tools via MCP protocol

This module handles communication with tavily-mcp server through stdio and normalizes
results to a consistent schema.
"""

import json
import os
import subprocess
import sys
import threading
from typing import Dict, List, Optional, Any
import logging

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


class MCPTavilyClient:
    """
    Client for invoking Tavily research tools via MCP protocol.
    
    Communicates with tavily-mcp server through stdio, handles tool invocation,
    and normalizes results to consistent schema.
    """
    
    def __init__(self, timeout: int = 60):
        """
        Initialize MCP Tavily client.
        
        Args:
            timeout: Timeout in seconds for MCP responses.
        """
        self.timeout = timeout
        self.process = None
        self._initialize_server()
    
    
    def _initialize_server(self):
        """Start tavily-mcp server via stdio."""
        try:
            logger.info("Starting tavily-mcp server...")
            
            # Get Tavily API key from environment only.
            api_key = os.environ.get('TAVILY_API_KEY')
            if not api_key:
                raise RuntimeError("TAVILY_API_KEY environment variable is required")
            
            env = os.environ.copy()
            env['TAVILY_API_KEY'] = api_key
            
            # Start server: npx -y tavily-mcp@latest
            # Use shell=True on Windows to find npx in PATH
            command = "npx -y tavily-mcp@latest"
            self.process = subprocess.Popen(
                command,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=env,
                text=True,
                encoding='utf-8',
                errors='replace',
                bufsize=1,
                shell=True  # Use shell=True to resolve npx in Windows PATH
            )
            
            logger.info("[OK] Server started successfully")
            self._initialize_mcp_client()
        except Exception as e:
            logger.error(f"[ERROR] Failed to start MCP server: {e}")
            raise
    
    
    def _call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Call a tool on the MCP server.
        
        Args:
            tool_name: Name of the tool (e.g., 'tavily_research', 'tavily_search')
            arguments: Tool arguments
        
        Returns:
            Tool response or None if failed
        """
        if not self.process:
            logger.error("MCP server not initialized")
            return None
        
        try:
            # For tavily-mcp, use the tool's input schema directly
            if tool_name == "tavily_research":
                wrapped_args = {
                    "input": arguments.get("query", ""),
                    "model": arguments.get("model", "pro")
                }
            elif tool_name == "tavily_search":
                wrapped_args = {
                    "query": arguments.get("query", ""),
                    "search_depth": arguments.get("search_depth", "advanced"),
                    "max_results": arguments.get("max_results", 5)
                }
            else:
                wrapped_args = arguments
            
            # Prepare tool call message (MCP JSON-RPC format)
            request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/call",
                "params": {
                    "name": tool_name,
                    "arguments": wrapped_args
                }
            }
            
            logger.debug(f"Calling tool: {tool_name} with args: {wrapped_args}")
            
            # Send request to server
            self.process.stdin.write(json.dumps(request) + "\n")
            self.process.stdin.flush()
            
            # Read response with timeout
            response_line = self._read_stdout_json()
            if not response_line:
                stderr_line = self._read_stderr_line()
                if stderr_line:
                    logger.error(f"Server stderr: {stderr_line.strip()}")
                logger.warning(f"No response from server for tool: {tool_name} within timeout {self.timeout}s")
                return None
            
            response = response_line
            logger.debug(f"Tool response: {response}")
            
            # Extract result
            if 'result' in response:
                return response['result']
            elif 'error' in response:
                logger.error(f"Tool error: {response['error']}")
                return None
            else:
                return response
        
        except Exception as e:
            logger.error(f"Error calling tool {tool_name}: {e}")
            return None

    def _read_stdout_json(self) -> Optional[Dict[str, Any]]:
        """Read JSON response from stdout with a timeout."""
        result: Dict[str, Any] = {'json': None}

        def reader():
            buffer = ''
            started = False
            while True:
                try:
                    line = self.process.stdout.readline()
                except Exception:
                    break

                if line is None:
                    break

                stripped = line.strip()
                if not stripped:
                    continue

                if not started and stripped[0] not in '{[':
                    continue

                started = True
                buffer += line

                try:
                    parsed = json.loads(buffer)
                    result['json'] = parsed
                    break
                except json.JSONDecodeError:
                    # Continue reading until the JSON message is complete
                    continue

        thread = threading.Thread(target=reader, daemon=True)
        thread.start()
        thread.join(self.timeout)
        if thread.is_alive():
            return None
        return result['json']

    def _read_stderr_line(self) -> Optional[str]:
        """Read one line from stderr with a short timeout."""
        result = {'line': None}

        def reader():
            try:
                line = self.process.stderr.readline()
                result['line'] = line
            except Exception:
                result['line'] = None

        thread = threading.Thread(target=reader, daemon=True)
        thread.start()
        thread.join(1)
        if thread.is_alive():
            return None
        return result['line']

    def _initialize_mcp_client(self):
        """Initialize the MCP client by sending the JSON-RPC initialize request."""
        if not self.process:
            raise RuntimeError("MCP server process is not initialized")

        initialize_request = {
            "jsonrpc": "2.0",
            "id": 0,
            "method": "initialize",
            "params": {
                "protocolVersion": "1.0",
                "clientInfo": {
                    "name": "tavily_researcher",
                    "version": "1.0"
                },
                "capabilities": {}
            }
        }

        logger.info("Initializing MCP client...")
        self.process.stdin.write(json.dumps(initialize_request) + "\n")
        self.process.stdin.flush()

        response = self._read_stdout_json()
        if not response:
            raise RuntimeError("MCP initialize request did not receive a response")

        if 'error' in response:
            raise RuntimeError(f"MCP initialize error: {response['error']}")

        logger.info("[OK] MCP initialize completed")
    
    
    def search_criterion(self, query: str, max_results: int = 3, model: str = "mini") -> Dict[str, Any]:
        """
        Execute a search query using Tavily.
        
        Tries tavily_research first (with mini model for efficiency), falls back to tavily_search if unavailable.
        
        Args:
            query: Search query string
            max_results: Maximum number of results to return
            model: Model to use for tavily_research ("mini" for efficiency, "pro" for quality)
        
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
            # Try tavily_research first (with mini model for token efficiency)
            logger.info(f"Searching with tavily_research (model={model}): {query[:60]}...")
            response = self._call_tool("tavily_research", {
                "query": query,
                "model": model
            })
            
            if response is None or self._is_error_response(response):
                if response is None:
                    logger.warning("tavily_research unavailable, trying tavily_search...")
                else:
                    logger.warning("tavily_research returned error response, trying tavily_search...")
                # Fallback to tavily_search with basic depth
                response = self._call_tool("tavily_search", {
                    "query": query,
                    "max_results": max_results,
                    "search_depth": "basic"
                })
            
            # Normalize results
            if response and not self._is_error_response(response):
                normalized_results = self._normalize_results(response)
                results["results"] = normalized_results
                results["status"] = "completed"
                logger.info(f"[OK] Found {len(normalized_results)} results")
            else:
                results["status"] = "no_results"
                if response and self._is_error_response(response):
                    logger.warning(f"[WARN] Tool response flagged as error for query: {query[:60]}...")
                else:
                    logger.warning(f"[WARN] No results found for query: {query[:60]}...")
        
        except Exception as e:
            results["status"] = "error"
            results["error"] = str(e)
            logger.error(f"Search error: {e}")
        
        return results
    
    
    def _normalize_results(self, response: Any) -> List[Dict[str, Any]]:
        """
        Normalize MCP Tavily response to standard schema.
        
        Args:
            response: Raw response from tavily tool
        
        Returns:
            List of normalized results: [{title, snippet, source, relevance_score}]
        """
        normalized = []
        
        # Handle different response formats
        results_list = []
        
        if isinstance(response, dict):
            # If response has top-level 'results'
            if 'results' in response:
                results_list = response['results']
            # If response returns tavily_research/tavily_search structure
            elif 'content' in response:
                text = self._extract_text_from_content(response['content'])
                results_list = [
                    {
                        'title': self._extract_title_from_text(text),
                        'snippet': self._extract_snippet_from_text(text),
                        'source': self._extract_source_from_text(text),
                        'relevance_score': self._calculate_relevance_score(text)
                    }
                ]
            elif 'answer' in response:
                results_list = [response]
            else:
                results_list = [response]
        elif isinstance(response, list):
            results_list = response
        
        # Normalize each result
        for item in results_list:
            if isinstance(item, dict):
                if 'content' in item and isinstance(item['content'], list):
                    text = self._extract_text_from_content(item['content'])
                    normalized_item = {
                        'title': self._extract_title_from_text(text),
                        'snippet': self._extract_snippet_from_text(text),
                        'source': self._extract_source_from_text(text),
                        'relevance_score': self._calculate_relevance_score(text)
                    }
                    if normalized_item['snippet']:
                        normalized.append(normalized_item)
                    continue

                snippet_text = ''
                if isinstance(item.get('snippet'), list):
                    snippet_text = self._extract_text_from_content(item['snippet'])
                else:
                    snippet_text = item.get('snippet') or item.get('content') or item.get('answer') or item.get('text', '')

                normalized_item = {
                    'title': item.get('title') or item.get('name') or self._extract_title_from_text(snippet_text),
                    'snippet': snippet_text,
                    'source': item.get('source') or item.get('url') or item.get('link') or self._extract_source_from_text(snippet_text),
                    'relevance_score': self._calculate_relevance_score(snippet_text)
                }
                
                if normalized_item['snippet']:
                    normalized.append(normalized_item)
        
        return normalized
    
    
    def _is_error_response(self, response: Any) -> bool:
        """Detect Tavily tool error responses so we can fallback cleanly."""
        if not isinstance(response, dict):
            return False
        if response.get('isError'):
            return True
        if isinstance(response.get('content'), list):
            for item in response.get('content', []):
                if isinstance(item, dict) and isinstance(item.get('text'), str) and 'Tavily API error:' in item.get('text'):
                    return True
        return False

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

    def _extract_text_from_content(self, content: Any) -> str:
        """Extract plain text from a content list or string."""
        if isinstance(content, str):
            return content.strip()
        if isinstance(content, list):
            pieces = []
            for segment in content:
                if isinstance(segment, dict):
                    piece = segment.get('text') or segment.get('content')
                    if piece:
                        pieces.append(str(piece).strip())
                elif isinstance(segment, str):
                    pieces.append(segment.strip())
            return '\n'.join([p for p in pieces if p])
        return ''

    def _extract_title_from_text(self, text: str) -> str:
        """Extract a title from raw text if available."""
        for line in text.splitlines():
            if line.strip().startswith('Title:'):
                return line.split('Title:', 1)[1].strip()
        first_line = next((line.strip() for line in text.splitlines() if line.strip()), '')
        return first_line[:120] if first_line else 'Untitled'

    def _extract_source_from_text(self, text: str) -> str:
        """Extract a source URL from raw text if available."""
        for line in text.splitlines():
            if line.strip().startswith('URL:'):
                return line.split('URL:', 1)[1].strip()
        return ''

    def _extract_snippet_from_text(self, text: str) -> str:
        """Extract a snippet from raw text, preferring content after a content marker."""
        if 'Content:' in text:
            parts = text.split('Content:', 1)
            return parts[1].strip()[:800]
        return text.strip()[:800]

    def close(self):
        """Close MCP server connection."""
        if self.process:
            try:
                self.process.terminate()
                self.process.wait(timeout=5)
                logger.info("[OK] Server closed successfully")
            except Exception as e:
                logger.error(f"Error closing server: {e}")
                self.process.kill()


def create_client(timeout: int = 360) -> MCPTavilyClient:
    """
    Factory function to create and initialize MCPTavilyClient.
    
    Args:
        timeout: Timeout in seconds
    
    Returns:
        Initialized MCPTavilyClient instance
    """
    return MCPTavilyClient(timeout=timeout)
