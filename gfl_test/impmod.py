from web3 import Web3
from eth_account.messages import encode_defunct


w3 = Web3()

address = "0xC11F1975dD5a21695Ae48a1AED2B66cDce484Ece"
key = "0x289e73135dad31b89df9659953c4cc638db1dd9b8a73b815f21a5672d52dee55"

msg = encode_defunct(hexstr=b"qwert".hex())
signed_msg = w3.eth.account.sign_message(msg, key)
print(signed_msg.signature.hex())

sign = "0x00200f1dd5d375d1ccbd3c53f0704e1442905931233b731da47ec2513c9fdd5b12a213abd594597aec74be5255ef45448a39f8853ed87ffd62e0667ded4f83e01c"

addr = w3.eth.account.recover_message(msg, signature=sign)
print(addr)


if __name__ == "__main__":
    pass
