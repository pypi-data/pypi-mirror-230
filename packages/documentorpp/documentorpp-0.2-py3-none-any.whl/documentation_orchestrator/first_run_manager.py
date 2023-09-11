from git_tools.git_file_paths import GitFilePaths
from git_tools.git_manager import GitManager
from repository_scrapping.file_scrapper import FileScrapper
from snippet_management.snippet_storage import SnippetStorage
from metaclasses.singleton_meta import SingletonMeta
from typing import ClassVar


class FirstRunManager(metaclass=SingletonMeta):
    instance: ClassVar = None
    _snippets_to_doc: SnippetStorage
    _first_run_scrapper: FileScrapper

    def __init__(self):
        self._snippets_to_doc = SnippetStorage()
        self._first_run_scrapper = FileScrapper()

    def _start_first_run(self):
        GitManager.select_front_commit()
        self._first_run_scrapper.scrape_specified(GitFilePaths.get_all_valid_paths())
        all_snippets_to_doc_dict = self._first_run_scrapper.storage_dict
        self._snippets_to_doc.update_storage(all_snippets_to_doc_dict)

    @staticmethod
    def start_first_run():
        FirstRunManager.instance._start_first_run()

    @staticmethod
    def get_snippets_to_doc() -> SnippetStorage:
        return FirstRunManager.instance._snippets_to_doc


FirstRunManager()
