#!/usr/bin/env python3
"""
Google Drive MCP Tools
======================

MCP tools for Google Drive integration with OAuth2 authentication.

Provides file access, upload, download, search, and management capabilities
for Google Drive. Supports configuration via Streamlit secrets or environment variables.

Created: 2025-10-10
Sprint: US-RAG-001 Enhancement
"""

import logging
import os
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path

# MCP Tool Integration
try:
    from utils.mcp.mcp_tool import mcp_tool, AccessLevel, ToolCategory
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False

# Google API imports
try:
    from google.oauth2.credentials import Credentials
    from google.oauth2 import service_account
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
    import google.auth
    GOOGLE_API_AVAILABLE = True
except ImportError:
    GOOGLE_API_AVAILABLE = False

logger = logging.getLogger(__name__)

# Global Google Drive service instance
_drive_service = None
_credentials = None


# ============================================================================
# Configuration and Authentication
# ============================================================================

def get_google_credentials() -> Optional[Any]:
    """
    Get Google API credentials from various sources.
    
    Priority:
    1. Streamlit secrets
    2. Environment variables
    3. Service account file
    4. User OAuth flow
    """
    global _credentials
    
    if _credentials:
        return _credentials
    
    try:
        # Try Streamlit secrets
        try:
            import streamlit as st
            if hasattr(st, 'secrets') and 'google' in st.secrets:
                secrets = st.secrets['google']
                _credentials = create_credentials_from_dict(secrets)
                logger.info("✅ Loaded Google credentials from Streamlit secrets")
                return _credentials
        except:
            pass
        
        # Try environment variables
        if os.getenv('GOOGLE_APPLICATION_CREDENTIALS'):
            creds_file = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
            _credentials = service_account.Credentials.from_service_account_file(
                creds_file,
                scopes=['https://www.googleapis.com/auth/drive']
            )
            logger.info(f"✅ Loaded Google credentials from service account: {creds_file}")
            return _credentials
        
        # Try default credentials
        try:
            _credentials, _ = google.auth.default(
                scopes=['https://www.googleapis.com/auth/drive']
            )
            logger.info("✅ Loaded Google default credentials")
            return _credentials
        except:
            pass
        
        logger.warning("⚠️ No Google credentials found. Configure via:")
        logger.warning("   1. Streamlit secrets (.streamlit/secrets.toml)")
        logger.warning("   2. GOOGLE_APPLICATION_CREDENTIALS env var")
        logger.warning("   3. gcloud auth application-default login")
        return None
        
    except Exception as e:
        logger.error(f"Failed to load Google credentials: {e}")
        return None


def create_credentials_from_dict(secrets: Dict) -> Any:
    """Create credentials from Streamlit secrets dictionary."""
    if 'service_account' in secrets:
        # Service account credentials
        return service_account.Credentials.from_service_account_info(
            secrets['service_account'],
            scopes=['https://www.googleapis.com/auth/drive']
        )
    elif 'client_id' in secrets and 'client_secret' in secrets:
        # OAuth2 credentials
        return Credentials(
            token=secrets.get('token'),
            refresh_token=secrets.get('refresh_token'),
            token_uri="https://oauth2.googleapis.com/token",
            client_id=secrets['client_id'],
            client_secret=secrets['client_secret'],
            scopes=['https://www.googleapis.com/auth/drive']
        )
    else:
        raise ValueError("Invalid Google credentials format in secrets")


def get_drive_service():
    """Get or create Google Drive service instance."""
    global _drive_service
    
    if _drive_service:
        return _drive_service
    
    if not GOOGLE_API_AVAILABLE:
        return None
    
    credentials = get_google_credentials()
    if not credentials:
        return None
    
    try:
        _drive_service = build('drive', 'v3', credentials=credentials)
        logger.info("✅ Google Drive service initialized")
        return _drive_service
    except Exception as e:
        logger.error(f"Failed to initialize Drive service: {e}")
        return None


# ============================================================================
# MCP Tools - Google Drive
# ============================================================================

if MCP_AVAILABLE:
    
    @mcp_tool(
        "gdrive.list_files",
        "List files and folders in Google Drive",
        AccessLevel.RESTRICTED,
        ToolCategory.CLOUD_STORAGE
    )
    def gdrive_list_files_mcp(
        query: str = "",
        max_results: int = 100,
        folder_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        List files and folders in Google Drive.
        
        Args:
            query: Search query (e.g., "name contains 'report'")
            max_results: Maximum number of results
            folder_id: Optional folder ID to search in
            
        Returns:
            List of files with metadata
        """
        if not GOOGLE_API_AVAILABLE:
            return {
                "error": "Google API not available",
                "message": "Install: pip install google-api-python-client google-auth"
            }
        
        service = get_drive_service()
        if not service:
            return {"error": "Google Drive not configured. Set up credentials."}
        
        try:
            # Build query
            query_parts = []
            if query:
                query_parts.append(query)
            if folder_id:
                query_parts.append(f"'{folder_id}' in parents")
            
            full_query = " and ".join(query_parts) if query_parts else ""
            
            # List files
            results = service.files().list(
                q=full_query,
                pageSize=max_results,
                fields="files(id, name, mimeType, size, createdTime, modifiedTime, webViewLink)"
            ).execute()
            
            files = results.get('files', [])
            
            return {
                "success": True,
                "files": files,
                "total_files": len(files),
                "query": full_query,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to list Drive files: {e}")
            return {"error": str(e)}
    
    
    @mcp_tool(
        "gdrive.search",
        "Search files in Google Drive",
        AccessLevel.RESTRICTED,
        ToolCategory.CLOUD_STORAGE
    )
    def gdrive_search_mcp(
        search_term: str,
        file_type: Optional[str] = None,
        max_results: int = 50
    ) -> Dict[str, Any]:
        """
        Search files in Google Drive.
        
        Args:
            search_term: Search term
            file_type: Optional file type filter (document, spreadsheet, pdf, etc.)
            max_results: Maximum results
            
        Returns:
            Search results
        """
        query_parts = [f"name contains '{search_term}'"]
        
        # Add file type filter
        if file_type:
            mime_types = {
                "document": "application/vnd.google-apps.document",
                "spreadsheet": "application/vnd.google-apps.spreadsheet",
                "presentation": "application/vnd.google-apps.presentation",
                "pdf": "application/pdf",
                "folder": "application/vnd.google-apps.folder"
            }
            mime = mime_types.get(file_type.lower())
            if mime:
                query_parts.append(f"mimeType = '{mime}'")
        
        query = " and ".join(query_parts)
        
        return gdrive_list_files_mcp(query=query, max_results=max_results)
    
    
    @mcp_tool(
        "gdrive.get_file_content",
        "Get file content from Google Drive",
        AccessLevel.RESTRICTED,
        ToolCategory.CLOUD_STORAGE
    )
    def gdrive_get_file_content_mcp(
        file_id: str,
        export_format: str = "text/plain"
    ) -> Dict[str, Any]:
        """
        Get file content from Google Drive.
        
        Args:
            file_id: Google Drive file ID
            export_format: Export format (text/plain, text/html, application/pdf)
            
        Returns:
            File content
        """
        if not GOOGLE_API_AVAILABLE:
            return {"error": "Google API not available"}
        
        service = get_drive_service()
        if not service:
            return {"error": "Google Drive not configured"}
        
        try:
            # Get file metadata
            file = service.files().get(fileId=file_id).execute()
            
            # Export file if it's a Google Doc
            if file['mimeType'].startswith('application/vnd.google-apps'):
                content = service.files().export(
                    fileId=file_id,
                    mimeType=export_format
                ).execute()
            else:
                # Download binary file
                request = service.files().get_media(fileId=file_id)
                content = request.execute()
            
            # Decode if text
            if isinstance(content, bytes):
                try:
                    content = content.decode('utf-8')
                except:
                    content = f"<binary content, {len(content)} bytes>"
            
            return {
                "success": True,
                "file_id": file_id,
                "file_name": file['name'],
                "mime_type": file['mimeType'],
                "content": content,
                "content_length": len(str(content)),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get file content: {e}")
            return {"error": str(e)}
    
    
    @mcp_tool(
        "gdrive.upload_file",
        "Upload file to Google Drive",
        AccessLevel.RESTRICTED,
        ToolCategory.CLOUD_STORAGE
    )
    def gdrive_upload_file_mcp(
        file_path: str,
        folder_id: Optional[str] = None,
        file_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Upload file to Google Drive.
        
        Args:
            file_path: Local file path
            folder_id: Optional folder ID to upload to
            file_name: Optional custom file name
            
        Returns:
            Upload result with file ID
        """
        if not GOOGLE_API_AVAILABLE:
            return {"error": "Google API not available"}
        
        service = get_drive_service()
        if not service:
            return {"error": "Google Drive not configured"}
        
        try:
            path = Path(file_path)
            if not path.exists():
                return {"error": f"File not found: {file_path}"}
            
            # File metadata
            file_metadata = {
                'name': file_name or path.name
            }
            if folder_id:
                file_metadata['parents'] = [folder_id]
            
            # Upload file
            media = MediaFileUpload(str(path), resumable=True)
            file = service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id, name, webViewLink'
            ).execute()
            
            return {
                "success": True,
                "file_id": file['id'],
                "file_name": file['name'],
                "web_link": file.get('webViewLink'),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to upload file: {e}")
            return {"error": str(e)}
    
    
    @mcp_tool(
        "gdrive.create_folder",
        "Create folder in Google Drive",
        AccessLevel.RESTRICTED,
        ToolCategory.CLOUD_STORAGE
    )
    def gdrive_create_folder_mcp(
        folder_name: str,
        parent_folder_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create folder in Google Drive.
        
        Args:
            folder_name: Folder name
            parent_folder_id: Optional parent folder ID
            
        Returns:
            Created folder info
        """
        if not GOOGLE_API_AVAILABLE:
            return {"error": "Google API not available"}
        
        service = get_drive_service()
        if not service:
            return {"error": "Google Drive not configured"}
        
        try:
            folder_metadata = {
                'name': folder_name,
                'mimeType': 'application/vnd.google-apps.folder'
            }
            if parent_folder_id:
                folder_metadata['parents'] = [parent_folder_id]
            
            folder = service.files().create(
                body=folder_metadata,
                fields='id, name, webViewLink'
            ).execute()
            
            return {
                "success": True,
                "folder_id": folder['id'],
                "folder_name": folder['name'],
                "web_link": folder.get('webViewLink'),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to create folder: {e}")
            return {"error": str(e)}
    
    
    @mcp_tool(
        "gdrive.get_status",
        "Get Google Drive connection status",
        AccessLevel.UNRESTRICTED,
        ToolCategory.CLOUD_STORAGE
    )
    def gdrive_get_status_mcp() -> Dict[str, Any]:
        """
        Get Google Drive configuration status.
        
        Returns:
            Connection status and configuration info
        """
        status = {
            "google_api_available": GOOGLE_API_AVAILABLE,
            "credentials_configured": False,
            "drive_service_ready": False,
            "configuration_methods": [
                "Streamlit secrets (.streamlit/secrets.toml)",
                "Service account file (GOOGLE_APPLICATION_CREDENTIALS)",
                "gcloud auth application-default login"
            ]
        }
        
        if GOOGLE_API_AVAILABLE:
            credentials = get_google_credentials()
            status["credentials_configured"] = credentials is not None
            
            if credentials:
                service = get_drive_service()
                status["drive_service_ready"] = service is not None
        
        return status


if __name__ == "__main__":
    # Test Google Drive tools
    print("🧪 Testing Google Drive MCP Tools\n")
    
    # Test status
    print("1. Testing gdrive.get_status...")
    result = gdrive_get_status_mcp()
    print(f"   API available: {result.get('google_api_available')}")
    print(f"   Credentials configured: {result.get('credentials_configured')}")
    
    # Test list files (if configured)
    if result.get('drive_service_ready'):
        print("\n2. Testing gdrive.list_files...")
        result = gdrive_list_files_mcp(max_results=10)
        print(f"   Result: {result.get('success', False)}")
        if result.get('success'):
            print(f"   Found: {result.get('total_files', 0)} files")
    else:
        print("\n⚠️ Google Drive not configured - skipping file tests")
    
    print("\n✅ Google Drive MCP tools test complete!")

