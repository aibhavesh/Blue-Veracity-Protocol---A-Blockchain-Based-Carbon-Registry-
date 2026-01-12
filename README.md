# Blue Veracity Protocol
## Blockchain-Based Blue Carbon Credit Registry

A full-stack Web3 system for registering, verifying, and minting carbon credit NFTs on the Polygon blockchain.

---

## 🏗️ Architecture Overview

```
┌─────────────────┐
│  Mobile App     │  (React Native/Expo)
│  - Camera       │  - GPS Capture
│  - MetaMask     │  - Submit Evidence
└────────┬────────┘
         │ HTTPS/API
         ▼
┌─────────────────────┐
│  FastAPI Backend    │  Trusted Oracle
│  - /submit          │  - IPFS Upload
│  - /pending         │  - Smart Contract Calls
│  - /approve         │  - Database
└────────┬────────────┘
         │              ┌──────────────────┐
         ├─────────────→│  Pinata IPFS     │
         │              │  (Evidence Store)│
         │              └──────────────────┘
         │
         ▼
┌──────────────────────────────┐
│  Polygon Amoy Testnet        │
│  BlueCarbonCredit (ERC-721)  │
│  - Minting NFTs              │
│  - GeoTagged Records         │
│  - Access Control            │
└──────────────────────────────┘
         ▲
         │ Web3.js/Ethers
         │
┌─────────────────────┐
│  Verifier Dashboard │  (React)
│  - Pending List     │  - Approve & Mint
│  - IPFS Preview     │  - Track NFTs
└─────────────────────┘
```

---

## 🗂️ Project Structure

```
blue-veracity-protocol/
│
├── smart-contract/
│   ├── contracts/
│   │   └── BlueCarbonCredit.sol      (ERC-721 with geotagging)
│   ├── scripts/
│   │   └── deploy.js                 (Deployment script)
│   ├── hardhat.config.js
│   ├── package.json
│   └── .env.example
│
├── backend/
│   ├── main.py                       (FastAPI app)
│   ├── models.py                     (Pydantic schemas)
│   ├── database.py                   (SQLAlchemy ORM)
│   ├── ipfs.py                       (Pinata integration)
│   ├── blockchain.py                 (Web3.py integration)
│   ├── requirements.txt
│   └── .env.example
│
├── mobile-app/
│   ├── App.js                        (Entry point)
│   ├── screens/
│   │   ├── CaptureScreen.js          (Camera + GPS)
│   │   ├── SubmitScreen.js           (Wallet + Submit)
│   │   └── StatusScreen.js           (Track submission)
│   ├── package.json
│   ├── app.json
│   └── .env.example
│
├── verifier-dashboard/
│   ├── src/
│   │   ├── App.js                    (Main app)
│   │   ├── App.css
│   │   ├── components/
│   │   │   ├── PendingList.js        (Submissions list)
│   │   │   ├── PendingList.css
│   │   │   ├── ApproveButton.js      (Mint NFT)
│   │   │   └── ApproveButton.css
│   │   └── index.js
│   ├── package.json
│   └── public/
│
└── README.md
```

---

## 🚀 Quick Start

### 1. Smart Contract Deployment

```bash
cd smart-contract

# Install dependencies
npm install

# Create .env from example
cp .env.example .env

# Fill in your Polygon Amoy details
# PRIVATE_KEY=0x...
# BACKEND_WALLET=0x...
# VERIFIER_WALLET=0x...

# Compile
npm run compile

# Deploy to Polygon Amoy
npm run deploy

# Note the contract address
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env from example
cp .env.example .env

# Configure:
# - POLYGON_AMOY_RPC
# - CONTRACT_ADDRESS (from deployment)
# - BACKEND_WALLET_KEY
# - PINATA_API_KEY
# - PINATA_API_SECRET

# Run server
python main.py
# API available at http://localhost:8000
# Docs at http://localhost:8000/docs
```

### 3. Mobile App Setup

```bash
cd mobile-app

# Install dependencies
npm install
# or
yarn install

# Create .env from example
cp .env.example .env

# Start Expo
npm start
# Use Expo Go app on your phone to scan QR code
```

### 4. Verifier Dashboard Setup

```bash
cd verifier-dashboard

# Install dependencies
npm install

# Start development server
npm start
# Opens at http://localhost:3000
```

---

## 🔌 API Endpoints

### Health Check
```
GET /health
```
Returns service status and timestamp.

### Submit Carbon Credit
```
POST /submit
Content-Type: multipart/form-data

Parameters:
- file: Image evidence (required)
- latitude: float (-90 to 90, required)
- longitude: float (-180 to 180, required)
- wallet_address: string (0x..., required)
- credits_amount: float (> 0, required)

Response:
{
  "submission_id": "uuid",
  "status": "PENDING",
  "ipfs_hash": "QmXxxx",
  "message": "Submission received...",
  "timestamp": "2024-01-12T..."
}
```

### Get Pending Submissions
```
GET /pending?limit=10

Response:
{
  "count": 5,
  "submissions": [
    {
      "submission_id": "uuid",
      "wallet_address": "0x...",
      "latitude": 19.0760,
      "longitude": 72.8777,
      "ipfs_hash": "QmXxxx",
      "credits_amount": 2.5,
      "file_name": "photo.jpg",
      "created_at": "2024-01-12T..."
    }
  ]
}
```

### Approve & Mint NFT
```
POST /approve/{submission_id}

Response:
{
  "submission_id": "uuid",
  "status": "VERIFIED",
  "transaction_hash": "0x...",
  "token_id": 1,
  "nft_uri": "ipfs://QmXxxx",
  "message": "Carbon credit verified..."
}
```

### Get Submission Status
```
GET /submission/{submission_id}

Response:
{
  "submission_id": "uuid",
  "status": "VERIFIED",
  "wallet_address": "0x...",
  "ipfs_hash": "QmXxxx",
  "latitude": 19.0760,
  "longitude": 72.8777,
  "credits_amount": 2.5,
  "transaction_hash": "0x...",
  "token_id": 1,
  "metadata_hash": "QmXxxx",
  "created_at": "2024-01-12T...",
  "verified_at": "2024-01-12T..."
}
```

### Get Statistics
```
GET /stats

Response:
{
  "total_submissions": 42,
  "pending": 5,
  "verified": 37,
  "total_credits_minted": 128.5,
  "timestamp": "2024-01-12T..."
}
```

---

## 🔐 Security Features

### Smart Contract
- **AccessControl**: MINTER_ROLE restricts who can mint
- **Duplicate Prevention**: IPFS hash → tokenId mapping prevents double-minting
- **Geotagging**: Immutable location data on-chain
- **Metadata Validation**: All evidence linked via IPFS

### Backend
- **Private Key Separation**: Backend wallet ≠ deployer wallet
- **Pinata Integration**: Decentralized evidence storage
- **Database Validation**: SQL injection protection via SQLAlchemy
- **CORS Configuration**: Restrict cross-origin requests

### Mobile
- **MetaMask Integration**: Cryptographic wallet signing
- **GPS Verification**: Location-based evidence collection
- **HTTPS Only**: Encrypted API communication

---

## 📡 Polygon Amoy Configuration

| Parameter | Value |
|-----------|-------|
| Chain ID | 80002 |
| RPC URL | https://rpc-amoy.polygon.technology |
| Currency | MATIC |
| Block Time | ~2 seconds |
| Gas Token | MATIC |

### Testnet Faucet
Get test MATIC: https://faucet.polygon.technology/

---

## 🗄️ Database Schema

### CarbonCreditDB Table

```sql
CREATE TABLE carbon_credits (
  id UUID PRIMARY KEY,
  wallet_address VARCHAR NOT NULL,
  latitude FLOAT NOT NULL,
  longitude FLOAT NOT NULL,
  ipfs_hash VARCHAR UNIQUE NOT NULL,
  credits_amount FLOAT NOT NULL,
  file_name VARCHAR NOT NULL,
  status VARCHAR DEFAULT 'PENDING',
  transaction_hash VARCHAR UNIQUE,
  token_id INTEGER UNIQUE,
  metadata_hash VARCHAR,
  created_at DATETIME DEFAULT NOW(),
  verified_at DATETIME,
  
  INDEX(wallet_address),
  INDEX(status),
  INDEX(created_at)
);
```

---

## 🧪 Testing

### Test Smart Contract
```bash
cd smart-contract
npm run test
```

### Test Backend API
```bash
cd backend
pytest tests/
```

### Verify Deployment
```bash
curl http://localhost:8000/health
```

---

## 📊 Workflow Example

### Field User (Mobile App)
1. Opens app → Capture Screen
2. Takes geotagged photo with camera
3. Enters wallet address (MetaMask)
4. Specifies carbon credits (2.5 tCO2e)
5. Submits to backend
6. Receives submission ID
7. Views status via Status Screen

### Verifier (Dashboard)
1. Logs into dashboard
2. Connects MetaMask wallet
3. Reviews pending submissions
4. Examines IPFS evidence image
5. Verifies location, credits, authenticity
6. Clicks "Approve & Mint NFT"
7. Approves MetaMask transaction
8. NFT minted on Polygon Amoy
9. Field user receives NFT in wallet

### Smart Contract
- Verifier calls `safeMint()`
- Contract mints ERC-721 token
- Metadata stored with IPFS hash
- Geolocation data embedded
- Duplicate hash check prevents fraud
- Event emitted for off-chain tracking

---

## 🚨 Error Handling

### Common Errors

**"IPFS upload failed"**
- Check Pinata API credentials
- Verify PINATA_API_KEY and PINATA_API_SECRET

**"Smart contract connection failed"**
- Verify CONTRACT_ADDRESS is correct
- Check POLYGON_AMOY_RPC is accessible
- Ensure contract is deployed

**"Insufficient gas"**
- Increase gas limit in blockchain.py
- Request more MATIC from faucet

**"MINTER_ROLE not granted"**
- Run deploy script with BACKEND_WALLET set
- Or manually grant role via etherscan

---

## 📱 Supported Platforms

| Component | Platform | Version |
|-----------|----------|---------|
| Smart Contract | Ethereum/Polygon | Solidity 0.8.20 |
| Backend | Linux/macOS/Windows | Python 3.9+ |
| Mobile App | iOS/Android | Expo 50+ |
| Dashboard | Web | React 18+ |

---

## 🔧 Configuration Files

### .env Template (Backend)
```env
POLYGON_AMOY_RPC=https://rpc-amoy.polygon.technology
CONTRACT_ADDRESS=0x...
BACKEND_WALLET_KEY=0x...
PINATA_API_KEY=...
PINATA_API_SECRET=...
DATABASE_URL=sqlite:///./blue_veracity.db
```

### .env Template (Smart Contract)
```env
PRIVATE_KEY=0x...
BACKEND_WALLET=0x...
VERIFIER_WALLET=0x...
POLYGONSCAN_API_KEY=...
```

---

## 📚 Dependencies

### Smart Contract
- OpenZeppelin Contracts v5.4.0
- Hardhat v2.22.6
- Ethers v6.11

### Backend
- FastAPI v0.104.1
- Web3.py v6.11.2
- SQLAlchemy v2.0.23
- Aiohttp v3.9.1

### Mobile
- Expo v50.0
- Expo Camera v14.1
- Expo Location v16.5
- React Navigation v6.1

### Dashboard
- React v18.2
- Ethers v6.15

---

## 🌍 Environmental Impact

**BlueCarbon Context:**
- Blue carbon = carbon captured by coastal/marine ecosystems
- Mangroves, seagrass, salt marshes
- Prevents deforestation monitoring fraud
- Each NFT = verified carbon credit from IPFS-stored evidence

**Fraud Prevention:**
- ✅ Geotagged photos prevent location spoofing
- ✅ IPFS hash deduplication prevents double-minting
- ✅ Immutable blockchain records
- ✅ Verifier approval required before minting
- ✅ AccessControl roles prevent unauthorized minting

---

## 📄 License

MIT License - See LICENSE file

---

## 👥 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

---

## 📞 Support

- **Smart Contract Issues**: Check artifacts for ABI mismatches
- **IPFS Errors**: Verify Pinata API credentials
- **Blockchain Issues**: Check gas, nonce, and balance
- **API Issues**: Check FastAPI logs and database connection

---

## 🎯 Future Enhancements

- [ ] Batch minting for multiple submissions
- [ ] Marketplace for carbon credit trading
- [ ] Governance DAO for verifier voting
- [ ] Multi-signature wallet verification
- [ ] Off-chain data indexing (The Graph)
- [ ] NFT metadata IPFS auto-pinning
- [ ] Mobile app offline mode

---

**Built with ❤️ for climate action using Blockchain technology**
