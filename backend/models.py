"""
Pydantic models for Blue Veracity Protocol
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class CarbonCreditSubmission(BaseModel):
    """Input model for carbon credit submission"""

    wallet_address: str = Field(
        ..., description="Field user's blockchain wallet address"
    )
    latitude: float = Field(..., ge=-90, le=90, description="GPS latitude")
    longitude: float = Field(..., ge=-180, le=180, description="GPS longitude")
    ipfs_hash: str = Field(..., description="IPFS content hash of evidence")
    credits_amount: float = Field(..., gt=0, description="Metric tons CO2e")
    file_name: str = Field(..., description="Original filename")

    def to_db_model(self):
        """Convert to database model"""
        from database import CarbonCreditDB

        return CarbonCreditDB(
            wallet_address=self.wallet_address,
            latitude=self.latitude,
            longitude=self.longitude,
            ipfs_hash=self.ipfs_hash,
            credits_amount=self.credits_amount,
            file_name=self.file_name,
            status="PENDING",
        )

    class Config:
        from_attributes = True


class SubmissionResponse(BaseModel):
    """Response model for submission endpoint"""

    submission_id: str = Field(..., description="Unique submission ID")
    status: str = Field(..., description="Submission status (PENDING, VERIFIED, FAILED)")
    ipfs_hash: str = Field(..., description="IPFS content hash")
    message: str = Field(..., description="Confirmation message")
    timestamp: str = Field(..., description="Submission timestamp")

    class Config:
        from_attributes = True


class PendingSubmission(BaseModel):
    """Model for pending submissions list"""

    submission_id: str
    wallet_address: str
    latitude: float
    longitude: float
    ipfs_hash: str
    credits_amount: float
    file_name: str
    created_at: str

    class Config:
        from_attributes = True


class ApprovalRequest(BaseModel):
    """Request model for approval endpoint"""

    submission_id: str = Field(..., description="Submission ID to approve")


class VerificationResponse(BaseModel):
    """Response model for approval/minting"""

    submission_id: str
    status: str = Field(..., description="VERIFIED")
    transaction_hash: str = Field(..., description="On-chain transaction hash")
    token_id: int = Field(..., description="Minted NFT token ID")
    nft_uri: str = Field(..., description="IPFS URI of NFT metadata")
    message: str

    class Config:
        from_attributes = True


class CreditMetadata(BaseModel):
    """On-chain metadata structure"""

    name: str
    description: str
    image: str  # ipfs:// URI
    attributes: list

    class Config:
        from_attributes = True
