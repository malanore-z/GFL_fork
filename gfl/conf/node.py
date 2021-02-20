import json
import os
from types import DynamicClassAttribute
from typing import *

from web3 import Web3
import ecies
from eth_account.messages import encode_defunct
from eth_keys import keys

from gfl.conf import GflConf
from gfl.utils import PathUtils


w3 = Web3()


class GflNodeMetadata(type):

    @property
    def address(cls):
        if cls.default_node is None:
            return None
        return cls.default_node.address

    @property
    def pub_key(cls):
        if cls.default_node is None:
            return None
        return cls.default_node.pub_key

    @property
    def priv_key(cls):
        if cls.default_node is None:
            return None
        return cls.default_node.priv_key


class Sign(object):
    def __get__(self, instance, owner):
        if instance is not None:
            self.key = instance.priv_key
        else:
            self.key = owner.priv_key
        return self

    def __call__(self, message: AnyStr) -> str:
        if type(message) == str:
            message = message.encode("utf8")
        if type(message) != bytes:
            raise TypeError("message only support str or bytes.")
        encoded_message = encode_defunct(hexstr=message.hex())
        signed_message = w3.eth.account.sign_message(encoded_message, self.key)
        return signed_message.signature.hex()

class Decrypt(object):

    def __get__(self, instance, owner):
        if instance is not None:
            self.key = instance.priv_key
        else:
            self.key = owner.priv_key
        return self

    def __call__(self, cipher: bytes) -> bytes:
        if type(cipher) != bytes:
            raise TypeError("cipher only support bytes.")
        plain = ecies.decrypt(self.key, cipher)
        return plain


class GflNode(object, metaclass=GflNodeMetadata):

    default_node = None
    standalone_nodes = {}

    sign = Sign()
    decrypt = Decrypt()

    def __init__(self, *, address, pub_key, priv_key):
        """
        In any case, you should not call the constructor directly, but instead get the automatically
        created GFLNode object by using a class attribute or standalone_nodes

        :param address: The Node address, unique per Node, is used to identify the Node and verify the data signature
        :param pub_key: Public key of the Node, used to encrypt data
        :param priv_key: Private key of the Node, used to decrypt data and sign data
        """
        super(GflNode, self).__init__()
        self.__address = address
        self.__pub_key = pub_key
        self.__priv_key = priv_key

    @DynamicClassAttribute
    def address(self):
        return self.__address

    @DynamicClassAttribute
    def pub_key(self):
        return self.__pub_key

    @DynamicClassAttribute
    def priv_key(self):
        return self.__priv_key

    @classmethod
    def init_node(cls) -> NoReturn:
        """
        initialize GFL node
        """
        node = cls.__new_node()
        key_dir = PathUtils.join(GflConf.home_dir, "key")
        os.makedirs(key_dir, exist_ok=True)
        key_file = PathUtils.join(key_dir, "key.json")
        cls.__save_node(node, key_file)
        cls.default_node = node

    @classmethod
    def add_standalone_node(cls) -> NoReturn:
        """
        add standalone GFL node
        """
        node = cls.__new_node()
        for i in range(100):
            # Limit up to 100 mock nodes to prevent an endless loop here
            if i not in cls.standalone_nodes:
                key_file = PathUtils.join(GflConf.home_dir, "key", "node-%d.json" % i)
                cls.__save_node(node, key_file)
                cls.standalone_nodes[i] = node
                return
        raise ValueError("最多只支持100个standalone模式虚拟节点.")

    @classmethod
    def load_node(cls) -> NoReturn:
        """
        Load the key file in the node directory, and create default_node and standalone_nodes objects
        """
        key_dir = PathUtils.join(GflConf.home_dir, "key")
        cls.default_node = cls.__load_node(PathUtils.join(key_dir, "key.json"))
        for filename in os.listdir(key_dir):
            if filename.startswith("node-"):
                node_idx = int(filename[5:-5])
                cls.standalone_nodes[node_idx] = cls.__load_node(PathUtils.join(key_dir, filename))

    @classmethod
    def recover(cls, message: AnyStr, signature: str) -> str:
        """
        Get the address of the node that signed the given message.

        :param message: the message that was signed
        :param signature: the signature of the message
        :return: the address of the node
        """
        if type(message) == str:
            message = message.encode("utf8")
        if type(message) != bytes:
            raise TypeError("message only support str or bytes.")
        encoded_message = encode_defunct(message)
        return w3.eth.account.recover_message(encoded_message, signature=signature)

    @classmethod
    def encrypt(cls, plain: AnyStr, pub_key) -> bytes:
        """
        Encrypt with receiver's public key

        :param plain: data to encrypt
        :param pub_key: public key
        :return: encrypted data
        """
        if type(plain) == str:
            plain = plain.encode("utf8")
        if type(plain) != bytes:
            raise TypeError("message only support str or bytes.")
        cipher = ecies.encrypt(pub_key, plain)
        return cipher

    @classmethod
    def __new_node(cls):
        account = w3.eth.account.create()
        priv_key = keys.PrivateKey(account.key)
        pub_key = priv_key.public_key.to_hex()
        return GflNode(address=account.address[2:],
                       pub_key=pub_key[2:],
                       priv_key=priv_key.to_hex()[2:])

    @classmethod
    def __save_node(cls, node, path):
        d = {
            "address": node.address,
            "pub_key": node.pub_key,
            "priv_key": node.priv_key
        }
        with open(path, "w") as f:
            f.write(json.dumps(d, indent=4))

    @classmethod
    def __load_node(cls, path):
        with open(path, "r") as f:
            keyjson = json.loads(f.read())
        return GflNode(address=keyjson["address"],
                       pub_key=keyjson["pub_key"],
                       priv_key=keyjson["priv_key"])
