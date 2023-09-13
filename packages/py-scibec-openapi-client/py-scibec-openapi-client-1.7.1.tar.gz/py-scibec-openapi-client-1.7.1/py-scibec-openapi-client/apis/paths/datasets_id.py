from py-scibec-openapi-client.paths.datasets_id.get import ApiForget
from py-scibec-openapi-client.paths.datasets_id.delete import ApiFordelete
from py-scibec-openapi-client.paths.datasets_id.patch import ApiForpatch


class DatasetsId(
    ApiForget,
    ApiFordelete,
    ApiForpatch,
):
    pass
