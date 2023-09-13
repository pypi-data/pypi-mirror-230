import os
import shutil
import tempfile

import pytest

from seeq.spy.docs import _copy


@pytest.mark.unit
def test_copy():
    with tempfile.TemporaryDirectory() as temp_folder:
        long_folder_name = os.path.join(temp_folder, 'long_' * 10)
        _copy.copy(long_folder_name)

        assert os.path.exists(long_folder_name)

        with pytest.raises(RuntimeError):
            _copy.copy(long_folder_name)

        assert os.path.exists(long_folder_name)

        _copy.copy(long_folder_name, overwrite=True, advanced=True)

        assert os.path.exists(long_folder_name)
        assert os.path.exists(os.path.join(long_folder_name, 'spy.workbooks.ipynb'))
        assert os.path.exists(os.path.join(long_folder_name, 'Asset Trees 3 - Report and Dashboard Templates.ipynb'))

        shutil.rmtree(long_folder_name)
