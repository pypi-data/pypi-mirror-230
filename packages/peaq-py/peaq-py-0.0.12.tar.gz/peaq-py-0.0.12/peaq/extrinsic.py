# [TODO] Change API
def transfer_with_tip(substrate, kp_src, kp_dst_addr, token_num, tip, token_base=0):
    if not token_base:
        token_base = 10 ** 3

    nonce = substrate.get_account_nonce(kp_src.ss58_address)

    call = substrate.compose_call(
        call_module='Balances',
        call_function='transfer',
        call_params={
            'dest': kp_dst_addr,
            'value': token_num * token_base
        })

    extrinsic = substrate.create_signed_extrinsic(
        call=call,
        keypair=kp_src,
        era={'period': 64},
        tip=tip * token_base,
        nonce=nonce
    )

    receipt = substrate.submit_extrinsic(extrinsic, wait_for_inclusion=True)
    return receipt


# TODO Change API
def transfer(substrate, kp_src, kp_dst_addr, token_num, token_base=0):
    return transfer_with_tip(substrate, kp_src, kp_dst_addr, token_num, 0, token_base)
