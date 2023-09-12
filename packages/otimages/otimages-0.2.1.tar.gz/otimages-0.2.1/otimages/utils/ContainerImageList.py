from operator import length_hint
from . import ContainerImage

from rich.progress import track, Progress, BarColumn, TextColumn


class ContainerImageList:
    def __init__(self, images, docker_client_args={}):
        self.images = images
        self.docker_client_args = docker_client_args

    def list(self):
        for image in self.images:
            image.print()

    def pull(self):
        with Progress() as progress:
            task = progress.add_task("Pulling ... ", total=len(self.images))
            for image in self.images:
                progress.console.print(f"Pulling {image.fullPath()}")
                image.pull()
                progress.advance(task)

    def push(self, repository, path, **kwargs):
        with Progress() as progress:
            task = progress.add_task(
                f"Publishing ...",
                total=len(self.images) * 2,
            )
            for image in self.images:
                progress.console.print(f"Pulling {image.fullPath()}", style="")
                image.pull()
                progress.advance(task)

                progress.console.print(f"Pushing {image.targetPath(repository, path)}")
                image.push(repository, path, **kwargs)
                progress.advance(task)

    def append(self, image: ContainerImage):
        self.images.append(image)

    def include(self, filter: str):
        filter_list = filter.split(",")  # Split the comma-separated filters into a list

        # Use list comprehension to filter self.images based on any of the filters
        self.images = [
            image for image in self.images if any(f in image.name for f in filter_list)
        ]

    def exclude(self, filter: str):
        filter_list = filter.split(",")  # Split the comma-separated filters into a list

        # Use list comprehension to filter self.images based on any of the filters
        self.images = [
            image
            for image in self.images
            if not any(f in image.name for f in filter_list)
        ]
