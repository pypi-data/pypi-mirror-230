from peaq.utils import ExtrinsicBatch


# [TODO] Change the API, kp_dst to addr
def transfer(substrate, kp_src, kp_dst, token_num):
    batch = ExtrinsicBatch(substrate, kp_src)
    batch.compose_call(
        'Balances',
        'transfer',
        {
            'dest': kp_dst.ss58_address,
            'value': token_num
        })
    return batch.execute()
