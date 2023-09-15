import hcl2

from typing import List

from pydriller.repository import Repository
from pydriller.domain.commit import ModificationType

from repominer import filters, utils
from repominer.mining.ansible_modules import DATABASE_MODULES, FILE_MODULES, IDENTITY_MODULES, NETWORK_MODULES, \
    STORAGE_MODULES
from repominer.mining.base import BaseMiner, FixingCommitClassifier

CONFIG_DATA_MODULES = DATABASE_MODULES + FILE_MODULES + IDENTITY_MODULES + NETWORK_MODULES + STORAGE_MODULES


class TerraformMiner(BaseMiner):
    """ This class extends BaseMiner to mine Terraform-based repositories
    """

    def __init__(self, url_to_repo: str, clone_repo_to: str, branch: str = None):
        super(self.__class__, self).__init__(url_to_repo, clone_repo_to, branch)
        self.FixingCommitClassifier = TerraformFixingCommitClassifier

    def ignore_file(self, path_to_file: str, content: str = None):
        """
        Ignore non-Terraform files.

        Parameters
        ----------
        path_to_file: str
            The filepath (e.g., repominer/mining/base.py).

        content: str
            The file content.

        Returns
        -------
        bool
            True if the file is not a Terraform file, and must be ignored. False, otherwise.

        """
        return not filters.is_terraform_file(path_to_file)


class TerraformFixingCommitClassifier(FixingCommitClassifier):
    """ This class extends a FixingCommitClassifier to classify bug-fixing commits of Terraform files.
    """
    # Il metodo data changed non lo posso sovrascrivere perchè esiste un corrispettivo dei moduli in terraform
    # la categoria è troppo generica e lo script sarebbe incredibile complesso

    def is_include_changed(self) -> bool:
        for modified_file in self.commit.modified_files:
            if modified_file.change_type != ModificationType.MODIFY or not filters.is_terraform_file(
                    modified_file.new_path):
                continue

            try:

                source_code_before = hcl2.loads(modified_file.source_code_before)
                source_code_current = hcl2.loads(modified_file.source_code)

                modules_before = source_code_before['module']
                modules_current = source_code_current['module']

                return modules_before != modules_current

            except Exception:
                pass

        return False
