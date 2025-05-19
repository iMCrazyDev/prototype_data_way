// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract DataReceiver {
    address public admin;
    uint256 public nextDeviceId = 1;

    struct DeviceInfo {
        address sender;
        string name;
        string metadata;
    }

    mapping(uint256 => DeviceInfo) public devices;           // id → info
    mapping(address => uint256) public addressToId;          // sender → id

    event DataReceived(
        uint256 indexed id,
        address indexed sender,
        bytes data
    );

    modifier onlyAdmin() {
        require(msg.sender == admin, "Not admin");
        _;
    }

    constructor() {
        admin = msg.sender;
    }

    function allowSender(
        address sender,
        string calldata name,
        string calldata metadata
    ) external onlyAdmin returns (uint256 assignedId) {
        require(sender != address(0), "zero addr");
        require(addressToId[sender] == 0, "already allowed");

        uint256 id = nextDeviceId++;
        addressToId[sender] = id;
        devices[id] = DeviceInfo({
            sender: sender,
            name: name,
            metadata: metadata
        });

        return id;
    }

    function revokeSender(address sender) external onlyAdmin {
        uint256 id = addressToId[sender];
        require(id != 0, "not allowed");

        delete devices[id];
        delete addressToId[sender];
    }

    function receiveData(bytes calldata data) external {
        uint256 id = addressToId[msg.sender];
        require(id != 0, "Sender not allowed");

        emit DataReceived(id, msg.sender, data);
    }

    // View helpers
    function getDeviceById(uint256 id) external view returns (DeviceInfo memory) {
        return devices[id];
    }

    function getDeviceIdByAddress(address sender) external view returns (uint256) {
        return addressToId[sender];
    }
}
