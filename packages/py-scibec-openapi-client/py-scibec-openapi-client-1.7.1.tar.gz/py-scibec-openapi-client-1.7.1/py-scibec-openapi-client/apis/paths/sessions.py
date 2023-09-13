from py-scibec-openapi-client.paths.sessions.get import ApiForget
from py-scibec-openapi-client.paths.sessions.post import ApiForpost
from py-scibec-openapi-client.paths.sessions.patch import ApiForpatch


class Sessions(
    ApiForget,
    ApiForpost,
    ApiForpatch,
):
    pass
