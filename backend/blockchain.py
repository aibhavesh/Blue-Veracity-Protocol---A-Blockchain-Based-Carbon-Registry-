"""
Blockchain integration using Web3.py
Handles minting and smart contract interactions on Polygon Amoy
"""

import os
import json
import logging
from typing import Tuple, Optional
from web3 import Web3
from eth_account import Account

logger = logging.getLogger(__name__)

# Configuration from environment
POLYGON_AMOY_RPC = os.getenv(
    "POLYGON_AMOY_RPC",
    "https://rpc-amoy.polygon.technology"
)
CONTRACT_ADDRESS = os.getenv("CONTRACT_ADDRESS", "").lower()
BACKEND_WALLET_KEY = os.getenv("BACKEND_WALLET_KEY", "")
CONTRACT_ABI_PATH = os.getenv("CONTRACT_ABI_PATH", "./artifacts/contracts/BlueCarbonCredit.sol/BlueCarbonCredit.json")

# Global Web3 instance
w3 = None
contract = None
backend_account = None


def initialize_blockchain():
    """Initialize Web3 connection and contract instance"""
    global w3, contract, backend_account

    try:
        # Initialize Web3
        w3 = Web3(Web3.HTTPProvider(POLYGON_AMOY_RPC))

        if not w3.is_connected():
            logger.error("❌ Failed to connect to Polygon Amoy RPC")
            return False

        logger.info("✅ Connected to Polygon Amoy")

        # Initialize backend account
        if BACKEND_WALLET_KEY:
            backend_account = Account.from_key(BACKEND_WALLET_KEY)
            logger.info(f"✅ Backend wallet initialized: {backend_account.address}")
        else:
            logger.warning("⚠️  BACKEND_WALLET_KEY not set - minting will fail")

        # Load contract ABI
        try:
            with open(CONTRACT_ABI_PATH, "r") as f:
                contract_data = json.load(f)
                contract_abi = contract_data.get("abi", contract_data)
        except FileNotFoundError:
            logger.warning(
                f"⚠️  Contract ABI file not found at {CONTRACT_ABI_PATH}, using minimal ABI"
            )
            contract_abi = get_minimal_abi()

        # Initialize contract
        if CONTRACT_ADDRESS and CONTRACT_ADDRESS != "":
            contract = w3.eth.contract(
                address=Web3.to_checksum_address(CONTRACT_ADDRESS),
                abi=contract_abi
            )
            logger.info(f"✅ Contract initialized: {CONTRACT_ADDRESS}")
        else:
            logger.warning("⚠️  CONTRACT_ADDRESS not set - contract operations will fail")

        return True

    except Exception as e:
        logger.error(f"❌ Blockchain initialization error: {str(e)}")
        return False


def get_contract_instance():
    """Get initialized contract instance"""
    global contract
    if contract is None:
        initialize_blockchain()
    return contract


def get_w3():
    """Get initialized Web3 instance"""
    global w3
    if w3 is None:
        initialize_blockchain()
    return w3


async def mint_carbon_credit(
    wallet_address: str,
    ipfs_cid: str,
    latitude: int,
    longitude: int,
    credits_amount: str,
    metadata_uri: str = "",
) -> Tuple[Optional[str], Optional[int]]:
    """
    Mint a carbon credit NFT on Polygon Amoy

    Args:
        wallet_address: Recipient wallet address
        ipfs_cid: IPFS content hash of evidence
        latitude: Latitude × 10^6
        longitude: Longitude × 10^6
        credits_amount: Credit amount string
        metadata_uri: IPFS URI of metadata (tokenURI)

    Returns:
        Tuple of (transaction_hash, token_id) or (None, None) if failed
    """
    try:
        web3 = get_w3()
        contract_instance = get_contract_instance()

        if not web3 or not contract_instance or not backend_account:
            logger.error("❌ Blockchain not properly initialized")
            return None, None

        # Convert addresses to checksum
        recipient = Web3.to_checksum_address(wallet_address)
        from_address = backend_account.address

        # Convert latitude/longitude to integers (×10^6)
        lat_int = int(latitude * 1e6)
        long_int = int(longitude * 1e6)

        logger.info(f"🔍 Preparing to mint for {recipient}")
        logger.info(f"   IPFS: {ipfs_cid}")
        logger.info(f"   Location: ({latitude}, {longitude})")
        logger.info(f"   Credits: {credits_amount}")

        # Get nonce
        nonce = web3.eth.get_transaction_count(from_address)

        # Build transaction
        mint_tx = contract_instance.functions.safeMint(
            recipient,
            metadata_uri,
            ipfs_cid,
            lat_int,
            long_int,
            credits_amount,
        ).build_transaction({
            'from': from_address,
            'nonce': nonce,
            'gas': 500000,  # Increased for complex transaction
            'maxFeePerGas': web3.eth.gas_price * 2,
            'maxPriorityFeePerGas': web3.eth.gas_price,
            'chainId': 80002,  # Polygon Amoy chainId
        })

        logger.info(f"⛓️  Estimated gas: {mint_tx['gas']}")

        # Sign transaction
        signed_tx = web3.eth.account.sign_transaction(
            mint_tx,
            private_key=backend_account.key
        )

        logger.info("📝 Signing transaction...")

        # Send transaction
        tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)
        tx_hash_str = tx_hash.hex()

        logger.info(f"📤 Transaction sent: {tx_hash_str}")

        # Wait for receipt
        logger.info("⏳ Waiting for confirmation...")
        receipt = web3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)

        if receipt['status'] == 1:
            logger.info(f"✅ Transaction confirmed in block {receipt['blockNumber']}")

            # Extract token ID from event logs
            token_id = extract_token_id_from_receipt(contract_instance, receipt)

            logger.info(f"✅ NFT minted successfully!")
            logger.info(f"   Token ID: {token_id}")
            logger.info(f"   TX Hash: {tx_hash_str}")

            return tx_hash_str, token_id
        else:
            logger.error(f"❌ Transaction failed in block {receipt['blockNumber']}")
            return None, None

    except Exception as e:
        logger.error(f"❌ Minting error: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return None, None


def extract_token_id_from_receipt(contract_instance, receipt) -> Optional[int]:
    """Extract token ID from transaction receipt logs"""
    try:
        # Get the Transfer event
        transfer_events = contract_instance.events.Transfer().process_receipt(receipt)
        if transfer_events:
            return transfer_events[0]['args']['tokenId']
    except Exception as e:
        logger.warning(f"⚠️  Could not extract token ID from logs: {str(e)}")
    return None


async def verify_credit(token_id: int) -> bool:
    """
    Call the verify() function on contract

    Args:
        token_id: Token ID to verify

    Returns:
        True if successful
    """
    try:
        web3 = get_w3()
        contract_instance = get_contract_instance()

        if not web3 or not contract_instance or not backend_account:
            return False

        nonce = web3.eth.get_transaction_count(backend_account.address)

        verify_tx = contract_instance.functions.verify(token_id).build_transaction({
            'from': backend_account.address,
            'nonce': nonce,
            'gas': 100000,
            'maxFeePerGas': web3.eth.gas_price * 2,
            'maxPriorityFeePerGas': web3.eth.gas_price,
            'chainId': 80002,
        })

        signed_tx = web3.eth.account.sign_transaction(
            verify_tx,
            private_key=backend_account.key
        )

        tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)
        receipt = web3.eth.wait_for_transaction_receipt(tx_hash, timeout=60)

        return receipt['status'] == 1

    except Exception as e:
        logger.error(f"❌ Verification error: {str(e)}")
        return False


def get_minimal_abi():
    """Return minimal ABI for contract"""
    return [
        {
            "inputs": [
                {"internalType": "address", "name": "to", "type": "address"},
                {"internalType": "string", "name": "uri", "type": "string"},
                {"internalType": "string", "name": "ipfsCid", "type": "string"},
                {"internalType": "int256", "name": "lat", "type": "int256"},
                {"internalType": "int256", "name": "long", "type": "int256"},
                {"internalType": "string", "name": "creditsAmount", "type": "string"},
            ],
            "name": "safeMint",
            "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
            "stateMutability": "external",
            "type": "function",
        },
        {
            "inputs": [{"internalType": "uint256", "name": "tokenId", "type": "uint256"}],
            "name": "verify",
            "outputs": [],
            "stateMutability": "external",
            "type": "function",
        },
        {
            "inputs": [{"internalType": "string", "name": "ipfsCid", "type": "string"}],
            "name": "isDuplicateSubmission",
            "outputs": [{"internalType": "bool", "name": "", "type": "bool"}],
            "stateMutability": "view",
            "type": "function",
        },
    ]


# Initialize on module import
initialize_blockchain()
