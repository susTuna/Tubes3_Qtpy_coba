"""Global service provider module"""
from .searchservice import SearchService

# Global service instance
_search_service = None

def get_search_service():
    """Get the global search service instance"""
    global _search_service
    if _search_service is None:
        _search_service = SearchService()
    return _search_service

def set_search_service(service):
    """Set the global search service instance"""
    global _search_service
    _search_service = service