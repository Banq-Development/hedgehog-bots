# hedgehog-bots
Minimal bot implementations for automated use of hedgehog a decentralized hedging protocol. 

This bot contains an example implementation that opens a hedge position if the price of ETH/DAI decreases more than 0.01% between blocks and closed the hedge position if the price of ETH/DAI increases more than 0.01%. This is only an example to show the options. You can customize the bot to execute your own hedging strategy. 

## Dependencies
- python 3.0
- web3.py
- asyncio

## Customize
To use your own hedging strategy customize the bot file hedgehog_hedger.py:
	1. Enter your infura key 
	2. Add your account info
	  	IMPORTANT: approve the hedgehog contract for the public key used
	3. Adjust the logic under handle_event() to use your own hedging strategy

## Run
Runs like any python script.
