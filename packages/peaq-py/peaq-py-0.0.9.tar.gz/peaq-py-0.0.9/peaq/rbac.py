from peaq.utils import ExtrinsicBatch


def _comp_rbac_call(batch, cl_fcn, cl_par):
    batch.compose_call(
        'PeaqRbac',
        cl_fcn,
        cl_par
    )


def rbac_add_role_payload(batch, entity_id, name):
    _comp_rbac_call(
        batch,
        'add_role',
        {
            'role_id': entity_id,
            'name': name,
        })


def rbac_add_role(substrate, kp_src, entity_id, name):
    batch = ExtrinsicBatch(substrate, kp_src)
    rbac_add_role_payload(batch, entity_id, name)
    return batch.execute_receipt()


def rbac_add_group_payload(batch, group_id, name):
    _comp_rbac_call(
        batch,
        'add_group',
        {
            'group_id': group_id,
            'name': name,
        })


def rbac_add_group(substrate, kp_src, group_id, name):
    batch = ExtrinsicBatch(substrate, kp_src)
    rbac_add_group_payload(batch, group_id, name)
    return batch.execute_receipt()


def rbac_add_permission_payload(batch, permission_id, name):
    _comp_rbac_call(
        batch,
        'add_permission',
        {
            'permission_id': permission_id,
            'name': name,
        })


def rbac_add_permission(substrate, kp_src, permission_id, name):
    batch = ExtrinsicBatch(substrate, kp_src)
    rbac_add_permission_payload(batch, permission_id, name)
    return batch.execute_receipt()


def rbac_permission2role_payload(batch, permission_id, role_id):
    _comp_rbac_call(
        batch,
        'assign_permission_to_role',
        {
            'permission_id': permission_id,
            'role_id': role_id,
        })


def rbac_permission2role(substrate, kp_src, permission_id, role_id):
    batch = ExtrinsicBatch(substrate, kp_src)
    rbac_permission2role_payload(batch, permission_id, role_id)
    return batch.execute_receipt()


def rbac_role2group_payload(batch, role_id, group_id):
    _comp_rbac_call(
        batch,
        'assign_role_to_group',
        {
            'role_id': role_id,
            'group_id': group_id,
        })


def rbac_role2group(substrate, kp_src, role_id, group_id):
    batch = ExtrinsicBatch(substrate, kp_src)
    rbac_role2group_payload(batch, role_id, group_id)
    return batch.execute_receipt()


def rbac_role2user_payload(batch, role_id, user_id):
    _comp_rbac_call(
        batch,
        'assign_role_to_user',
        {
            'role_id': role_id,
            'user_id': user_id,
        })


def rbac_role2user(substrate, kp_src, role_id, user_id):
    batch = ExtrinsicBatch(substrate, kp_src)
    rbac_role2user_payload(batch, role_id, user_id)
    return batch.execute_receipt()


def rbac_user2group_payload(batch, user_id, group_id):
    _comp_rbac_call(
        batch,
        'assign_user_to_group',
        {
            'user_id': user_id,
            'group_id': group_id,
        })


def rbac_user2group(substrate, kp_src, user_id, group_id):
    batch = ExtrinsicBatch(substrate, kp_src)
    rbac_user2group_payload(batch, user_id, group_id)
    return batch.execute_receipt()


def rbac_disable_group_payload(batch, group_id):
    _comp_rbac_call(
        batch,
        'disable_group',
        {
            'group_id': group_id,
        })


def rbac_disable_group(substrate, kp_src, group_id):
    batch = ExtrinsicBatch(substrate, kp_src)
    rbac_disable_group_payload(batch, group_id)
    return batch.execute_receipt()
