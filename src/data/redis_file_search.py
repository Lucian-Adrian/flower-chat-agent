"""
File Search Engine with Redis Caching
Provides file content search capabilities with Redis-based caching
"""

import os
import re
import mimetypes
from pathlib import Path
from typing import Dict, List, Optional, Any, Set
import json

from src.utils.utils import setup_logger
from .redis_search_cache import RedisSearchCache, get_search_cache

logger = setup_logger(__name__)


class FileSearchEngine:
    """
    File search engine with Redis caching for improved performance
    Searches through project files and caches results
    """
    
    def __init__(self, base_path: Optional[str] = None, redis_cache: Optional[RedisSearchCache] = None):
        """
        Initialize file search engine
        
        Args:
            base_path: Base directory to search in (defaults to project root)
            redis_cache: Redis cache instance
        """
        self.base_path = Path(base_path) if base_path else Path(__file__).parent.parent.parent
        self.redis_cache = redis_cache or get_search_cache()
        
        # File type filters
        self.searchable_extensions = {
            '.py', '.js', '.ts', '.json', '.yaml', '.yml', '.md', '.txt', 
            '.html', '.css', '.sql', '.sh', '.env', '.cfg', '.ini', '.toml'
        }
        
        # Directories to exclude from search
        self.excluded_dirs = {
            '__pycache__', '.git', '.pytest_cache', 'node_modules', 
            '.env', 'venv', '.venv', 'dist', 'build', '.chroma_db', 
            'chroma_db_flowers', 'chroma_db_simple'
        }
        
        # Maximum file size to search (in bytes)
        self.max_file_size = 1024 * 1024  # 1MB
        
        logger.info(f"File Search Engine initialized with base path: {self.base_path}")
    
    def search_files(self, query: str, file_types: Optional[List[str]] = None, 
                    case_sensitive: bool = False, max_results: int = 50) -> List[Dict[str, Any]]:
        """
        Search for files containing the specified query
        
        Args:
            query: Search query string
            file_types: List of file extensions to search (e.g., ['.py', '.js'])
            case_sensitive: Whether search should be case sensitive
            max_results: Maximum number of results to return
            
        Returns:
            List of search results with file information and matches
        """
        # Check cache first
        cache_filters = {
            'file_types': file_types,
            'case_sensitive': case_sensitive,
            'max_results': max_results
        }
        
        cached_results = self.redis_cache.get_cached_search('files', query, cache_filters)
        if cached_results:
            return cached_results
        
        # Perform file search
        results = self._perform_file_search(query, file_types, case_sensitive, max_results)
        
        # Cache results
        self.redis_cache.cache_search_results('files', query, results, cache_filters, ttl=1800)  # 30 minutes
        
        return results
    
    def _perform_file_search(self, query: str, file_types: Optional[List[str]], 
                           case_sensitive: bool, max_results: int) -> List[Dict[str, Any]]:
        """Perform actual file search without caching"""
        results = []
        search_pattern = query if case_sensitive else query.lower()
        
        # Determine which file types to search
        if file_types:
            extensions_to_search = set(ext.lower() for ext in file_types)
        else:
            extensions_to_search = self.searchable_extensions
        
        try:
            # Walk through directory tree
            for root, dirs, files in os.walk(self.base_path):
                # Filter out excluded directories
                dirs[:] = [d for d in dirs if d not in self.excluded_dirs]
                
                for file in files:
                    file_path = Path(root) / file
                    
                    # Check file extension
                    if file_path.suffix.lower() not in extensions_to_search:
                        continue
                    
                    # Check file size
                    try:
                        if file_path.stat().st_size > self.max_file_size:
                            continue
                    except (OSError, PermissionError):
                        continue
                    
                    # Search in filename
                    filename_match = self._search_in_text(file, search_pattern, case_sensitive)
                    
                    # Search in file content
                    content_matches = self._search_in_file(file_path, search_pattern, case_sensitive)
                    
                    # If we found matches, add to results
                    if filename_match or content_matches:
                        result = {
                            'file_path': str(file_path.relative_to(self.base_path)),
                            'absolute_path': str(file_path),
                            'filename': file,
                            'file_type': file_path.suffix,
                            'file_size': file_path.stat().st_size,
                            'matches': {
                                'filename': filename_match,
                                'content': content_matches
                            },
                            'total_matches': len(content_matches) + (1 if filename_match else 0)
                        }
                        results.append(result)
                        
                        # Check if we've reached max results
                        if len(results) >= max_results:
                            break
                
                # Break outer loop if max results reached
                if len(results) >= max_results:
                    break
        
        except Exception as e:
            logger.error(f"Error during file search: {e}")
        
        # Sort results by relevance (total matches, then by filename matches)
        results.sort(key=lambda x: (x['total_matches'], x['matches']['filename'] is not None), reverse=True)
        
        logger.info(f"File search for '{query}' found {len(results)} results")
        return results
    
    def _search_in_file(self, file_path: Path, search_pattern: str, case_sensitive: bool) -> List[Dict[str, Any]]:
        """Search for pattern within file content"""
        matches = []
        
        try:
            # Determine file encoding
            with open(file_path, 'rb') as f:
                raw_data = f.read(1024)  # Read first 1KB to detect encoding
                
            # Try UTF-8 first, then fallback to other encodings
            encodings = ['utf-8', 'latin-1', 'cp1252']
            content = None
            
            for encoding in encodings:
                try:
                    with open(file_path, 'r', encoding=encoding) as f:
                        content = f.read()
                    break
                except UnicodeDecodeError:
                    continue
            
            if content is None:
                return matches
            
            # Split content into lines for context
            lines = content.split('\n')
            
            # Search each line
            for line_no, line in enumerate(lines, 1):
                line_to_search = line if case_sensitive else line.lower()
                
                if search_pattern in line_to_search:
                    # Find all occurrences in this line
                    start = 0
                    while True:
                        pos = line_to_search.find(search_pattern, start)
                        if pos == -1:
                            break
                        
                        # Get context around the match
                        context_start = max(0, pos - 50)
                        context_end = min(len(line), pos + len(search_pattern) + 50)
                        context = line[context_start:context_end]
                        
                        matches.append({
                            'line_number': line_no,
                            'column': pos + 1,
                            'context': context,
                            'line_content': line.strip()
                        })
                        
                        start = pos + 1
        
        except (OSError, PermissionError, UnicodeDecodeError) as e:
            logger.debug(f"Could not search file {file_path}: {e}")
        
        return matches
    
    def _search_in_text(self, text: str, search_pattern: str, case_sensitive: bool) -> Optional[Dict[str, Any]]:
        """Search for pattern in text (like filename)"""
        text_to_search = text if case_sensitive else text.lower()
        
        if search_pattern in text_to_search:
            pos = text_to_search.find(search_pattern)
            return {
                'position': pos,
                'match_text': text[pos:pos + len(search_pattern)],
                'full_text': text
            }
        
        return None
    
    def search_by_file_type(self, file_extension: str, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get all files of a specific type
        
        Args:
            file_extension: File extension to search for (e.g., '.py')
            limit: Maximum number of files to return
            
        Returns:
            List of file information
        """
        cache_key = f"file_type_{file_extension}"
        cached_results = self.redis_cache.get_cached_search('files', cache_key)
        if cached_results:
            return cached_results[:limit]
        
        results = []
        
        try:
            for root, dirs, files in os.walk(self.base_path):
                # Filter out excluded directories
                dirs[:] = [d for d in dirs if d not in self.excluded_dirs]
                
                for file in files:
                    if file.endswith(file_extension):
                        file_path = Path(root) / file
                        
                        try:
                            file_info = {
                                'file_path': str(file_path.relative_to(self.base_path)),
                                'absolute_path': str(file_path),
                                'filename': file,
                                'file_type': file_extension,
                                'file_size': file_path.stat().st_size,
                                'modified_time': file_path.stat().st_mtime
                            }
                            results.append(file_info)
                            
                            if len(results) >= limit * 2:  # Get more for caching
                                break
                        except (OSError, PermissionError):
                            continue
                
                if len(results) >= limit * 2:
                    break
        
        except Exception as e:
            logger.error(f"Error searching by file type: {e}")
        
        # Cache results
        self.redis_cache.cache_search_results('files', cache_key, results, ttl=3600)  # 1 hour
        
        return results[:limit]
    
    def get_file_info(self, file_path: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a specific file
        
        Args:
            file_path: Path to the file (relative to base_path)
            
        Returns:
            File information dictionary or None if file not found
        """
        try:
            full_path = self.base_path / file_path
            
            if not full_path.exists():
                return None
            
            stat = full_path.stat()
            
            # Try to read file content preview
            content_preview = ""
            line_count = 0
            
            if full_path.suffix.lower() in self.searchable_extensions and stat.st_size <= self.max_file_size:
                try:
                    with open(full_path, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                        line_count = len(lines)
                        # Get first 10 lines as preview
                        content_preview = ''.join(lines[:10])
                except (UnicodeDecodeError, OSError):
                    content_preview = "[Binary or unreadable file]"
            
            return {
                'file_path': file_path,
                'absolute_path': str(full_path),
                'filename': full_path.name,
                'file_type': full_path.suffix,
                'file_size': stat.st_size,
                'line_count': line_count,
                'modified_time': stat.st_mtime,
                'is_readable': full_path.suffix.lower() in self.searchable_extensions,
                'content_preview': content_preview[:500]  # Limit preview size
            }
        
        except Exception as e:
            logger.error(f"Error getting file info for {file_path}: {e}")
            return None
    
    def get_project_structure(self, max_depth: int = 3) -> Dict[str, Any]:
        """
        Get project directory structure
        
        Args:
            max_depth: Maximum directory depth to traverse
            
        Returns:
            Project structure as nested dictionary
        """
        cache_key = f"project_structure_depth_{max_depth}"
        cached_results = self.redis_cache.get_cached_search('files', cache_key)
        if cached_results:
            return cached_results[0] if cached_results else {}
        
        def build_tree(path: Path, current_depth: int) -> Dict[str, Any]:
            if current_depth >= max_depth:
                return {}
            
            tree = {
                'type': 'directory',
                'name': path.name,
                'path': str(path.relative_to(self.base_path)),
                'children': {}
            }
            
            try:
                items = list(path.iterdir())
                items.sort(key=lambda x: (x.is_file(), x.name.lower()))
                
                for item in items:
                    if item.name.startswith('.') or item.name in self.excluded_dirs:
                        continue
                    
                    if item.is_directory():
                        tree['children'][item.name] = build_tree(item, current_depth + 1)
                    else:
                        tree['children'][item.name] = {
                            'type': 'file',
                            'name': item.name,
                            'path': str(item.relative_to(self.base_path)),
                            'size': item.stat().st_size,
                            'extension': item.suffix
                        }
            except (OSError, PermissionError):
                pass
            
            return tree
        
        structure = build_tree(self.base_path, 0)
        
        # Cache the structure
        self.redis_cache.cache_search_results('files', cache_key, [structure], ttl=1800)  # 30 minutes
        
        return structure


# Global instance for easy access
_file_search_engine = None

def get_file_search_engine() -> FileSearchEngine:
    """Get the global file search engine instance"""
    global _file_search_engine
    if _file_search_engine is None:
        _file_search_engine = FileSearchEngine()
    return _file_search_engine


# Convenience functions for direct access
def search_files(query: str, file_types: Optional[List[str]] = None, 
                case_sensitive: bool = False, max_results: int = 50) -> List[Dict[str, Any]]:
    """Search for files containing the specified query"""
    return get_file_search_engine().search_files(query, file_types, case_sensitive, max_results)


def search_by_file_type(file_extension: str, limit: int = 100) -> List[Dict[str, Any]]:
    """Get all files of a specific type"""
    return get_file_search_engine().search_by_file_type(file_extension, limit)


def get_file_info(file_path: str) -> Optional[Dict[str, Any]]:
    """Get detailed information about a specific file"""
    return get_file_search_engine().get_file_info(file_path)


def get_project_structure(max_depth: int = 3) -> Dict[str, Any]:
    """Get project directory structure"""
    return get_file_search_engine().get_project_structure(max_depth)