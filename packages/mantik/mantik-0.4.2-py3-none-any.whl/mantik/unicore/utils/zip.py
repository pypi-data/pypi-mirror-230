import io
import os
import pathlib
import tempfile
import typing as t
import zipfile

import mantik.unicore.config.core as core
import mantik.unicore.utils.upload as upload_files


def zip_directory_with_exclusion(
    path: pathlib.Path, config: core.Config
) -> t.BinaryIO:
    """Zip given directory."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        with zipfile.ZipFile(tmp_dir + "/zip_tmp", "w") as zipwriter:
            for filepath in upload_files.get_files_to_upload(path, config):
                zip_path = os.path.relpath(filepath, path)
                zipwriter.write(filepath, zip_path)
            zipwriter.close()
        with open(tmp_dir + "/zip_tmp", "rb") as f:
            content = f.read()
        return io.BytesIO(content)
