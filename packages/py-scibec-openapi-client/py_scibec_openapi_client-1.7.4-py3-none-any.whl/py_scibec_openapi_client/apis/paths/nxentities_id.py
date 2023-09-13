from py_scibec_openapi_client.paths.nxentities_id.get import ApiForget
from py_scibec_openapi_client.paths.nxentities_id.put import ApiForput
from py_scibec_openapi_client.paths.nxentities_id.delete import ApiFordelete
from py_scibec_openapi_client.paths.nxentities_id.patch import ApiForpatch


class NxentitiesId(
    ApiForget,
    ApiForput,
    ApiFordelete,
    ApiForpatch,
):
    pass
