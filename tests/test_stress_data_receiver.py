from brownie import accounts, DataReceiver, network, chain
import csv, time, random, string
from pathlib import Path
from tqdm import trange

def test_single_tx():
    admin  = accounts[0]
    sender = accounts[1]

    c = DataReceiver.deploy({'from': admin})
    c.allowSender(sender, 42, {'from': admin})

    tx = c.receiveData(b"ping", {'from': sender})
    print("gas:", tx.gas_used, tx.events)
    assert tx.events["DataReceived"]["id"] == 42

N_MSG      = 10           
M_SENDERS  = 20               
PAYLOAD_B  = 300              
BATCH_SIZE = 500              
CSV_FILE   = Path("stress_stats.csv")

def rand_bytes(n):
    return "".join(random.choices(string.ascii_letters + string.digits, k=n)).encode()

def write_csv_row(epoch, sent, avg_gas):
    first = not CSV_FILE.exists()
    with CSV_FILE.open("a", newline="") as f:
        w = csv.writer(f)
        if first:
            w.writerow(["ts", "messages", "avg_gas"])
        w.writerow([epoch, sent, avg_gas])

def test_stress():
    admin = accounts[0]
    contract = DataReceiver.deploy({"from": admin})

    senders, id_map = [], {}
    for i in range(M_SENDERS):
        sender = accounts.add()
        contract.allowSender(sender, i + 1, {"from": admin})
        senders.append(sender)
        id_map[sender.address] = i + 1

    total_gas = 0
    start_ts  = int(time.time())

    for i in trange(1, N_MSG + 1, desc="stress"):
        s      = random.choice(senders)
        expect = id_map[s.address]
        tx     = contract.receiveData(rand_bytes(PAYLOAD_B), {"from": s})

        ev = tx.events["DataReceived"]
        assert ev["id"] == expect and ev["sender"] == s.address
        total_gas += tx.gas_used

        if i % BATCH_SIZE == 0:
            avg_gas = total_gas / i
            write_csv_row(int(time.time() - start_ts), i, round(avg_gas, 2))
            snap = chain.snapshot()
            chain.revert(snap)

    write_csv_row(int(time.time()-start_ts), N_MSG, round(total_gas/N_MSG, 2))
    avg = total_gas / N_MSG
    print(f"\n*** DONE  messages={N_MSG}  avg_gas={avg:.1f} ***")
