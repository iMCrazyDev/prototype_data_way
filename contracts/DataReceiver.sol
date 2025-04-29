// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract DataReceiver {
    address public admin;

    mapping(address => uint256) public allowedSenders;
    mapping(uint256 => address) public idOwner;

    event DataReceived(uint256 indexed id, address indexed sender, bytes data);

    modifier onlyAdmin() {
        require(msg.sender == admin, "Not admin");
        _;
    }

    constructor() {
        admin = msg.sender;
    }

    function allowSender(address sender, uint256 id) external onlyAdmin {
        require(sender != address(0), "zero addr");
        require(id != 0, "zero id");
        require(allowedSenders[sender] == 0, "already allowed");
        require(idOwner[id] == address(0), "id taken");

        allowedSenders[sender] = id;
        idOwner[id]            = sender;
    }

    function revokeSender(address sender) external onlyAdmin {
        uint256 id = allowedSenders[sender];
        require(id != 0, "not allowed");

        delete allowedSenders[sender];
        delete idOwner[id];
    }

    function receiveData(bytes calldata data) external {
        uint256 id = allowedSenders[msg.sender];
        require(id != 0, "Sender not allowed");
        emit DataReceived(id, msg.sender, data);
    }
}
