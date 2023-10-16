import pytest

import mantik.remote_file_service.s3_file_service as s3_fs


@pytest.mark.parametrize(
    "path,expected",
    [
        ("s3://bucket/resource.item", True),
        ("folder/sub-folder/resource.item", False),
    ],
)
def test_is_remote(path: str, expected: bool) -> None:
    assert s3_fs.is_remote(path) == expected


@pytest.mark.parametrize(
    "path,expected",
    [
        ("s3://bucket-name/resource.item", "resource.item"),
        ("s3://bucket-name", ""),
    ],
)
def test_localise_path(path, expected) -> None:
    assert s3_fs.localise_path(path) == expected


@pytest.mark.parametrize(
    "path,expected",
    [
        ("s3://bucket-name/resource.item", "bucket-name"),
        ("folder/sub-folder/resource.item", "ValueError"),
    ],
)
def test_get_bucket_name(path, expected) -> None:
    if expected == "ValueError":
        with pytest.raises(ValueError):
            s3_fs.get_bucket_name(path)
            return
    else:
        assert s3_fs.get_bucket_name(path) == expected
