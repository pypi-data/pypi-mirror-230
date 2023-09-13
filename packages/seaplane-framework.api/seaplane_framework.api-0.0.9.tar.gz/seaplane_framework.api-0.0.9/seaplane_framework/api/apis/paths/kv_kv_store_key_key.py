from seaplane_framework.api.paths.kv_kv_store_key_key.get import ApiForget
from seaplane_framework.api.paths.kv_kv_store_key_key.put import ApiForput
from seaplane_framework.api.paths.kv_kv_store_key_key.delete import ApiFordelete


class KvKvStoreKeyKey(
    ApiForget,
    ApiForput,
    ApiFordelete,
):
    pass
