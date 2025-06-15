"""Global service provider module"""
from .searchservice import SearchService
from .encryptservice import EncryptService

# Global service instance
_search_service = None
_encrypt_service = None

def get_search_service():
    """Get the global search service instance"""
    global _search_service
    if _search_service is None:
        _search_service = SearchService()
    return _search_service

def get_encrypt_service():
    global _encrypt_service
    if _encrypt_service is None:
        _encrypt_service = EncryptService()
    return _encrypt_service

def set_search_service(service):
    """Set the global search service instance"""
    global _search_service
    _search_service = service

def set_encrypt_service(service):
    global _encrypt_service
    _encrypt_service = service