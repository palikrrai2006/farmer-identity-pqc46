// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract FarmerRegistry {
    
    struct Farmer {
        string  farmer_id;
        string  bio_hash;
        string  ipfs_cid;
        uint256 timestamp;
        bool    exists;
    }

    mapping(string => Farmer) private farmers;
    address public owner;

    event FarmerRegistered(string farmer_id, string ipfs_cid, uint256 timestamp);
    event FarmerVerified(string farmer_id, uint256 timestamp);

    constructor() {
        owner = msg.sender;
    }

    modifier onlyOwner() {
        require(msg.sender == owner, "Only owner can call this");
        _;
    }

    function registerFarmer(
        string memory farmer_id,
        string memory bio_hash,
        string memory ipfs_cid
    ) public onlyOwner {
        require(!farmers[farmer_id].exists, "Farmer already registered");
        
        farmers[farmer_id] = Farmer({
            farmer_id:  farmer_id,
            bio_hash:   bio_hash,
            ipfs_cid:   ipfs_cid,
            timestamp:  block.timestamp,
            exists:     true
        });

        emit FarmerRegistered(farmer_id, ipfs_cid, block.timestamp);
    }

    function getFarmer(string memory farmer_id) 
        public view returns (
            string memory,
            string memory,
            string memory,
            uint256
        ) 
    {
        require(farmers[farmer_id].exists, "Farmer not found");
        Farmer memory f = farmers[farmer_id];
        return (f.farmer_id, f.bio_hash, f.ipfs_cid, f.timestamp);
    }

    function farmerExists(string memory farmer_id) public view returns (bool) {
        return farmers[farmer_id].exists;
    }
}