# Security Best Practices

This document outlines the security measures implemented in the Blue Veracity Protocol and recommendations for production deployment.

## Backend Security

### 1. CORS Configuration
- **Status**: ✅ Fixed
- **Change**: Replaced wildcard (`*`) CORS with environment-based whitelist
- **Configuration**: Set `ALLOWED_ORIGINS` in `.env` file
- **Example**: `ALLOWED_ORIGINS=https://yourdomain.com,https://app.yourdomain.com`

### 2. Input Validation
- **Status**: ✅ Fixed
- **Changes**:
  - Wallet addresses: Validated with regex pattern `^0x[a-fA-F0-9]{40}$`
  - File uploads: Limited to 10MB max size
  - GPS coordinates: Range validated (-90 to 90, -180 to 180)
  - Credits amount: Must be greater than 0

### 3. Database Security
- **Status**: ⚠️ Requires Manual Setup
- **Current**: SQLite (development only)
- **Production Recommendation**: PostgreSQL with connection pooling
- **Migration**: Update `DATABASE_URL` in `.env` to PostgreSQL connection string

### 4. Transaction Safety
- **Status**: ✅ Fixed
- **Change**: Added database rollback on blockchain transaction failures
- **Protection**: Prevents inconsistent state between database and blockchain

## Smart Contract Security

### 1. Access Control
- **Status**: ✅ Secure
- **Implementation**: OpenZeppelin AccessControl
- **Roles**:
  - `DEFAULT_ADMIN_ROLE`: Contract deployer
  - `MINTER_ROLE`: Backend wallet
  - `VERIFIER_ROLE`: Verifier wallet (optional)

### 2. Duplicate Prevention
- **Status**: ✅ Secure
- **Protection**: IPFS hash mapping prevents double-minting
- **Check**: `isDuplicateSubmission()` function

### 3. Version Pinning
- **Status**: ✅ Fixed
- **Change**: Updated pragma from `^0.8.20` to `~0.8.20`
- **Benefit**: Prevents breaking changes from minor version updates

## Mobile App Security

### 1. API Configuration
- **Status**: ✅ Fixed
- **Change**: Removed hardcoded localhost URLs
- **Configuration**: Use `config.js` with environment variables
- **Setup**: Set `API_BASE_URL` in environment

### 2. Wallet Validation
- **Status**: ✅ Fixed
- **Validation**: Address length (42 chars) and format (0x prefix)

## Deployment Checklist

### Pre-Production
- [ ] Generate strong private keys (never commit to git)
- [ ] Set up PostgreSQL database
- [ ] Configure CORS whitelist in `.env`
- [ ] Set API rate limiting (use nginx or API gateway)
- [ ] Enable HTTPS only (no HTTP)
- [ ] Set up monitoring and alerting

### Secrets Management
- [ ] Store private keys in secure vault (AWS Secrets Manager, Azure Key Vault, etc.)
- [ ] Rotate API keys regularly (Pinata, RPC endpoints)
- [ ] Use separate keys for development and production
- [ ] Never log or expose private keys

### Smart Contract
- [ ] Verify contract on Polygonscan
- [ ] Grant MINTER_ROLE only to backend wallet
- [ ] Revoke unnecessary admin privileges
- [ ] Test on testnet before mainnet deployment

### Backend
- [ ] Set `ALLOWED_ORIGINS` to production domains only
- [ ] Use production-grade database (PostgreSQL)
- [ ] Enable database connection pooling
- [ ] Configure rate limiting middleware
- [ ] Set up logging and monitoring
- [ ] Use secure random for session tokens

### Frontend/Mobile
- [ ] Update `API_BASE_URL` to production endpoint
- [ ] Enable SSL certificate pinning (optional, advanced)
- [ ] Implement proper error handling
- [ ] Add user authentication (if needed)

## Known Limitations

### 1. Authentication
- **Status**: ⚠️ Not Implemented
- **Impact**: `/approve` endpoint has no authentication
- **Recommendation**: Add JWT or API key authentication before production
- **Implementation**: Use FastAPI dependency for auth middleware

### 2. Rate Limiting
- **Status**: ⚠️ Not Implemented
- **Impact**: API vulnerable to abuse
- **Recommendation**: Use `slowapi` or nginx rate limiting
- **Example**: Limit to 10 requests/minute per IP

### 3. File Type Validation
- **Status**: ✅ Basic (MIME type check)
- **Recommendation**: Add deeper file validation (check magic bytes)
- **Library**: Use `python-magic` for robust file type detection

### 4. Geolocation Validation
- **Status**: ⚠️ Range Only
- **Current**: Only validates lat/lng ranges
- **Recommendation**: Add reverse geocoding to verify location authenticity
- **Service**: Use Google Maps or OpenStreetMap API

## Monitoring Recommendations

### Application Metrics
- Request rate per endpoint
- Error rate and types
- Response times (p50, p95, p99)
- Database query performance

### Blockchain Metrics
- Transaction success rate
- Gas usage and costs
- Pending transaction queue
- Failed mints (log reasons)

### Security Metrics
- Failed authentication attempts
- Unusual request patterns
- File upload sizes
- IPFS upload failures

## Incident Response

### If Private Key Compromised
1. Immediately revoke MINTER_ROLE from compromised wallet
2. Generate new backend wallet
3. Grant MINTER_ROLE to new wallet
4. Update backend `.env` with new key
5. Audit all recent transactions from compromised wallet

### If Database Compromised
1. Take database offline
2. Restore from backup
3. Rotate all API keys
4. Check blockchain for any unauthorized mints
5. Notify affected users

### If IPFS Credentials Compromised
1. Revoke Pinata API keys
2. Generate new keys
3. Update backend `.env`
4. Audit recent IPFS uploads
5. Remove any malicious content

## Security Audit Checklist

- [x] CORS configured with whitelist
- [x] Input validation on all endpoints
- [x] Transaction rollback on failures
- [x] Private key management documented
- [x] Environment variable examples provided
- [x] .gitignore excludes secrets
- [ ] Authentication on admin endpoints (TODO)
- [ ] Rate limiting implemented (TODO)
- [ ] File magic byte validation (TODO)
- [ ] Geolocation verification (TODO)

## Contact

For security issues, please report via GitHub Security Advisories.
Do not disclose security vulnerabilities publicly.
