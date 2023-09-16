import os
import time

from typing import Dict, List

from eai_commons.utils import file
from eai_commons_tests.unit_tests import executor


def test_file_relative_path():
    source_path = __file__
    print(source_path)
    dest_abs_path = file.file_relative_path(source_path, "../../../README.md")
    print(dest_abs_path)


def test_get_file_extension():
    source_path = __file__
    dest_abs_path = file.file_relative_path(source_path, "../../../README.md")
    extension_ = file.get_file_extension(dest_abs_path)
    assert extension_ == ".md"


def test_load_json_file():
    source_path = __file__
    json_obj_path = file.file_relative_path(source_path, "../../resources/json_object.json")
    dict_ = file.load_json_file(json_obj_path)
    assert isinstance(dict_, (dict, Dict))
    json_array_path = file.file_relative_path(source_path, "../../resources/json_array.json")
    list_ = file.load_json_file(json_array_path)
    assert isinstance(list_, (list, List))


def test_create_directory():
    test_dir = file.file_relative_path(__file__, "../../resources/test_dir")
    file.create_directory(test_dir)

    assert os.path.exists(test_dir)
    os.removedirs(test_dir)

    task = [test_dir for _ in range(8)]
    executor.map(file.create_directory, task)

    time.sleep(1)
    assert os.path.exists(test_dir)
    os.removedirs(test_dir)


def test_dicts_to_csv_file():
    dicts = [{
        "name": "周杰伦",
        "song": "兰亭序"
    }]
    test_csv_file = file.file_relative_path(__file__, "../../resources/test_csv_file.csv")
    generate = file.dicts_to_csv_file(test_csv_file, dicts)
    assert generate

    os.remove(test_csv_file)


def test_csv_file_to_dicts():
    csv_file = file.file_relative_path(__file__, "../../resources/csv_file.csv")
    dicts = file.csv_file_to_dicts(csv_file)
    assert isinstance(dicts, list)
    assert len(dicts) > 0
    print(dicts)
