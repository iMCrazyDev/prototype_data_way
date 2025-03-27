// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract DataReceiver {
    address public admin;

    mapping(address => uint256) public allowedSenders;

    event DataReceived(uint256 indexed id, address indexed sender, string data);

    modifier onlyAdmin() {
        require(msg.sender == admin, "Not admin");
        _;
    }

    constructor() {
        admin = msg.sender;
    }

    function allowSender(address sender, uint256 id) external onlyAdmin {
        allowedSenders[sender] = id;
    }

    function revokeSender(address sender) external onlyAdmin {
        delete allowedSenders[sender];
    }

    function receiveData(string memory data) public {
        uint256 id = allowedSenders[msg.sender];
        require(id != 0, "Sender not allowed");

        emit DataReceived(id, msg.sender, data);
    }
}
