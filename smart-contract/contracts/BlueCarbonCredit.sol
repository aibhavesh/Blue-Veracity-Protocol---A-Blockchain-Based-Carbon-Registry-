// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "@openzeppelin/contracts/token/ERC721/extensions/ERC721URIStorage.sol";
import "@openzeppelin/contracts/access/AccessControl.sol";
import "@openzeppelin/contracts/utils/Counters.sol";

/**
 * @title BlueCarbonCredit
 * @dev ERC721 NFT representing verified blue carbon credits with geospatial proof
 * @notice Each token is backed by IPFS-stored evidence (geotagged images)
 */
contract BlueCarbonCredit is ERC721, ERC721URIStorage, AccessControl {
    using Counters for Counters.Counter;

    // Role definitions
    bytes32 public constant MINTER_ROLE = keccak256("MINTER_ROLE");
    bytes32 public constant VERIFIER_ROLE = keccak256("VERIFIER_ROLE");

    // Token counter
    Counters.Counter private _tokenIdCounter;

    // Carbon credit metadata structure
    struct CarbonCreditMetadata {
        string ipfsCid;           // IPFS hash of geotagged evidence
        int256 latitude;          // Latitude × 10^6 (stored as integer)
        int256 longitude;         // Longitude × 10^6 (stored as integer)
        uint256 timestamp;        // Submission timestamp
        address submitter;        // Field user's wallet
        string creditsAmount;     // Metric tons of CO2 equivalent
        bool verified;            // Verification status
    }

    // Mapping: tokenId => CarbonCreditMetadata
    mapping(uint256 => CarbonCreditMetadata) public creditMetadata;

    // Mapping: ipfsCid => tokenId (prevent duplicate credits)
    mapping(string => uint256) public cidToTokenId;

    // Events
    event CreditMinted(
        uint256 indexed tokenId,
        address indexed to,
        string ipfsCid,
        int256 latitude,
        int256 longitude
    );

    event CreditVerified(uint256 indexed tokenId, address indexed verifier);

    event MetadataUpdated(uint256 indexed tokenId, string newUri);

    /**
     * @dev Constructor sets deployer as DEFAULT_ADMIN_ROLE
     */
    constructor() ERC721("BlueCarbonCredit", "BCC") {
        _grantRole(DEFAULT_ADMIN_ROLE, msg.sender);
    }

    /**
     * @dev Mints a new carbon credit NFT with geospatial data
     * @param to Address receiving the NFT (field user wallet)
     * @param uri TokenURI pointing to IPFS metadata
     * @param ipfsCid IPFS content hash of evidence
     * @param lat Latitude × 10^6
     * @param long Longitude × 10^6
     * @param creditsAmount String representation of credits (e.g., "2.5")
     * @notice Only MINTER_ROLE can call (backend wallet)
     * @notice Prevents duplicate IPFS hashes
     */
    function safeMint(
        address to,
        string memory uri,
        string memory ipfsCid,
        int256 lat,
        int256 long,
        string memory creditsAmount
    ) external onlyRole(MINTER_ROLE) returns (uint256) {
        // Prevent duplicate credits
        require(cidToTokenId[ipfsCid] == 0, "IPFS hash already minted");
        require(to != address(0), "Invalid recipient address");
        require(lat >= -90000000 && lat <= 90000000, "Invalid latitude");
        require(long >= -180000000 && long <= 180000000, "Invalid longitude");

        uint256 tokenId = _tokenIdCounter.current();
        _tokenIdCounter.increment();

        // Safe mint
        _safeMint(to, tokenId);

        // Set token URI
        _setTokenURI(tokenId, uri);

        // Store metadata
        creditMetadata[tokenId] = CarbonCreditMetadata({
            ipfsCid: ipfsCid,
            latitude: lat,
            longitude: long,
            timestamp: block.timestamp,
            submitter: to,
            creditsAmount: creditsAmount,
            verified: true
        });

        // Register IPFS hash
        cidToTokenId[ipfsCid] = tokenId;

        emit CreditMinted(tokenId, to, ipfsCid, lat, long);

        return tokenId;
    }

    /**
     * @dev Verifies a pending carbon credit
     * @param tokenId ID of the token to verify
     * @notice Only VERIFIER_ROLE can call
     */
    function verify(uint256 tokenId) external onlyRole(VERIFIER_ROLE) {
        require(_ownerOf(tokenId) != address(0), "Token does not exist");
        creditMetadata[tokenId].verified = true;
        emit CreditVerified(tokenId, msg.sender);
    }

    /**
     * @dev Updates the URI for a token
     * @param tokenId ID of the token
     * @param newUri New token URI
     */
    function updateTokenURI(uint256 tokenId, string memory newUri)
        external
        onlyRole(DEFAULT_ADMIN_ROLE)
    {
        require(_ownerOf(tokenId) != address(0), "Token does not exist");
        _setTokenURI(tokenId, newUri);
        emit MetadataUpdated(tokenId, newUri);
    }

    /**
     * @dev Gets full metadata for a token
     */
    function getMetadata(uint256 tokenId)
        external
        view
        returns (CarbonCreditMetadata memory)
    {
        require(_ownerOf(tokenId) != address(0), "Token does not exist");
        return creditMetadata[tokenId];
    }

    /**
     * @dev Gets total minted credits
     */
    function getTotalMinted() external view returns (uint256) {
        return _tokenIdCounter.current();
    }

    /**
     * @dev Checks if IPFS hash is already registered
     */
    function isDuplicateSubmission(string memory ipfsCid)
        external
        view
        returns (bool)
    {
        return cidToTokenId[ipfsCid] != 0;
    }

    // Override functions for ERC721URIStorage compatibility
    function tokenURI(uint256 tokenId)
        public
        view
        override(ERC721, ERC721URIStorage)
        returns (string memory)
    {
        return super.tokenURI(tokenId);
    }

    function supportsInterface(bytes4 interfaceId)
        public
        view
        override(ERC721, ERC721URIStorage, AccessControl)
        returns (bool)
    {
        return super.supportsInterface(interfaceId);
    }

    function _update(
        address to,
        uint256 tokenId,
        address auth
    ) internal override(ERC721) returns (address) {
        return super._update(to, tokenId, auth);
    }

    function _increaseBalance(address account, uint128 value)
        internal
        override(ERC721)
    {
        super._increaseBalance(account, value);
    }
}