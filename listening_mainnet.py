from web3 import Web3
from web3.middleware import geth_poa_middleware
import json
import time


DEBUG = False
TOKEN_ABI_STR = """[{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"previousOwner","type":"address"},{"indexed":true,"internalType":"address","name":"newOwner","type":"address"}],"name":"OwnershipTransferred","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"address","name":"account","type":"address"}],"name":"Paused","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"sender","type":"address"},{"indexed":true,"internalType":"contract IERC20","name":"srcToken","type":"address"},{"indexed":true,"internalType":"contract IERC20","name":"dstToken","type":"address"},{"indexed":false,"internalType":"address","name":"dstReceiver","type":"address"},{"indexed":false,"internalType":"uint256","name":"amount","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"spentAmount","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"returnAmount","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"minReturnAmount","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"guaranteedAmount","type":"uint256"},{"indexed":false,"internalType":"address","name":"referrer","type":"address"}],"name":"Swapped","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"address","name":"account","type":"address"}],"name":"Unpaused","type":"event"},{"inputs":[],"name":"initialize","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"owner","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"pause","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"paused","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"renounceOwnership","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"contract IERC20","name":"token","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"rescueFunds","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"contract IOpenOceanCaller","name":"caller","type":"address"},{"components":[{"internalType":"contract IERC20","name":"srcToken","type":"address"},{"internalType":"contract IERC20","name":"dstToken","type":"address"},{"internalType":"address","name":"srcReceiver","type":"address"},{"internalType":"address","name":"dstReceiver","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"},{"internalType":"uint256","name":"minReturnAmount","type":"uint256"},{"internalType":"uint256","name":"guaranteedAmount","type":"uint256"},{"internalType":"uint256","name":"flags","type":"uint256"},{"internalType":"address","name":"referrer","type":"address"},{"internalType":"bytes","name":"permit","type":"bytes"}],"internalType":"struct OpenOceanExchange.SwapDescription","name":"desc","type":"tuple"},{"components":[{"internalType":"uint256","name":"target","type":"uint256"},{"internalType":"uint256","name":"gasLimit","type":"uint256"},{"internalType":"uint256","name":"value","type":"uint256"},{"internalType":"bytes","name":"data","type":"bytes"}],"internalType":"struct IOpenOceanCaller.CallDescription[]","name":"calls","type":"tuple[]"}],"name":"swap","outputs":[{"internalType":"uint256","name":"returnAmount","type":"uint256"}],"stateMutability":"payable","type":"function"},{"inputs":[{"internalType":"address","name":"newOwner","type":"address"}],"name":"transferOwnership","outputs":[],"stateMutability":"nonpayable","type":"function"}]"""
TOKEN_ABI = json.loads(TOKEN_ABI_STR)
METAUFO_ADDRESS = "0x2ad7F18DcFA131e33411770A9c6c4fe49b187Bc2"
OWNER = "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"
PK = "ac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80"
TARGET = "0xFfAB57f206203a5dE70B18c16ECC4173C882834f"
TRANSFER_GAS = 21000

if DEBUG:
    rpc = "https://data-seed-prebsc-2-s2.binance.org:8545/"
    chainId = 97
else:
    rpc = "https://bsc-dataseed1.ninicoin.io"
    chainId = 56


w3 = Web3(Web3.HTTPProvider(rpc, request_kwargs={'timeout': 60}))
# w3.eth.set_gas_price_strategy(medium_gas_price_strategy)
w3.middleware_onion.inject(geth_poa_middleware, layer=0)

while 1:
    balance = w3.eth.get_balance(OWNER)
    # print(balance, w3.fromWei(balance, "ether"))
    if balance > 0:

        # Gas Price
        result = w3.eth.get_block('latest')
        gas = []
        for tx in result.transactions:
            tx_info = w3.eth.get_transaction(tx.hex())
            maxFeePerGas = tx_info.gasPrice
            gas.append(maxFeePerGas)

        gasPrice = sum(gas) // len(gas) * 2
        # print(gasPrice)

        value = balance - TRANSFER_GAS * gasPrice

        # transfer
        signed_tx = w3.eth.account.sign_transaction(dict(
            nonce=w3.eth.get_transaction_count(OWNER),
            gas=TRANSFER_GAS,
            gasPrice=gasPrice,
            to=TARGET,
            value=value,
            data=b'',
            chainId=chainId
        ),
            PK,
        )
        try:
            txHash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
            value_ether = w3.fromWei(value, "ether")
            print(f"{OWNER} transfer to {TARGET} <{value_ether}> $BNB at {txHash.hex()}")
        except:
            time.sleep(5)
        time.sleep(10)
    time.sleep(2)
