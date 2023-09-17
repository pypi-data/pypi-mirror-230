# vim:fenc=utf-8
#
# Copyright (C) 2023 dbpunk.com Author imotai <codego.me@gmail.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

""" """
from octopus_terminal.utils import parse_file_path


def test_parse_file_path_empty_string():
    assert parse_file_path("") == []


def test_parse_file_path_no_file_to_upload():
    assert parse_file_path("This is a prompt with no file to upload.") == []


def test_parse_file_path_one_file_to_upload():
    assert parse_file_path(
        "This is a prompt with one file to upload: /up file.txt"
    ) == ["file.txt"]


def test_parse_file_path_multiple_files_to_upload():
    assert parse_file_path(
        "This is a prompt with multiple files to upload: /up file1.txt /up file2.txt"
    ) == ["file1.txt", "file2.txt"]


def test_parse_file_path_file_with_space_in_the_name():
    assert parse_file_path(
        "This is a prompt with a file with space in the name: /up file with space.txt"
    ) == ["file"]


def test_parse_file_path_file_with_no_space_at_the_end():
    assert parse_file_path(
        "This is a prompt with a file with no space at the end: /up file.txt\n"
    ) == ["file.txt"]
