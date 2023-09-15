from peaq.utils import ExtrinsicBatch


# [TODO] Change the API, kp_dst to addr
def fund(substrate, kp_sudo, kp_dst, new_free, new_reserved=0):
    batch = ExtrinsicBatch(substrate, kp_sudo)
    batch.compose_sudo_call(
        'Balances',
        'set_balance',
        {
            'who': kp_dst.ss58_address,
            'new_free': new_free,
            'new_reserved': 0
        }
    )
    return batch.execute()
