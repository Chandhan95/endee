"""Endee Vector Database Client"""

import requests
from typing import Optional, List, Dict, Any
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import logging

logger = logging.getLogger(__name__)


class EndeeClient:
    """Client for interacting with Endee vector database"""
    
    def __init__(
        self,
        base_url: str = "http://localhost:8080",
        auth_token: Optional[str] = None,
        timeout: int = 30
    ):
        """
        Initialize Endee client
        
        Args:
            base_url: Base URL of Endee server
            auth_token: Optional authentication token
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip("/")
        self.auth_token = auth_token
        self.timeout = timeout
        
        # Setup session with retries
        self.session = requests.Session()
        retries = Retry(
            total=3,
            backoff_factor=0.5,
            status_forcelist=(500, 502, 503, 504)
        )
        adapter = HTTPAdapter(max_retries=retries)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # Setup headers
        self.headers = {"Content-Type": "application/json"}
        if auth_token:
            self.headers["Authorization"] = auth_token
    
    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Make HTTP request to Endee API"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = self.session.request(
                method=method,
                url=url,
                json=data,
                headers=self.headers,
                timeout=self.timeout,
                **kwargs
            )
            response.raise_for_status()
            return response.json() if response.text else {}
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {str(e)}")
            raise
    
    def health_check(self) -> bool:
        """Check if Endee server is healthy"""
        try:
            response = self.session.get(
                f"{self.base_url}/api/v1/health",
                headers=self.headers,
                timeout=5
            )
            return response.status_code == 200
        except:
            return False
    
    def create_index(
        self,
        name: str,
        dimension: int,
        metric: str = "L2"
    ) -> None:
        """
        Create a new index
        
        Args:
            name: Index name
            dimension: Vector dimension
            metric: Distance metric (L2, cosine, dot)
        """
        logger.info(f"Creating index '{name}' with dimension {dimension}")
        
        try:
            self._make_request(
                "POST",
                "/api/v1/index/create",
                data={
                    "name": name,
                    "dimension": dimension,
                    "metric": metric
                }
            )
            logger.info(f"Index '{name}' created successfully")
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 409:
                logger.info(f"Index '{name}' already exists")
            else:
                raise
    
    def list_indices(self) -> List[str]:
        """List all available indices"""
        response = self._make_request("GET", "/api/v1/index/list")
        return response.get("indices", [])
    
    def delete_index(self, name: str) -> None:
        """Delete an index"""
        logger.info(f"Deleting index '{name}'")
        self._make_request("DELETE", f"/api/v1/index/{name}")
    
    def insert(
        self,
        index_name: str,
        vectors: List[Dict[str, Any]]
    ) -> None:
        """
        Insert vectors into an index
        
        Args:
            index_name: Target index name
            vectors: List of vector objects with 'id', 'values', and optional 'metadata'
        """
        logger.info(f"Inserting {len(vectors)} vectors into '{index_name}'")
        
        payload = {
            "vectors": [
                {
                    "id": v["id"],
                    "values": v["values"],
                    **({"metadata": v["metadata"]} if "metadata" in v else {})
                }
                for v in vectors
            ]
        }
        
        self._make_request(
            "POST",
            f"/api/v1/index/{index_name}/insert",
            data=payload
        )
    
    def search(
        self,
        index_name: str,
        query_vector: List[float],
        k: int = 5,
        filter_: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for similar vectors
        
        Args:
            index_name: Index to search
            query_vector: Query vector
            k: Number of results to return
            filter_: Optional metadata filter
            
        Returns:
            List of search results
        """
        payload = {
            "query": query_vector,
            "k": k
        }
        
        if filter_:
            payload["filter"] = filter_
        
        response = self._make_request(
            "POST",
            f"/api/v1/index/{index_name}/search",
            data=payload
        )
        
        return response.get("results", [])
    
    def get_vector(self, index_name: str, vector_id: str) -> Optional[Dict[str, Any]]:
        """Get a vector by ID"""
        try:
            response = self._make_request(
                "GET",
                f"/api/v1/index/{index_name}/vector/{vector_id}"
            )
            return response.get("vector")
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                return None
            raise
    
    def delete_vector(self, index_name: str, vector_id: str) -> None:
        """Delete a vector"""
        self._make_request(
            "DELETE",
            f"/api/v1/index/{index_name}/vector/{vector_id}"
        )
    
    def get_index_stats(self, index_name: str) -> Dict[str, Any]:
        """Get index statistics"""
        response = self._make_request(
            "GET",
            f"/api/v1/index/{index_name}/stats"
        )
        return response
