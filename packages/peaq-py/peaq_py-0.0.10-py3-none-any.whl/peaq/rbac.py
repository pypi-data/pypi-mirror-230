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


def _rbac_rpc_fetch_entity(substrate, addr, entity, entity_id):
    return substrate.rpc_request(
        f'peaqrbac_fetch{entity}',
        [addr, entity_id]
    )['result']


def rbac_rpc_fetch_role(substrate, addr, entity_id):
    return _rbac_rpc_fetch_entity(substrate, addr, 'Role', entity_id)


def rbac_rpc_fetch_permission(substrate, addr, entity_id):
    return _rbac_rpc_fetch_entity(substrate, addr, 'Permission', entity_id)


def rbac_rpc_fetch_group(substrate, addr, entity_id):
    return _rbac_rpc_fetch_entity(substrate, addr, 'Group', entity_id)


# def rbac_rpc_fetch_entities(self, kp_src, entity, entity_ids, names):
#     data = self.substrate.rpc_request(
#         f'peaqrbac_fetch{entity}s',
#         [kp_src.ss58_address]
#     )
#     data = self.check_ok_wo_enable_and_return(data, len(entity_ids))
#     for i in range(0, len(names)):
#         data.index({
#             'id': entity_ids[i],
#             'name': [ord(x) for x in names[i]],
#             'enabled': True
#         })
#
# def rbac_rpc_fetch_group_roles(self, kp_src, group_id, role_ids):
#     data = self.substrate.rpc_request(
#         'peaqrbac_fetchGroupRoles',
#         [kp_src.ss58_address, group_id])
#     data = self.check_all_ok_and_return_all(data, len(role_ids))
#     for i in range(0, len(role_ids)):
#         data.index({
#             'role': role_ids[i],
#             'group': group_id
#         })
#
# def rbac_rpc_fetch_group_permissions(
#         self, kp_src, group_id, perm_ids, names):
#     data = self.substrate.rpc_request(
#         'peaqrbac_fetchGroupPermissions',
#         [kp_src.ss58_address, group_id])
#     data = self.check_ok_wo_enable_and_return(data, len(perm_ids))
#     for i in range(0, len(perm_ids)):
#         data.index({
#             'id': perm_ids[i],
#             'name': [ord(x) for x in names[i]],
#             'enabled': True
#         })
#
# def rbac_rpc_fetch_role_permissions(self, kp_src, role_id, perm_ids):
#     data = self.substrate.rpc_request(
#         'peaqrbac_fetchRolePermissions',
#         [kp_src.ss58_address, role_id])
#     data = self.check_all_ok_and_return_all(data, len(perm_ids))
#     for i in range(0, len(perm_ids)):
#         data.index({
#             'permission': perm_ids[i],
#             'role': role_id
#         })
#
# def rbac_rpc_fetch_user_roles(self, kp_src, user_id, role_ids):
#     data = self.substrate.rpc_request(
#         'peaqrbac_fetchUserRoles',
#         [kp_src.ss58_address, user_id])
#     data = self.check_all_ok_and_return_all(data, len(role_ids))
#     for i in range(0, len(role_ids)):
#         data.index({
#             'role': role_ids[i],
#             'user': user_id
#         })
#
# def rbac_rpc_fetch_user_groups(self, kp_src, user_id, group_ids):
#     data = self.substrate.rpc_request(
#         'peaqrbac_fetchUserGroups',
#         [kp_src.ss58_address, user_id])
#     data = self.check_all_ok_and_return_all(data, len(group_ids))
#     for i in range(0, len(group_ids)):
#         data.index({
#             'group': group_ids[i],
#             'user': user_id
#         })
#
# def rbac_rpc_fetch_user_permissions(
#         self, kp_src, user_id, perm_ids, names):
#     data = self.substrate.rpc_request(
#         'peaqrbac_fetchUserPermissions',
#         [kp_src.ss58_address, user_id])
#     data = self.check_ok_wo_enable_and_return(data, len(perm_ids))
#     for i in range(0, len(perm_ids)):
#         data.index({
#             'id': perm_ids[i],
#             'name': [ord(x) for x in names[i]],
#             'enabled': True
#         })
