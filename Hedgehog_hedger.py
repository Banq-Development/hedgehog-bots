# Minimal local hedger script for Hedgehog
from web3 import Web3
import asyncio
import json

'''
ADD BELOW VARIABLES
'''
infura_key = "ADD_INFURA_KEY_HERE"
pbk = "ADD_PUBLIC_KEY_HERE"
pvk = "ADD_PRIVATE_KEY_HERE"
amount = 0  #ADJUST_AMOUNT FOR HASSETS TO DEPOSIT/WITHDRAW

#Import chain data
web3 = Web3(Web3.HTTPProvider("https://mainnet.infura.io/v3/"+infura_key))
#Import Hedgehog contract
with open("ABI/hedgehog_abi.json") as f:
    info_json = json.load(f)
    abi_Hedgehog = info_json["abi"]
address_Hedgehog = web3.toChecksumAddress("0x7ad99BD7414b1d27C25076afB807b8d3BDC8CC59")
contract_Hedgehog = web3.eth.contract(address_Hedgehog, abi=abi_Hedgehog)
#Import Uniswap contract
with open("ABI/uniswap_router_abi.json") as f:
    info_json = json.load(f)
    abi_Uniswap_Router = info_json["abi"]
address_Uniswap_Router = web3.toChecksumAddress("0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D")
contract_Uniswap_Router = web3.eth.contract(address_Uniswap_Router, abi=abi_Uniswap_Router)
#Set address tokens used for hedging price assesment
address_DAI = web3.toChecksumAddress("0x6b175474e89094c44da98b954eedeac495271d0f")
address_WETH = web3.toChecksumAddress("0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2")
with open("ABI/WETH_abi.json") as f:
    info_json = json.load(f)
    abi_WETH = info_json["abi"]
contract_WETH = web3.eth.contract(address_WETH, abi=abi_WETH)

#Global ETH price storage per block
price_ETH_stored = 0

def handle_event(block_hash):
    global price_ETH_stored
    block = web3.eth.getBlock(block_hash)
    #Get price Hedgehog current
    price_hedgehog = contract_Hedgehog.functions.price().call()
    #Get price Uniswap ETH-DAI
    amount_out = contract_Uniswap_Router.functions.getAmountsOut(10**18, [address_WETH, address_DAI]).call()

    '''
    ADJUST LOGIC BELOW FOR CUSTOM SCRIPT
    '''
    if price_ETH_stored == 0:
        price_ETH_stored = amount_out[1]
    # Add buy logic here - current example is remove a hedge position on per block price positive change ETH/DAI > 0.01%
    if amount_out[1] > price_ETH_stored * 10001 / 10000:
        print("close hedge position")

        #Check if hAsset balance > amount burn
        balance_hAsset = contract_Hedgehog.functions.balanceOf(pbk).call()
        print('balance hasset', balance_hAsset)
        if balance_hAsset > amount:
            #Create signed transaction for infura
            amount_asset = contract_Hedgehog.functions.calculateAssetOut(amount).call()
            nonce = web3.eth.getTransactionCount(web3.toChecksumAddress(pbk))
            txn = contract_Hedgehog.functions.withdraw(amount, amount_asset).buildTransaction({'gas': 300000,'nonce': nonce})
            signed_txn = web3.eth.account.signTransaction(txn, pvk)
            #Send transaction
            web3.eth.sendRawTransaction(signed_txn.rawTransaction)
    # Add sell logic here - example is takes a hedge position on per block negative price change ETH/DAI > 0.01%
    elif amount_out[1] < price_ETH_stored * 9999 / 10000:
        print("open hedge position")
        #Check if asset balance > amount mint
        balance_asset = contract_WETH.functions.balanceOf(pbk).call()
        print('balance asset', balance_asset)
        if balance_asset > amount:
            #Create signed transaction for infura
            amount_asset = contract_Hedgehog.functions.calculateAssetIn(amount).call()
            nonce = web3.eth.getTransactionCount(web3.toChecksumAddress(pbk))
            txn = contract_Hedgehog.functions.deposit(amount, amount_asset).buildTransaction({'gas': 300000,'nonce': nonce})
            signed_txn = web3.eth.account.signTransaction(txn, pvk)
            #Send transaction
            web3.eth.sendRawTransaction(signed_txn.rawTransaction)

    price_ETH_stored = amount_out[1]
    print('Block Number: ', block['number'])
    print("Block Hash: {}".format(block_hash.hex()))
    print("Hedgehog price:", price_hedgehog / 10**18, "WETH / hWETH")
    print("ETH price:", amount_out[1] / 10**18, "DAI / ETH")

async def log_loop(block_filter, poll_interval):
    while True:
        for block_hash in block_filter.get_new_entries():
            handle_event(block_hash)
        await asyncio.sleep(poll_interval)

def main():
    loop = asyncio.get_event_loop()
    try:
        block_filter = web3.eth.filter('latest')
        loop.run_until_complete(asyncio.gather(log_loop(block_filter, 2)))
    finally:
        loop.close()

if __name__ == '__main__':
    main()