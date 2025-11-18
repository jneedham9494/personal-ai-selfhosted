from fastapi import APIRouter, HTTPException, Query
from typing import Optional
import sys
import logging
sys.path.append('..')
from services.obsidian_service import ObsidianService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize services with updated vault path
import os
obsidian_service = ObsidianService()

router = APIRouter(prefix="/vault", tags=["vault"])

@router.get("/files")
async def list_files():
    """Get list of all markdown files in the vault"""
    result = await obsidian_service.list_all_notes()

    if not result['success']:
        raise HTTPException(status_code=500, detail=result['error'])

    return {
        "files": result['notes'],
        "count": len(result['notes'])
    }

@router.get("/file")
async def get_file(path: str = Query(..., description="Relative path to the file within the vault")):
    """Get content of a specific markdown file"""
    result = await obsidian_service.read_note(path)

    if not result['success']:
        raise HTTPException(status_code=404, detail=result['error'])

    return {
        "path": path,
        "content": result['content']
    }

@router.get("/recent")
async def list_recent(limit: int = Query(10, description="Number of recent files to return")):
    """Get list of recently modified files"""
    result = await obsidian_service.list_recent_notes(limit=limit)

    if not result['success']:
        raise HTTPException(status_code=500, detail=result['error'])

    return {
        "files": result['notes'],
        "count": len(result['notes'])
    }
