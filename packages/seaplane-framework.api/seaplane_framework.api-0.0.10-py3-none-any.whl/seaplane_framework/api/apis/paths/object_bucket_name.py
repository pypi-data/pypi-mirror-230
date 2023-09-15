from seaplane_framework.api.paths.object_bucket_name.get import ApiForget
from seaplane_framework.api.paths.object_bucket_name.put import ApiForput
from seaplane_framework.api.paths.object_bucket_name.delete import ApiFordelete


class ObjectBucketName(
    ApiForget,
    ApiForput,
    ApiFordelete,
):
    pass
