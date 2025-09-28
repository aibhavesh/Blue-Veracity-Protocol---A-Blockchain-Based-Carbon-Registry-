# main.py

import os
import json
import requests
from fastapi import FastAPI, File, Form, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from web3 import Web3
from pydantic import BaseModel

# --- CONFIGURATION ---
# Aapke details jo aapne daale the
PINATA_API_KEY = "ab4d7865401222671bda"
PINATA_API_SECRET = "4fadfd1a16fbe2a97dca6d6dad0762721a4316304214a5b0f9efd8012d313c1f"
POLYGON_MUMBAI_RPC_URL = "https://polygon-amoy.g.alchemy.com/v2/E92vsqVNW2APP7JQbQyDq"
MINTER_WALLET_PRIVATE_KEY = "ac19f2255785055b35615a1a1b5b27b993214736561f38a531f03d518066312a"

# Maine yeh neeche ke do (2) fields aapke liye bhar diye hain
CONTRACT_ADDRESS = "0xc49339a25A625812E694056214841a40a233e64b"
CONTRACT_ABI = [{"inputs": [], "stateMutability": "nonpayable", "type": "constructor"}, {"inputs": [{"internalType": "address", "name": "owner", "type": "address"}], "name": "OwnableInvalidOwner", "type": "error"}, {"inputs": [{"internalType": "address", "name": "account", "type": "address"}], "name": "OwnableUnauthorizedAccount", "type": "error"}, {"anonymous": False, "inputs": [{"indexed": True, "internalType": "address", "name": "owner", "type": "address"}, {"indexed": True, "internalType": "address", "name": "approved", "type": "address"}, {"indexed": True, "internalType": "uint256", "name": "tokenId", "type": "uint256"}], "name": "Approval", "type": "event"}, {"anonymous": False, "inputs": [{"indexed": True, "internalType": "address", "name": "owner", "type": "address"}, {"indexed": True, "internalType": "address", "name": "operator", "type": "address"}, {"indexed": False, "internalType": "bool", "name": "approved", "type": "bool"}], "name": "ApprovalForAll", "type": "event"}, {"anonymous": False, "inputs": [{"indexed": True, "internalType": "address", "name": "previousOwner", "type": "address"}, {"indexed": True, "internalType": "address", "name": "newOwner", "type": "address"}], "name": "OwnershipTransferred", "type": "event"}, {"anonymous": False, "inputs": [{"indexed": True, "internalType": "address", "name": "from", "type": "address"}, {"indexed": True, "internalType": "address", "name": "to", "type": "address"}, {"indexed": True, "internalType": "uint256", "name": "tokenId", "type": "uint256"}], "name": "Transfer", "type": "event"}, {"inputs": [{"internalType": "address", "name": "to", "type": "address"}, {"internalType": "uint256", "name": "tokenId", "type": "uint256"}], "name": "approve", "outputs": [], "stateMutability": "nonpayable", "type": "function"}, {"inputs": [{"internalType": "address", "name": "owner", "type": "address"}], "name": "balanceOf", "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}], "stateMutability": "view", "type": "function"}, {"inputs": [{"internalType": "uint256", "name": "tokenId", "type": "uint256"}], "name": "getApproved", "outputs": [{"internalType": "address", "name": "", "type": "address"}], "stateMutability": "view", "type": "function"}, {"inputs": [{"internalType": "address", "name": "owner", "type": "address"}, {"internalType": "address", "name": "operator", "type": "address"}], "name": "isApprovedForAll", "outputs": [{"internalType": "bool", "name": "", "type": "bool"}], "stateMutability": "view", "type": "function"}, {"inputs": [], "name": "name", "outputs": [{"internalType": "string", "name": "", "type": "string"}], "stateMutability": "view", "type": "function"}, {"inputs": [], "name": "owner", "outputs": [{"internalType": "address", "name": "", "type": "address"}], "stateMutability": "view", "type": "function"}, {"inputs": [{"internalType": "uint256", "name": "tokenId", "type": "uint256"}], "name": "ownerOf", "outputs": [{"internalType": "address", "name": "", "type": "address"}], "stateMutability": "view", "type": "function"}, {"inputs": [], "name": "renounceOwnership", "outputs": [], "stateMutability": "nonpayable", "type": "function"}, {"inputs": [{"internalType": "address", "name": "to", "type": "address"}, {"internalType": "string", "name": "ipfsHash", "type": "string"}], "name": "safeMint", "outputs": [], "stateMutability": "nonpayable", "type": "function"}, {"inputs": [{"internalType": "address", "name": "from", "type": "address"}, {"internalType": "address", "name": "to", "type": "address"}, {"internalType": "uint256", "name": "tokenId", "type": "uint256"}], "name": "safeTransferFrom", "outputs": [], "stateMutability": "nonpayable", "type": "function"}, {"inputs": [{"internalType": "address", "name": "from", "type": "address"}, {"internalType": "address", "name": "to", "type": "address"}, {"internalType": "uint256", "name": "tokenId", "type": "uint256"}, {"internalType": "bytes", "name": "data", "type": "bytes"}], "name": "safeTransferFrom", "outputs": [], "stateMutability": "nonpayable", "type": "function"}, {"inputs": [{"internalType": "address", "name": "operator", "type": "address"}, {"internalType": "bool", "name": "approved", "type": "bool"}], "name": "setApprovalForAll", "outputs": [], "stateMutability": "nonpayable", "type": "function"}, {"inputs": [{"internalType": "bytes4", "name": "interfaceId", "type": "bytes4"}], "name": "supportsInterface", "outputs": [{"internalType": "bool", "name": "", "type": "bool"}], "stateMutability": "view", "type": "function"}, {"inputs": [], "name": "symbol", "outputs": [{"internalType": "string", "name": "", "type": "string"}], "stateMutability": "view", "type": "function"}, {"inputs": [{"internalType": "uint256", "name": "tokenId", "type": "uint256"}], "name": "tokenURI", "outputs": [{"internalType": "string", "name": "", "type": "string"}], "stateMutability": "view", "type": "function"}, {"inputs": [{"internalType": "address", "name": "from", "type": "address"}, {"internalType": "address", "name": "to", "type": "address"}, {"internalType": "uint256", "name": "tokenId", "type": "uint256"}], "name": "transferFrom", "outputs": [], "stateMutability": "nonpayable", "type": "function"}, {"inputs": [{"internalType": "address", "name": "newOwner", "type": "address"}], "name": "transferOwnership", "outputs": [], "stateMutability": "nonpayable", "type": "function"}]

# --- END CONFIGURATION ---


# Initialize FastAPI app
app = FastAPI(title="Blue Veracity Protocol API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory "database"
db = {}
submission_counter = 0

# Setup Web3
w3 = Web3(Web3.HTTPProvider(POLYGON_MUMBAI_RPC_URL))
minter_account = w3.eth.account.from_key(MINTER_WALLET_PRIVATE_KEY)
contract = w3.eth.contract(address=Web3.to_checksum_address(CONTRACT_ADDRESS), abi=CONTRACT_ABI)


# --- API Endpoints ---
@app.get("/")
def read_root():
    return {"message": "Blue Veracity Protocol API is running"}

@app.post("/submit_evidence")
async def submit_evidence(
    file: UploadFile = File(...),
    latitude: float = Form(...),
    longitude: float = Form(...),
    walletAddress: str = Form(...)
):
    global submission_counter
    
    files = {'file': (file.filename, await file.read(), file.content_type)}
    headers = {'pinata_api_key': PINATA_API_KEY, 'pinata_secret_api_key': PINATA_API_SECRET}

    try:
        response = requests.post("https://api.pinata.cloud/pinning/pinFileToIPFS", files=files, headers=headers)
        response.raise_for_status()
        image_ipfs_hash = response.json()['IpfsHash']
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload to IPFS: {e}")

    submission_counter += 1
    db[submission_counter] = {
        "id": submission_counter,
        "walletAddress": walletAddress,
        "latitude": latitude,
        "longitude": longitude,
        "ipfsHash": image_ipfs_hash,
        "status": "pending",
        "txHash": None
    }
    
    print(f"New submission received: {db[submission_counter]}")
    return {"message": "Submission received, awaiting verification.", "submissionId": submission_counter, "ipfsHash": image_ipfs_hash}


@app.get("/get_pending_submissions")
async def get_pending_submissions():
    pending = [sub for sub in db.values() if sub['status'] == 'pending']
    return pending


class MintRequest(BaseModel):
    submissionId: int
    verifierAddress: str

@app.post("/trigger_minting")
async def trigger_minting(request: MintRequest):
    submission = db.get(request.submissionId)

    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found.")
    if submission['status'] != 'pending':
        raise HTTPException(status_code=400, detail="Submission has already been processed.")

    try:
        nonce = w3.eth.get_transaction_count(minter_account.address)
        tx = contract.functions.safeMint(
            Web3.to_checksum_address(submission['walletAddress']),
            submission['ipfsHash']
        ).build_transaction({
            'from': minter_account.address,
            'nonce': nonce,
            'gas': 300000,
            'gasPrice': w3.eth.gas_price
        })

        signed_tx = w3.eth.account.sign_transaction(tx, private_key=minter_account.key)
        # YEH LINE SAHI HAI
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        w3.eth.wait_for_transaction_receipt(tx_hash)

        submission['status'] = 'approved'
        submission['txHash'] = tx_hash.hex()
        
        print(f"Minting successful for submission {request.submissionId}. Tx: {tx_hash.hex()}")
        return {"message": "Minting successful!", "transactionHash": tx_hash.hex()}

    except Exception as e:
        print(f"Error during minting for submission {request.submissionId}: {e}")
        raise HTTPException(status_code=500, detail=f"An error occurred during the minting process: {e}")