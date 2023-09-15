""" 
create new dataset repository 
"""

from rich import print as rprint

from openxlab.dataset.commands.utility import ContextInfo
from openxlab.types.command_type import *


def create_repo(repo_name: str):
    """
    Create a dataset repository.

    Example:
        openxlab.dataset.create_repo(repo_name="dataset_repo_name")

    Parameters:
        @repo_name String The name of dataset repository.
    """
    ctx = ContextInfo()
    client = ctx.get_client()

    req_data_dict = {"name": f"{repo_name}", "displayname": f"{repo_name}"}

    resp_data_dict = client.get_api().create_dataset(req=req_data_dict)

    rprint(f"Dataset named: [blue]{resp_data_dict['name']}[/blue] create success!")
