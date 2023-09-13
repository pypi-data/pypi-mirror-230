from seaplane_framework.api.paths.object_bucket_name_store.get import ApiForget
from seaplane_framework.api.paths.object_bucket_name_store.put import ApiForput
from seaplane_framework.api.paths.object_bucket_name_store.delete import ApiFordelete


class ObjectBucketNameStore(
    ApiForget,
    ApiForput,
    ApiFordelete,
):
    pass
