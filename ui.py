import streamlit as st
import plotly.graph_objects as go
import numpy as np
import time
from web3 import Web3
import json
import datetime
from icecream import ic

from scipy.ndimage import gaussian_filter1d

# Set up the Streamlit page configuration
st.set_page_config(page_title="Prototype", layout="wide")
st.title("Blockchain E&I course prototype")

date_format = "%Y-%m-%d %H:%M:%S"



# URL Infura для сети Polygon Mainnet
infura_url = "https://polygon-mainnet.infura.io/v3/73e4cc21b1ff41c387f0629745ebf246"
w3 = Web3(Web3.HTTPProvider(infura_url))

time.sleep(3)

# Проверяем подключение к сети
if not w3.is_connected():
    print("Не удалось подключиться к сети Polygon Mainnet")
    exit(1)

# Укажите адрес вашего контракта (замените на реальный адрес)
contract_address =  "0xe232E12Eb7c060Ac788483CBdfF71286c4894D48"

# Определяем диапазон блоков для выборки логов
start_block = 0  # либо укажите конкретный начальный номер блока
START_LINE = "=========="

def parse_to_list(logs, param):
    values = []
    datetime = []

    for log in logs:
        datetime.append(log['datetime'])
        values.append(log['mnemonics'][param]['value'])

    return datetime, values


def decode_log_data(log):
    """
    Decodes the 'data' field from a log from hex to a UTF-8 string.
    """
    hex_data = log["data"]
    # Convert to hex string if needed.
    if isinstance(hex_data, bytes):
        hex_str = hex_data.hex()
    elif isinstance(hex_data, str):
        hex_str = hex_data[2:] if hex_data.startswith("0x") else hex_data
    else:
        hex_str = str(hex_data)
    try:
        decoded_str = bytes.fromhex(hex_str).decode("utf-8")
    except Exception:
        # Fallback to tolerant decoding.
        decoded_str = bytes.fromhex(hex_str).decode("utf-8", errors="ignore")
    decoded_str = decoded_str.replace("\x00", "").strip()
    return decoded_str


def get_data_from_blockchain():
    # while True:
    end_block = w3.eth.block_number  # последний блок на момент запроса

    # Получаем логи контракта
    logs = w3.eth.get_logs({
        "address": contract_address,
        "fromBlock": start_block,
        "toBlock": end_block
    })
    
    marker_block = None
    
    for log in logs:
        decoded = decode_log_data(log)
        if START_LINE in decoded.strip():
            marker_block = log["blockNumber"]
            print("Marker found at block:", marker_block)
            break

    if marker_block is None:
        print("Marker not found in logs.")
        return [], [], [], []


    subsequent_logs = w3.eth.get_logs({
            "address": contract_address,
            "fromBlock": marker_block,
            "toBlock": end_block
            })

    data_logs = []
    for log in subsequent_logs:
        decoded = decode_log_data(log)
        # Skip marker logs if encountered again.
        if START_LINE in decoded.strip():
            continue
        try:
            # Attempt to parse the decoded log data as JSON.
            data = json.loads(decoded)
        except Exception:
            # If decoding fails, store the raw decoded string.
            data = decoded
        data_logs.append(data)


    datetime_distance, distance = parse_to_list(logs=data_logs, param="distance")
    datetime_gas, gas = parse_to_list(logs=data_logs, param="CO2")

    return datetime_distance, distance, datetime_gas, gas
