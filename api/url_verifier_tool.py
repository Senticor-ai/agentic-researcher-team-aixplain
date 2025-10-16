"""
URL Verification Tool

This module provides a Python function tool for verifying URLs are valid and accessible.
Can be registered with aixplain SDK for use by agents.
"""
import logging
import re
from typing import List, Dict, Any
from urllib.parse import urlparse
import requests
from requests.exceptions import RequestException, Timeout

logger = logging.getLogger(__name__)


class URLVerifier:
    """
    Verifies URLs are valid and accessible
    """
    
    # Timeout for HTTP requests (seconds)
    REQUEST_TIMEOUT = 5
    
    # Invalid URL patterns
    INVALID_PATTERNS = [
        r'example\.com',
        r'placeholder',
        r'test\.com',
        r'localhost',
        r'127\.0\.0\.1',
        r'dummy',
        r'fake',
    ]
    
    @staticmethod
    def is_valid_format(url: str) -> tuple[bool, str]:
        """
        Check if URL has valid format
        
        Args:
            url: URL string to validate
            
        Returns:
            Tuple of (is_valid, issue_message)
        """
        if not url or not isinstance(url, str):
            return False, "URL is empty or not a string"
        
        url_lower = url.lower()
        
        # Check URL structure first
        try:
            parsed = urlparse(url)
            if not parsed.scheme:
                return False, "URL missing scheme (http/https)"
            if not parsed.netloc:
                return False, "URL missing domain"
            if parsed.scheme not in ['http', 'https']:
                return False, f"Invalid URL scheme: {parsed.scheme} (must be http or https)"
        except Exception as e:
            return False, f"Error parsing URL: {str(e)}"
        
        # Check for invalid patterns after structure validation
        for pattern in URLVerifier.INVALID_PATTERNS:
            if re.search(pattern, url_lower):
                return False, f"URL contains invalid pattern: {pattern}"
        
        return True, ""
    
    @staticmethod
    def check_accessibility(url: str) -> tuple[bool, int, str]:
        """
        Check if URL is accessible via HTTP HEAD request
        
        Args:
            url: URL string to check
            
        Returns:
            Tuple of (is_accessible, status_code, issue_message)
        """
        try:
            # Use HEAD request to minimize data transfer
            response = requests.head(
                url,
                timeout=URLVerifier.REQUEST_TIMEOUT,
                allow_redirects=True,
                headers={'User-Agent': 'Mozilla/5.0 (compatible; URLVerifier/1.0)'}
            )
            
            status_code = response.status_code
            
            # Success status codes (2xx and 3xx)
            if 200 <= status_code < 400:
                return True, status_code, ""
            else:
                return False, status_code, f"HTTP status {status_code}"
                
        except Timeout:
            return False, 0, f"Request timeout after {URLVerifier.REQUEST_TIMEOUT}s"
        except RequestException as e:
            return False, 0, f"Request failed: {str(e)}"
        except Exception as e:
            return False, 0, f"Unexpected error: {str(e)}"
    
    @staticmethod
    def verify_url(url: str) -> Dict[str, Any]:
        """
        Verify a single URL (format and accessibility)
        
        Args:
            url: URL string to verify
            
        Returns:
            {
                "url": str,
                "valid": bool,
                "accessible": bool,
                "status_code": int,
                "issue": str (if any)
            }
        """
        result = {
            "url": url,
            "valid": False,
            "accessible": False,
            "status_code": 0,
            "issue": ""
        }
        
        # Check format first
        is_valid_format, format_issue = URLVerifier.is_valid_format(url)
        if not is_valid_format:
            result["issue"] = format_issue
            logger.warning(f"URL format invalid: {url} - {format_issue}")
            return result
        
        result["valid"] = True
        
        # Check accessibility
        is_accessible, status_code, access_issue = URLVerifier.check_accessibility(url)
        result["accessible"] = is_accessible
        result["status_code"] = status_code
        
        if not is_accessible:
            result["issue"] = access_issue
            logger.warning(f"URL not accessible: {url} - {access_issue}")
        else:
            logger.info(f"URL verified: {url} (status {status_code})")
        
        return result
    
    @staticmethod
    def verify_urls(urls: List[str]) -> Dict[str, Any]:
        """
        Verify multiple URLs
        
        Args:
            urls: List of URL strings to verify
            
        Returns:
            {
                "total_urls": int,
                "valid_urls": int,
                "accessible_urls": int,
                "invalid_urls": int,
                "inaccessible_urls": int,
                "results": [
                    {
                        "url": str,
                        "valid": bool,
                        "accessible": bool,
                        "status_code": int,
                        "issue": str (if any)
                    }
                ]
            }
        """
        results = []
        valid_count = 0
        accessible_count = 0
        
        for url in urls:
            result = URLVerifier.verify_url(url)
            results.append(result)
            
            if result["valid"]:
                valid_count += 1
            if result["accessible"]:
                accessible_count += 1
        
        total = len(urls)
        invalid_count = total - valid_count
        inaccessible_count = valid_count - accessible_count
        
        summary = {
            "total_urls": total,
            "valid_urls": valid_count,
            "accessible_urls": accessible_count,
            "invalid_urls": invalid_count,
            "inaccessible_urls": inaccessible_count,
            "results": results
        }
        
        logger.info(
            f"URL verification complete: {accessible_count}/{total} accessible, "
            f"{valid_count}/{total} valid format"
        )
        
        return summary


def verify_urls(urls: list[str]) -> dict:
    """
    Verify URLs (accepts list - for Python use)
    
    Args:
        urls: List of URLs to verify
        
    Returns:
        Verification result dictionary
    """
    return URLVerifier.verify_urls(urls)


def verify_urls_json(urls_json: str) -> str:
    """
    Verify URLs (accepts JSON string - for aixplain tool registration)
    
    This function accepts a JSON string and returns a JSON string,
    making it compatible with aixplain utility model registration.
    
    Args:
        urls_json: JSON string representing array of URLs to verify
        
    Returns:
        JSON string with verification results
        
    Example:
        >>> urls_json = '["https://example.com", "https://google.com"]'
        >>> result_json = verify_urls_json(urls_json)
        >>> result = json.loads(result_json)
        >>> print(result['total_urls'])
        2
    """
    import json
    
    try:
        # Parse input JSON
        urls = json.loads(urls_json)
        
        # Validate input is a list
        if not isinstance(urls, list):
            raise ValueError("Input must be a JSON array of URLs")
        
        # Verify URLs
        result = URLVerifier.verify_urls(urls)
        
        # Return as JSON string
        return json.dumps(result)
        
    except json.JSONDecodeError as e:
        # Return error as JSON
        error_result = {
            "total_urls": 0,
            "valid_urls": 0,
            "accessible_urls": 0,
            "invalid_urls": 0,
            "inaccessible_urls": 0,
            "results": [],
            "error": f"Invalid JSON input: {str(e)}"
        }
        return json.dumps(error_result)
    except Exception as e:
        # Return error as JSON
        error_result = {
            "total_urls": 0,
            "valid_urls": 0,
            "accessible_urls": 0,
            "invalid_urls": 0,
            "inaccessible_urls": 0,
            "results": [],
            "error": f"Verification error: {str(e)}"
        }
        return json.dumps(error_result)
