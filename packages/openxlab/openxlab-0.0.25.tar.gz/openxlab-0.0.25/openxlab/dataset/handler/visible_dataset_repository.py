"""
update dataset repository
"""
from rich import print as rprint

from openxlab.dataset.commands.utility import ContextInfo
from openxlab.dataset.exception import *


def visibility(dataset_repo: str, private: bool):
    """
    set dataset visibility.

    Example:
        openxlab.dataset.visibility(
            dataset_repo="username/dataset_repo_name",
            private=True
        )

    Parameters:
        @dataset_repo String The address of dataset repository.
        @private String The visibility permission of repository.
    """
    ctx = ContextInfo()
    client = ctx.get_client()
    # parse dataset_name
    parsed_ds_name = dataset_repo.replace("/", ",")
    resp = client.get_api().set_repo_permission(parsed_ds_name, private)

    permission = 'private' if private else 'public'
    rprint(f"Visibility: [blue]{dataset_repo}[/blue] now is {permission}!")
