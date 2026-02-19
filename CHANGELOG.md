# Changelog

All notable changes to the Blue Veracity Protocol project will be documented in this file.

## [Unreleased] - 2024-02-19

### Security Fixes 🔐

#### Critical
- Fixed overly permissive CORS configuration (changed from `["*"]` to environment-based whitelist)
- Added wallet address validation with regex pattern `^0x[a-fA-F0-9]{40}$`
- Added maximum file upload size limit (10MB)
- Fixed duplicate main() function call in deploy script that could cause double execution
- Fixed unsafe UUID generation using `__import__()` in database model

#### High Priority
- Added transaction rollback on database update failures after blockchain minting
- Removed hardcoded localhost URLs from mobile app (now uses environment config)
- Fixed blockchain initialization to validate configuration before connecting
- Added proper error handling for IPFS upload failures

### Code Quality Improvements 🧹

#### Import and Dependency Management
- Fixed unsafe `__import__('datetime')` usage in ipfs.py (now properly imported)
- Fixed unsafe `__import__('uuid')` usage in database.py (now properly imported)
- Removed console.warn from mobile app error handling

#### Configuration Management
- Created `.env.example` files for all components (backend, mobile-app, smart-contract)
- Added `config.js` for mobile app with environment variable support
- Updated `.gitignore` to exclude `.env` files but allow `.env.example`
- Added database file exclusions (*.db, *.db-journal) to .gitignore
- Added proper node_modules and build artifact exclusions

#### Smart Contract
- Changed Solidity pragma from `^0.8.20` to `~0.8.20` for better version control
- Added comprehensive security documentation

### Documentation 📚

#### New Files
- Added `SECURITY.md` with comprehensive security best practices
- Added `CHANGELOG.md` (this file)
- Created `.env.example` files for all components

#### Updated
- Enhanced backend environment configuration with ALLOWED_ORIGINS
- Documented all security fixes and improvements

### Backend Changes

#### main.py
- Added `os` import for environment variable handling
- Configured CORS with environment-based whitelist (`ALLOWED_ORIGINS`)
- Added wallet address regex validation: `^0x[a-fA-F0-9]{40}$`
- Added file size limit: 10MB maximum
- Added explicit blockchain initialization on startup
- Added database rollback on blockchain transaction failures
- Improved error handling with try-except-finally blocks

#### blockchain.py
- Added `validate_config()` function for startup validation
- Improved configuration validation for CONTRACT_ADDRESS and BACKEND_WALLET_KEY
- Removed automatic module-level initialization (now explicit)
- Added better error messages for missing configuration

#### database.py
- Added proper `uuid` import
- Fixed UUID generation from lambda with `__import__()` to proper import
- Added database file exclusion patterns

#### ipfs.py
- Added proper `datetime` import
- Fixed `__import__('datetime')` usage in metadata generation
- Improved code readability

### Mobile App Changes

#### config.js (New File)
- Added centralized configuration with environment variable support
- Exports `API_BASE_URL` from environment or defaults to localhost

#### screens/SubmitScreen.js
- Imported and used `config.js` for API base URL
- Enhanced wallet address validation (42 characters + 0x prefix)
- Replaced hardcoded `http://localhost:8000` with `config.apiBaseUrl`

#### screens/StatusScreen.js
- Imported and used `config.js` for API base URL
- Replaced hardcoded `http://localhost:8000` with `config.apiBaseUrl`

#### App.js
- Removed `console.warn` in error handling
- Set `setIsReady(true)` on error to avoid blocking UI

### Smart Contract Changes

#### BlueCarbonCredit.sol
- Changed pragma from `pragma solidity ^0.8.20;` to `pragma solidity ~0.8.20;`
- Prevents breaking changes from minor compiler version updates

#### scripts/deploy.js
- Removed duplicate `main()` function call (was called twice)
- Kept single error handling block

### Gitignore Updates

- Excluded `.env` files but allowed `.env.example`
- Added `backend/*.db` and `backend/*.db-journal` exclusions
- Added `mobile-app/node_modules/` exclusion
- Added `smart-contract/cache/`, `smart-contract/artifacts/`, `smart-contract/node_modules/` exclusions
- Added `.expo-shared/` exclusion

## Known Issues & TODOs

### Security (Not Implemented Yet)
- [ ] Authentication/authorization on `/approve` endpoint
- [ ] Rate limiting middleware
- [ ] File magic byte validation (beyond MIME type)
- [ ] Geolocation reverse geocoding validation

### Code Quality
- [ ] Add comprehensive test suite
- [ ] Add API request/response logging
- [ ] Implement database connection pooling configuration
- [ ] Add health checks for IPFS/Pinata service

### Documentation
- [ ] Add API usage examples
- [ ] Add deployment guide
- [ ] Add testing guide

## Migration Notes

### For Existing Deployments

1. **Backend Configuration**
   - Add `ALLOWED_ORIGINS` to your `.env` file
   - Update your backend to use the new environment variable pattern
   - Example: `ALLOWED_ORIGINS=https://yourdomain.com,https://app.yourdomain.com`

2. **Mobile App**
   - Create a `.env` file based on `.env.example`
   - Set `API_BASE_URL` to your backend URL
   - Example: `API_BASE_URL=https://api.yourdomain.com`

3. **Smart Contract**
   - Recompile with updated pragma version
   - Test thoroughly on testnet before mainnet deployment

4. **Database**
   - Consider migrating from SQLite to PostgreSQL for production
   - Update `DATABASE_URL` in backend `.env`

## Contributors

Special thanks to all contributors who helped identify and fix these issues.

---

**Note**: This project is under active development. Always review the SECURITY.md file before deploying to production.
