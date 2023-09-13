import pytest
from gwlandscape_python.utils import file_filters
from gwlandscape_python import FileReference, FileReferenceList


@pytest.fixture
def data():
    return FileReferenceList([
        FileReference(
            path='data/dir/test1.h5',
            file_size='1',
            download_token='test_token_1',
            job_id='id'
        ),
        FileReference(
            path='data/dir/test2.h5',
            file_size='1',
            download_token='test_token_2',
            job_id='id'
        ),
    ])


@pytest.fixture
def other():
    return FileReferenceList([
        FileReference(
            path='result/dir/test1.png',
            file_size='1',
            download_token='test_token_3',
            job_id='id'
        ),
        FileReference(
            path='result/dir/test2.txt',
            file_size='1',
            download_token='test_token_4',
            job_id='id'
        ),
        FileReference(
            path='result/dir/h5.txt',
            file_size='1',
            download_token='test_token_5',
            job_id='id'
        ),
        FileReference(
            path='result/dir/h5',
            file_size='1',
            download_token='test_token_6',
            job_id='id'
        ),
    ])


@pytest.fixture
def full(data, other):
    return data + other


def test_data_file_filter(full, data):
    sub_list = file_filters.data_filter(full)
    assert file_filters.sort_file_list(sub_list) == file_filters.sort_file_list(data)
