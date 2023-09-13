from py_scibec_openapi_client.paths.events_id.get import ApiForget
from py_scibec_openapi_client.paths.events_id.put import ApiForput
from py_scibec_openapi_client.paths.events_id.delete import ApiFordelete
from py_scibec_openapi_client.paths.events_id.patch import ApiForpatch


class EventsId(
    ApiForget,
    ApiForput,
    ApiFordelete,
    ApiForpatch,
):
    pass
