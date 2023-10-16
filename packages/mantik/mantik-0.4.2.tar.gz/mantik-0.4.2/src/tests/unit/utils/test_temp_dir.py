import os

import mantik.utils.temp_dir as temp_dir


def test_use_temp_dir():
    @temp_dir.use_temp_dir
    def return_temp_dir_name(temp_dir_name=None):
        assert os.path.exists(temp_dir_name)
        return temp_dir_name

    assert not os.path.exists(return_temp_dir_name())
