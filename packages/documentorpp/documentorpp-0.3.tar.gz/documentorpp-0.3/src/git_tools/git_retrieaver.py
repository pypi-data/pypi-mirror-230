from git_tools.git_manager import GitManager
from metaclasses.no_instanciable_meta import NoInstanciable
from pathlib import Path
from pygit2 import Blob


class GitRetrieaver(metaclass=NoInstanciable):
    @staticmethod
    def retrieve_file(file_path: Path) -> str:
        file_git_id = (GitRetrieaver.get_file_git_object(file_path)).oid
        file_git_blob = GitManager.project_repo()[file_git_id]
        file_bytes_data = file_git_blob.data
        file_worked_data = file_bytes_data.decode("utf-8")
        return file_worked_data

    @staticmethod
    def get_file_git_object(file_path: Path) -> Blob:
        path_way = str(file_path).split("\\")
        current_object = GitManager.selected_commit_tree()
        for path in path_way:
            if path in current_object:
                current_object = current_object[path]
            else:
                raise Exception("Git_Retriever_Error: Not object found in git tree.")
        return current_object
