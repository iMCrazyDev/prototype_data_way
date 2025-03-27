import time
from gpiozero import DistanceSensor
from web3 import Web3

sensor = DistanceSensor(echo=24, trigger=23)

rpc_url = 'https://polygon-rpc.com'
w3 = Web3(Web3.HTTPProvider(rpc_url))

if not w3.is_connected():
    print("Ошибка: не удалось подключиться к блокчейну!")
    exit(1)

chain_id = 137

account = w3.eth.account.from_key(private_key)

contract_abi = [
	{
		"inputs": [
			{
				"internalType": "address",
				"name": "sender",
				"type": "address"
			},
			{
				"internalType": "uint256",
				"name": "id",
				"type": "uint256"
			}
		],
		"name": "allowSender",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [],
		"stateMutability": "nonpayable",
		"type": "constructor"
	},
	{
		"anonymous": False,
		"inputs": [
			{
				"indexed": True,
				"internalType": "uint256",
				"name": "id",
				"type": "uint256"
			},
			{
				"indexed": True,
				"internalType": "address",
				"name": "sender",
				"type": "address"
			},
			{
				"indexed": False,
				"internalType": "string",
				"name": "data",
				"type": "string"
			}
		],
		"name": "DataReceived",
		"type": "event"
	},
	{
		"inputs": [
			{
				"internalType": "string",
				"name": "data",
				"type": "string"
			}
		],
		"name": "receiveData",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "address",
				"name": "sender",
				"type": "address"
			}
		],
		"name": "revokeSender",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [],
		"name": "admin",
		"outputs": [
			{
				"internalType": "address",
				"name": "",
				"type": "address"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "address",
				"name": "",
				"type": "address"
			}
		],
		"name": "allowedSenders",
		"outputs": [
			{
				"internalType": "uint256",
				"name": "",
				"type": "uint256"
			}
		],
		"stateMutability": "view",
		"type": "function"
	}
]

contract = w3.eth.contract(address=contract_address, abi=contract_abi)

def send_distance(distance_cm):
    try:
        distance_str = f"{distance_cm:.2f}"
        print(f"Отправка транзакции с данными: {distance_str} см")
        nonce = w3.eth.get_transaction_count(account.address)
        txn = contract.functions.receive_data(distance_str).build_transaction({
            'chainId': chain_id,
            'gas': 2000000,
            'gasPrice': w3.to_wei('80', 'gwei'),
            'nonce': nonce,
        })
        signed_txn = account.sign_transaction(txn)
        tx_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)
        print("Tx hash:", w3.to_hex(tx_hash))
    except Exception as err:
        print("Ошибка отправки транзакции:", err)

try:
    while True:
        distance_m = sensor.distance
        distance_cm = distance_m * 100
        print(f"Измеренное расстояние: {distance_cm:.2f} см")
        send_distance(distance_cm)
        time.sleep(30)
except KeyboardInterrupt:
    print("Программа остановлена пользователем")
