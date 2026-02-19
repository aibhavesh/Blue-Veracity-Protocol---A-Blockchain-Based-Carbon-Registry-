"""
IPFS integration via Pinata Cloud
"""

import aiohttp
import json
import os
import logging
from datetime import datetime
from typing import Optional

logger = logging.getLogger(__name__)

# Pinata configuration
PINATA_API_KEY = os.getenv("PINATA_API_KEY", "")
PINATA_API_SECRET = os.getenv("PINATA_API_SECRET", "")
PINATA_API_URL = "https://api.pinata.cloud"


async def upload_to_pinata(
    file_content: bytes,
    file_name: str,
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
) -> Optional[str]:
    """
    Upload file to IPFS via Pinata Cloud

    Args:
        file_content: File bytes
        file_name: Original filename
        latitude: Optional GPS latitude
        longitude: Optional GPS longitude

    Returns:
        IPFS hash (CID) or None if failed
    """
    if not PINATA_API_KEY or not PINATA_API_SECRET:
        logger.error("❌ Pinata API credentials not configured")
        return None

    try:
        headers = {
            "pinata_api_key": PINATA_API_KEY,
            "pinata_secret_api_key": PINATA_API_SECRET,
        }

        # Prepare metadata
        metadata = {
            "name": file_name,
            "keyvalues": {
                "timestamp": datetime.utcnow().isoformat(),
            }
        }

        # Add geotags if provided
        if latitude is not None and longitude is not None:
            metadata["keyvalues"]["latitude"] = str(latitude)
            metadata["keyvalues"]["longitude"] = str(longitude)

        # Prepare multipart form data
        form_data = aiohttp.FormData()
        form_data.add_field(
            "file",
            file_content,
            filename=file_name,
        )
        form_data.add_field(
            "pinataMetadata",
            json.dumps(metadata),
            content_type="application/json",
        )

        # Upload to Pinata
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{PINATA_API_URL}/pinning/pinFileToIPFS",
                data=form_data,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=30),
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    ipfs_hash = data.get("IpfsHash")
                    logger.info(f"✅ Uploaded to IPFS: {ipfs_hash}")
                    return ipfs_hash
                else:
                    error_text = await response.text()
                    logger.error(
                        f"❌ Pinata upload failed (status {response.status}): {error_text}"
                    )
                    return None

    except Exception as e:
        logger.error(f"❌ IPFS upload error: {str(e)}")
        return None


async def pin_json_to_ipfs(data: dict, name: str) -> Optional[str]:
    """
    Upload JSON data to IPFS via Pinata

    Args:
        data: Dictionary to upload
        name: Name for the pinned content

    Returns:
        IPFS hash (CID) or None if failed
    """
    if not PINATA_API_KEY or not PINATA_API_SECRET:
        logger.error("❌ Pinata API credentials not configured")
        return None

    try:
        headers = {
            "pinata_api_key": PINATA_API_KEY,
            "pinata_secret_api_key": PINATA_API_SECRET,
            "Content-Type": "application/json",
        }

        payload = {
            "pinataContent": data,
            "pinataMetadata": {
                "name": name,
                "keyvalues": {
                    "timestamp": datetime.utcnow().isoformat(),
                    "type": "metadata",
                }
            },
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{PINATA_API_URL}/pinning/pinJSONToIPFS",
                json=payload,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=30),
            ) as response:
                if response.status == 200:
                    data_response = await response.json()
                    ipfs_hash = data_response.get("IpfsHash")
                    logger.info(f"✅ JSON pinned to IPFS: {ipfs_hash}")
                    return ipfs_hash
                else:
                    error_text = await response.text()
                    logger.error(
                        f"❌ Pinata JSON upload failed (status {response.status}): {error_text}"
                    )
                    return None

    except Exception as e:
        logger.error(f"❌ IPFS JSON upload error: {str(e)}")
        return None
