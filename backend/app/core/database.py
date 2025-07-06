"""
Database connection and utilities for Cloudflare D1.
Handles database operations, connection management, and query execution.
"""

import httpx
import json
from typing import Dict, List, Optional, Any, Union
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class CloudflareD1Client:
    """Cloudflare D1 database client for REST API operations."""
    
    def __init__(self):
        self.account_id = settings.cloudflare_account_id
        self.database_id = settings.cloudflare_d1_database_id
        self.api_token = settings.cloudflare_api_token
        self.base_url = f"https://api.cloudflare.com/client/v4/accounts/{self.account_id}/d1/database/{self.database_id}"
        self.headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }
    
    async def execute_query(self, query: str, params: Optional[List[Any]] = None) -> Dict[str, Any]:
        """Execute a SQL query and return results."""
        try:
            payload = {
                "sql": query,
                "params": params or []
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/query",
                    headers=self.headers,
                    json=payload,
                    timeout=30.0
                )
                
                if response.status_code != 200:
                    logger.error(f"D1 Query failed: {response.status_code} - {response.text}")
                    raise Exception(f"Database query failed: {response.status_code}")
                
                result = response.json()
                if not result.get("success", False):
                    logger.error(f"D1 Query error: {result.get('errors', [])}")
                    raise Exception(f"Database query error: {result.get('errors', [])}")
                
                return result.get("result", [])[0] if result.get("result") else {}
                
        except Exception as e:
            logger.error(f"Database query error: {str(e)}")
            raise
    
    async def execute_query_many(self, queries: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Execute multiple SQL queries in a transaction."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/query",
                    headers=self.headers,
                    json=queries,
                    timeout=30.0
                )
                
                if response.status_code != 200:
                    logger.error(f"D1 Batch query failed: {response.status_code} - {response.text}")
                    raise Exception(f"Database batch query failed: {response.status_code}")
                
                result = response.json()
                if not result.get("success", False):
                    logger.error(f"D1 Batch query error: {result.get('errors', [])}")
                    raise Exception(f"Database batch query error: {result.get('errors', [])}")
                
                return result.get("result", [])
                
        except Exception as e:
            logger.error(f"Database batch query error: {str(e)}")
            raise


class DatabaseManager:
    """Database manager for handling common database operations."""
    
    def __init__(self):
        self.client = CloudflareD1Client()
    
    async def get_by_id(self, table: str, id: int) -> Optional[Dict[str, Any]]:
        """Get a single record by ID."""
        query = f"SELECT * FROM {table} WHERE id = ? LIMIT 1"
        result = await self.client.execute_query(query, [id])
        return result.get("results", [None])[0] if result.get("results") else None
    
    async def get_all(self, table: str, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """Get all records with pagination."""
        query = f"SELECT * FROM {table} LIMIT ? OFFSET ?"
        result = await self.client.execute_query(query, [limit, offset])
        return result.get("results", [])
    
    async def get_by_field(self, table: str, field: str, value: Any) -> List[Dict[str, Any]]:
        """Get records by a specific field value."""
        query = f"SELECT * FROM {table} WHERE {field} = ?"
        result = await self.client.execute_query(query, [value])
        return result.get("results", [])
    
    async def get_by_field_single(self, table: str, field: str, value: Any) -> Optional[Dict[str, Any]]:
        """Get a single record by field value."""
        query = f"SELECT * FROM {table} WHERE {field} = ? LIMIT 1"
        result = await self.client.execute_query(query, [value])
        return result.get("results", [None])[0] if result.get("results") else None
    
    async def create(self, table: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create a new record."""
        fields = list(data.keys())
        placeholders = ["?" for _ in fields]
        values = list(data.values())
        
        query = f"INSERT INTO {table} ({', '.join(fields)}) VALUES ({', '.join(placeholders)}) RETURNING *"
        result = await self.client.execute_query(query, values)
        return result.get("results", [None])[0] if result.get("results") else None
    
    async def update(self, table: str, id: int, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update a record by ID."""
        fields = list(data.keys())
        set_clause = ", ".join([f"{field} = ?" for field in fields])
        values = list(data.values()) + [id]
        
        query = f"UPDATE {table} SET {set_clause} WHERE id = ? RETURNING *"
        result = await self.client.execute_query(query, values)
        return result.get("results", [None])[0] if result.get("results") else None
    
    async def delete(self, table: str, id: int) -> bool:
        """Delete a record by ID."""
        query = f"DELETE FROM {table} WHERE id = ?"
        result = await self.client.execute_query(query, [id])
        return result.get("meta", {}).get("changes", 0) > 0
    
    async def count(self, table: str, where_clause: str = "", params: Optional[List[Any]] = None) -> int:
        """Count records in a table."""
        query = f"SELECT COUNT(*) as count FROM {table}"
        if where_clause:
            query += f" WHERE {where_clause}"
        
        result = await self.client.execute_query(query, params or [])
        return result.get("results", [{}])[0].get("count", 0)
    
    async def search(self, table: str, search_fields: List[str], search_term: str, 
                    limit: int = 20, offset: int = 0) -> List[Dict[str, Any]]:
        """Search records across multiple fields."""
        if not search_fields or not search_term:
            return []
        
        # Create search conditions
        search_conditions = []
        search_params = []
        
        for field in search_fields:
            search_conditions.append(f"{field} LIKE ?")
            search_params.append(f"%{search_term}%")
        
        where_clause = " OR ".join(search_conditions)
        search_params.extend([limit, offset])
        
        query = f"SELECT * FROM {table} WHERE {where_clause} LIMIT ? OFFSET ?"
        result = await self.client.execute_query(query, search_params)
        return result.get("results", [])


# Global database manager instance
db_manager = DatabaseManager() 