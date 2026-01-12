"""
Blue Veracity Protocol - FastAPI Backend
Trusted Oracle between Field Data and Blockchain
"""

from fastapi import FastAPI, File, UploadFile, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import logging
from datetime import datetime

from models import (
    CarbonCreditSubmission,
    SubmissionResponse,
    PendingSubmission,
    VerificationResponse,
)
from database import init_db, SessionLocal
from ipfs import upload_to_pinata
from blockchain import mint_carbon_credit, get_contract_instance

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Blue Veracity Protocol Backend",
    description="Blockchain-based blue carbon credit registry",
    version="1.0.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    """Initialize database and verify blockchain connection"""
    try:
        init_db()
        logger.info("✅ Database initialized")

        contract = get_contract_instance()
        if contract:
            logger.info("✅ Smart contract connection verified")
        else:
            logger.error("❌ Failed to connect to smart contract")
    except Exception as e:
        logger.error(f"❌ Startup error: {str(e)}")


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "Blue Veracity Protocol Backend",
    }


@app.post("/submit", response_model=SubmissionResponse)
async def submit_carbon_credit(
    file: UploadFile = File(...),
    latitude: float = Query(..., ge=-90, le=90),
    longitude: float = Query(..., ge=-180, le=180),
    wallet_address: str = Query(...),
    credits_amount: float = Query(..., gt=0),
):
    """
    Submit a carbon credit for verification

    **Parameters:**
    - `file`: Image evidence (geotagged)
    - `latitude`: GPS latitude (-90 to 90)
    - `longitude`: GPS longitude (-180 to 180)
    - `wallet_address`: Field user's blockchain wallet
    - `credits_amount`: Metric tons of CO2e
    """
    db = SessionLocal()

    try:
        logger.info(
            f"📸 New submission from {wallet_address} at ({latitude}, {longitude})"
        )

        if not file.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="File must be an image")

        file_content = await file.read()
        if len(file_content) == 0:
            raise HTTPException(status_code=400, detail="File is empty")

        logger.info("📤 Uploading to IPFS...")
        ipfs_hash = await upload_to_pinata(
            file_content=file_content,
            file_name=file.filename,
            latitude=latitude,
            longitude=longitude,
        )

        if not ipfs_hash:
            raise HTTPException(status_code=500, detail="IPFS upload failed")

        from database import CarbonCreditDB

        existing = (
            db.query(CarbonCreditDB)
            .filter(CarbonCreditDB.ipfs_hash == ipfs_hash)
            .first()
        )
        if existing:
            logger.warning(f"⚠️  Duplicate IPFS hash detected: {ipfs_hash}")
            raise HTTPException(
                status_code=400,
                detail="This evidence has already been submitted",
            )

        submission = CarbonCreditSubmission(
            wallet_address=wallet_address,
            latitude=latitude,
            longitude=longitude,
            ipfs_hash=ipfs_hash,
            credits_amount=credits_amount,
            file_name=file.filename,
        )

        db_record = submission.to_db_model()
        db.add(db_record)
        db.commit()
        db.refresh(db_record)

        logger.info(
            f"✅ Submission saved: {db_record.id} | IPFS: {ipfs_hash[:12]}..."
        )

        return SubmissionResponse(
            submission_id=str(db_record.id),
            status="PENDING",
            ipfs_hash=ipfs_hash,
            message="Submission received. Awaiting verification.",
            timestamp=db_record.created_at.isoformat(),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Submission error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Submission failed: {str(e)}")
    finally:
        db.close()


@app.get("/pending")
async def get_pending_submissions(limit: int = Query(10, ge=1, le=100)):
    """Get unverified carbon credit submissions"""
    db = SessionLocal()

    try:
        from database import CarbonCreditDB

        pending = (
            db.query(CarbonCreditDB)
            .filter(CarbonCreditDB.status == "PENDING")
            .order_by(CarbonCreditDB.created_at.desc())
            .limit(limit)
            .all()
        )

        submissions = [
            PendingSubmission(
                submission_id=str(sub.id),
                wallet_address=sub.wallet_address,
                latitude=sub.latitude,
                longitude=sub.longitude,
                ipfs_hash=sub.ipfs_hash,
                credits_amount=sub.credits_amount,
                file_name=sub.file_name,
                created_at=sub.created_at.isoformat(),
            )
            for sub in pending
        ]

        logger.info(f"📋 Retrieved {len(submissions)} pending submissions")

        return {
            "count": len(submissions),
            "submissions": submissions,
        }

    except Exception as e:
        logger.error(f"❌ Error fetching pending submissions: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()


@app.post("/approve/{submission_id}", response_model=VerificationResponse)
async def approve_and_mint(submission_id: str):
    """Verify and mint a carbon credit NFT"""
    db = SessionLocal()

    try:
        from database import CarbonCreditDB
        import json

        submission = db.query(CarbonCreditDB).filter_by(id=submission_id).first()
        if not submission:
            logger.warning(f"⚠️  Submission not found: {submission_id}")
            raise HTTPException(status_code=404, detail="Submission not found")

        if submission.status != "PENDING":
            raise HTTPException(
                status_code=400, detail=f"Submission is already {submission.status}"
            )

        logger.info(f"🔍 Approving submission: {submission_id}")

        contract = get_contract_instance()
        if contract.functions.isDuplicateSubmission(
            submission.ipfs_hash
        ).call():
            logger.error(f"❌ IPFS hash already minted: {submission.ipfs_hash}")
            raise HTTPException(
                status_code=400, detail="Carbon credit already minted on-chain"
            )

        metadata = {
            "name": f"Blue Carbon Credit #{submission_id}",
            "description": f"Verified blue carbon credit: {submission.credits_amount} metric tons CO2e",
            "image": f"ipfs://{submission.ipfs_hash}",
            "attributes": [
                {"trait_type": "Latitude", "value": submission.latitude},
                {"trait_type": "Longitude", "value": submission.longitude},
                {"trait_type": "Carbon Credits (tCO2e)", "value": str(submission.credits_amount)},
                {"trait_type": "Verification Date", "value": datetime.utcnow().isoformat()},
            ],
        }

        logger.info("📤 Uploading metadata to IPFS...")
        metadata_json = json.dumps(metadata).encode()
        metadata_hash = await upload_to_pinata(
            file_content=metadata_json,
            file_name=f"metadata-{submission_id}.json",
        )

        if not metadata_hash:
            raise HTTPException(status_code=500, detail="Metadata upload failed")

        logger.info("⛓️  Minting NFT on blockchain...")
        tx_hash, token_id = await mint_carbon_credit(
            wallet_address=submission.wallet_address,
            ipfs_cid=submission.ipfs_hash,
            latitude=submission.latitude,
            longitude=submission.longitude,
            credits_amount=str(submission.credits_amount),
            metadata_uri=f"ipfs://{metadata_hash}",
        )

        if not tx_hash:
            raise HTTPException(status_code=500, detail="NFT minting failed")

        submission.status = "VERIFIED"
        submission.transaction_hash = tx_hash
        submission.token_id = token_id
        submission.metadata_hash = metadata_hash
        submission.verified_at = datetime.utcnow()

        db.commit()

        logger.info(
            f"✅ NFT minted! Token ID: {token_id} | TX: {tx_hash[:12]}..."
        )

        return VerificationResponse(
            submission_id=submission_id,
            status="VERIFIED",
            transaction_hash=tx_hash,
            token_id=token_id,
            nft_uri=f"ipfs://{metadata_hash}",
            message="Carbon credit verified and minted as NFT",
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Approval error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Approval failed: {str(e)}")
    finally:
        db.close()


@app.get("/submission/{submission_id}")
async def get_submission_status(submission_id: str):
    """Get submission status and details"""
    db = SessionLocal()

    try:
        from database import CarbonCreditDB

        submission = db.query(CarbonCreditDB).filter_by(id=submission_id).first()
        if not submission:
            raise HTTPException(status_code=404, detail="Submission not found")

        return {
            "submission_id": str(submission.id),
            "status": submission.status,
            "wallet_address": submission.wallet_address,
            "ipfs_hash": submission.ipfs_hash,
            "latitude": submission.latitude,
            "longitude": submission.longitude,
            "credits_amount": submission.credits_amount,
            "transaction_hash": submission.transaction_hash,
            "token_id": submission.token_id,
            "created_at": submission.created_at.isoformat(),
            "verified_at": submission.verified_at.isoformat() if submission.verified_at else None,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error fetching submission: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()


@app.get("/stats")
async def get_stats():
    """Get platform statistics"""
    db = SessionLocal()

    try:
        from database import CarbonCreditDB
        from sqlalchemy import func

        total = db.query(func.count(CarbonCreditDB.id)).scalar()
        pending = (
            db.query(func.count(CarbonCreditDB.id))
            .filter(CarbonCreditDB.status == "PENDING")
            .scalar()
        )
        verified = (
            db.query(func.count(CarbonCreditDB.id))
            .filter(CarbonCreditDB.status == "VERIFIED")
            .scalar()
        )
        total_credits = (
            db.query(func.sum(CarbonCreditDB.credits_amount))
            .filter(CarbonCreditDB.status == "VERIFIED")
            .scalar()
        )

        return {
            "total_submissions": total,
            "pending": pending,
            "verified": verified,
            "total_credits_minted": float(total_credits or 0),
            "timestamp": datetime.utcnow().isoformat(),
        }

    except Exception as e:
        logger.error(f"❌ Error fetching stats: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
