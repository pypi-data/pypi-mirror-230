from py-scibec-openapi-client.paths.events_id.get import ApiForget
from py-scibec-openapi-client.paths.events_id.put import ApiForput
from py-scibec-openapi-client.paths.events_id.delete import ApiFordelete
from py-scibec-openapi-client.paths.events_id.patch import ApiForpatch


class EventsId(
    ApiForget,
    ApiForput,
    ApiFordelete,
    ApiForpatch,
):
    pass
