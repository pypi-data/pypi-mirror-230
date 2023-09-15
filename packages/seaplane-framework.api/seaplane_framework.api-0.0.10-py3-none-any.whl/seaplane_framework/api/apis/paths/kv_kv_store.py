from seaplane_framework.api.paths.kv_kv_store.get import ApiForget
from seaplane_framework.api.paths.kv_kv_store.put import ApiForput
from seaplane_framework.api.paths.kv_kv_store.delete import ApiFordelete


class KvKvStore(
    ApiForget,
    ApiForput,
    ApiFordelete,
):
    pass
