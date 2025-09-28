// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

contract BlueCarbonCredit is ERC721, Ownable {
    uint256 private _nextTokenId;

    // Contract jab deploy hoga, to uska naam "Blue Carbon Credit" aur symbol "BCC" hoga.
    constructor(address initialOwner)
        ERC721("Blue Carbon Credit", "BCC")
        Ownable(initialOwner)
    {}

    // Yeh function naya carbon credit (NFT) banayega.
    // Sirf contract ka owner (hamara backend server) hi ise call kar paayega.
    function safeMint(address to, string memory ipfsHash) public onlyOwner {
        uint256 tokenId = _nextTokenId++;
        _safeMint(to, tokenId);
        // POC ko simple rakhne ke liye hum ipfsHash ko on-chain save nahi kar rahe.
    }
}