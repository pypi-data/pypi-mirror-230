from .abstract_rpcs import RPCData
from .abstract_abis import ABIBridge
from abstract_security.envy_it import get_env_value
class AccountManager:
    def __init__(self, env_key:str=None,address:str=None, rpc:dict=None):
        self.rpc_manager = RPCData(if_default_return_obj(obj=rpc,default=RPCData().get_default_rpc()))
        self.web3 = self.rpc_manager.w3
        self.private_key = self.check_priv_key(if_default_return_obj(obj=env_key,default=env_key))
        self.account_address = self.try_check_sum(if_default_return_obj(obj=self.web3.eth.accounts.privateKeyToAccount(self.private_key),default=address))
        self.nonce = self.get_transaction_count()
    def check_priv_key(self,priv_key):
        obj = get_env_value(key=private_key)
        if obj:
            return obj
        return priv_key
    def build_txn(self, contract_bridge,to_address):
        return contract_bridge.buildTransaction(self.get_txn_info(self, to_address, txn_value))
    def get_txn_info(self, to_address, txn_value):
        gas = self.estimate_gas(to_address,  self.account_address, txn_value)
        return {
            'to': to_address,
            'from': self.account_address,
            'value': txn_value,
            'gasPrice': 25000000000,
            'gas': gas,
            'nonce': self.nonce,
            'chainId': int(self.rpc_manager.chain_id)
        }
     def check_sum(self, address: str=None):
        """
        Convert the address to a checksum address.

        :param address: Ethereum address to convert.
        :return: Checksum Ethereum address.
        """
        address = if_default_return_obj(obj=self.contract_address,default=address)
        return self.rpc_manager.w3.to_checksum_address(address)
    def try_check_sum(self, address:str=None):
        """
        Attempt to convert the address to a checksum address.

        :param address: Ethereum address to convert.
        :return: Checksum Ethereum address.
        :raises ValueError: If the address is invalid.
        """
        address = if_default_return_obj(obj=self.contract_address,default=address)
        try:
            address = self.check_sum(address)
            return address
        except:
            raise ValueError("Invalid Ethereum Address")
    def get_transaction_count(self):
        return self.web3.eth.get_transaction_count(self.account_address)
    def sign_transaction(self, tx_info, private_key:str=None):
        return self.web3.eth.account.sign_transaction(tx_info, self.check_priv_key(if_default_return_obj(obj=private_key,default=env_key)))
    def send_transaction(self, tx_info, private_key:str=None):
        signed_txn = self.sign_transaction(txn_info=txn_info, private_key=self.check_priv_key(if_default_return_obj(obj=private_key,default=env_key)))
        return self.web3.eth.send_raw_transaction(signed_txn.rawTransaction)
    def estimate_gas(self, to_address, from_address, txn_value):
        return self.web3.eth.estimate_gas({"to": to_address,"from": from_address,"value": txn_value})
