from py_scibec_openapi_client.paths.sessions.get import ApiForget
from py_scibec_openapi_client.paths.sessions.post import ApiForpost
from py_scibec_openapi_client.paths.sessions.patch import ApiForpatch


class Sessions(
    ApiForget,
    ApiForpost,
    ApiForpatch,
):
    pass
