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


# 签名：如果数据被更改，则签名会被更改
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
        在任何情况下都不应该直接调用构造函数，而是通过使用类属性或standalone_nodes获取自动创建的GflNode对象

        :param address: Node地址，每个节点唯一，用于标识节点身份，验证数据签名
        :param pub_key: 节点公钥，用于加密数据
        :param priv_key: 节点私钥，用于解密数据，签名数据
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
        初始化GFL节点
        :return:
        """
        node = cls.__new_node()
        key_dir = PathUtils.join(GflConf.home_dir, "key")  # /Users/YY/.gfl/key
        os.makedirs(key_dir, exist_ok=True)
        key_file = PathUtils.join(key_dir, "key.json")  # /Users/YY/.gfl/key/key.json
        cls.__save_node(node, key_file)
        # key.json中的内容如下
        # {
        #     "address": "a8C03cEBFc6C11C1707032590adf2ACF4ccAc655",
        #     "pub_key": "d2a95fb211c91f79d052c3c927f51b22893a3b3f7a28090f32d03fc7224bdca0be91173445f71bf1bf91d0fee52ee7c805b7b10dc1b12fa2ed5267b818eb1bc8",
        #     "priv_key": "708d8f67deb461bdf2a3c9c2d82584b8304cbad32398a5ce5706a8e45f5210bf"
        # }
        cls.default_node = node

    @classmethod
    def add_standalone_node(cls) -> NoReturn:
        # 添加【一个】standalone_node
        node = cls.__new_node()
        for i in range(100):
            # 限制最多100个模拟节点， 防止此处出现死循环
            if i not in cls.standalone_nodes:
                key_file = PathUtils.join(GflConf.home_dir, "key", "manager-%d.json" % i)
                cls.__save_node(node, key_file)
                cls.standalone_nodes[i] = node
                return
        raise ValueError("最多只支持100个standalone模式虚拟节点.")

    @classmethod
    def load_node(cls) -> NoReturn:
        """
        加载节点目录中的key文件，创建default_node和standalone_nodes对象
        :return:
        """
        key_dir = PathUtils.join(GflConf.home_dir, "key")
        cls.default_node = cls.__load_node(PathUtils.join(key_dir, "key.json"))
        for filename in os.listdir(key_dir):
            if filename.startswith("manager-"):
                node_idx = int(filename[5:-5])
                cls.standalone_nodes[node_idx] = cls.__load_node(PathUtils.join(key_dir, filename))

    # 返回签名地址，从签名中返回。签名：如果数据被更改，则签名会被更改
    @classmethod
    def recover(cls, message: AnyStr, signature: str) -> str:
        """
        Get the address of the manager that signed the given message.

        :param message: the message that was signed
        :param signature: the signature of the message
        :return: the address of the manager
        """
        if type(message) == str:
            message = message.encode("utf8")
        if type(message) != bytes:
            raise TypeError("message only support str or bytes.")
        encoded_message = encode_defunct(message)
        return w3.eth.account.recover_message(encoded_message, signature=signature)

    @classmethod
    def encrypt(cls, plain: AnyStr, pub_key) -> bytes:
        # 使用 pub_key 公钥，进行加密
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
