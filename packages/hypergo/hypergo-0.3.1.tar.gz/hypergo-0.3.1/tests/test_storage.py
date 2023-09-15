import unittest
from typing import Any

from hypergo.storage import Storage, SubStorage


class TestStorage(unittest.TestCase):
    def test_abstract_instantiation(self) -> None:
        with self.assertRaises(TypeError):
            storage: Storage = Storage()

    def test_use_sub_path(self) -> None:
        base_storage: Storage = StorageMock()
        sub_path: str = "subfolder"
        sub_storage: Storage = base_storage.use_sub_path(sub_path)
        self.assertIsInstance(sub_storage, SubStorage)
        self.assertIs(sub_storage._base_storage, base_storage)
        self.assertEqual(sub_storage._sub_path, sub_path)

    def test_sub_storage_load(self) -> None:
        file_name: str = "test.txt"
        content: str = "Hello, world!"
        sub_path: str = "subfolder"
        base_storage: Storage = StorageMock(f"{sub_path}/{file_name}", content)
        sub_storage: Storage = SubStorage(base_storage, sub_path)
        result: str = sub_storage.load(file_name)
        self.assertEqual(result, content)

    def test_sub_storage_save(self) -> None:
        file_name: str = "test.txt"
        content: str = "Hello, world!"
        base_storage: Storage = StorageMock()
        sub_path: str = "subfolder"
        sub_storage: Storage = SubStorage(base_storage, sub_path)
        sub_storage.save(file_name, content)
        self.assertEqual(base_storage.saved_files, {f"{sub_path}/{file_name}": content})


class StorageMock(Storage):
    def __init__(self, file_name: str = "", content: str = "") -> None:
        self.saved_files: dict[str, str] = {}
        if file_name:
            self.save(file_name, content)

    def load(self, file_name: str) -> str:
        return self.saved_files.get(file_name)

    def save(self, file_name: str, content: str) -> None:
        self.saved_files[file_name] = content


if __name__ == '__main__':
    unittest.main()
