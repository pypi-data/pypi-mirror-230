from py-scibec-openapi-client.paths.experiments_id.get import ApiForget
from py-scibec-openapi-client.paths.experiments_id.delete import ApiFordelete
from py-scibec-openapi-client.paths.experiments_id.patch import ApiForpatch


class ExperimentsId(
    ApiForget,
    ApiFordelete,
    ApiForpatch,
):
    pass
