from py_scibec_openapi_client.paths.events.get import ApiForget
from py_scibec_openapi_client.paths.events.post import ApiForpost
from py_scibec_openapi_client.paths.events.patch import ApiForpatch


class Events(
    ApiForget,
    ApiForpost,
    ApiForpatch,
):
    pass
