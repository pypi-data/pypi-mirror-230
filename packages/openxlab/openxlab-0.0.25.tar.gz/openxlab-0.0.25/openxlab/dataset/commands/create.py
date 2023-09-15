""" 
create dataset repository-cli
"""
from openxlab.dataset.handler.create_dataset_repository import create_repo
from openxlab.types.command_type import *


class Create(BaseCommand):
    """Create a dataset repository."""

    def get_name(self) -> str:
        return "create"

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.usage = (
            'openxlab dataset create [OPTIONS]\n\n'
            "Create a dataset repository.\n\n"
            'Example:\n'
            '> openxlab dataset create --repo-name \"dataset_repo_name\"'
        )
        parser.add_argument(
            "--repo-name",
            required=True,
            help='The name of dataset repository.[required]',
        )

    def take_action(self, parsed_args: Namespace) -> int:
        create_repo(repo_name=parsed_args.repo_name)

        return 0
