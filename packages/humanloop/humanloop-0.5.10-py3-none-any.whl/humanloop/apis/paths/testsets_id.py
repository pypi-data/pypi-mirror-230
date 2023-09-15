from humanloop.paths.testsets_id.get import ApiForget
from humanloop.paths.testsets_id.delete import ApiFordelete
from humanloop.paths.testsets_id.patch import ApiForpatch


class TestsetsId(
    ApiForget,
    ApiFordelete,
    ApiForpatch,
):
    pass
