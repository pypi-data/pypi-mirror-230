from py_scibec_openapi_client.paths.datasets_id.get import ApiForget
from py_scibec_openapi_client.paths.datasets_id.delete import ApiFordelete
from py_scibec_openapi_client.paths.datasets_id.patch import ApiForpatch


class DatasetsId(
    ApiForget,
    ApiFordelete,
    ApiForpatch,
):
    pass
