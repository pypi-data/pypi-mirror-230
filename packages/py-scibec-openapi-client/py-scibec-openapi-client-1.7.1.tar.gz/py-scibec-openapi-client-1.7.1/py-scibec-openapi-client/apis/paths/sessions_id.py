from py-scibec-openapi-client.paths.sessions_id.get import ApiForget
from py-scibec-openapi-client.paths.sessions_id.delete import ApiFordelete
from py-scibec-openapi-client.paths.sessions_id.patch import ApiForpatch


class SessionsId(
    ApiForget,
    ApiFordelete,
    ApiForpatch,
):
    pass
