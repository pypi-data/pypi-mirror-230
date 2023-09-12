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
