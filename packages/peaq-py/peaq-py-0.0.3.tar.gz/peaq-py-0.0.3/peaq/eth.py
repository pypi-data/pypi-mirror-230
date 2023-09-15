from substrateinterface.utils import hasher, ss58

ETH_CHAIN_IDS = {
    'peaq-dev': 9990,
    'agung-network': 9990,
    'krest-network': 2241,
    'peaq-network': 424242,
}


def get_eth_chain_id(substrate):
    chain_name = substrate.rpc_request(method='system_chain', params=[]).get('result')
    return ETH_CHAIN_IDS[chain_name]


def _calculate_evm_account(addr):
    evm_addr = b'evm:' + bytes.fromhex(addr[2:].upper())
    hash_key = hasher.blake2_256(evm_addr)
    return hash_key


def calculate_evm_account(addr):
    return ss58.ss58_encode(calculate_evm_account_hex(addr))


def calculate_evm_account_hex(addr):
    return '0x' + _calculate_evm_account(addr).hex()


def calculate_evm_addr(addr):
    return '0x' + ss58.ss58_decode(addr)[:40]
