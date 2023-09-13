from py_scibec_openapi_client.paths.experiments_id.get import ApiForget
from py_scibec_openapi_client.paths.experiments_id.delete import ApiFordelete
from py_scibec_openapi_client.paths.experiments_id.patch import ApiForpatch


class ExperimentsId(
    ApiForget,
    ApiFordelete,
    ApiForpatch,
):
    pass
