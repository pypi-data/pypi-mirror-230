import json
import logging
import os
from rich import console
from docker import DockerClient
from ..Exceptions.DockerException import DockerException


logger = logging.getLogger("otimages." + os.path.basename(__file__))

console = console.Console()


class ContainerImage:
    def __init__(
        self,
        docker_client: DockerClient,
        repository: str = "artifactory.otxlab.net",
        path: str = "",
        name: str = "",
        version: str = "",
        name_overwrite: str = "",
        version_overwrite: str = "",
    ):
        """CotainerImage class that can be used to pull and push Images to a different repo.

        Args:
            repository (str, optional): _description_. Defaults to "artifactory.otxlab.net".
            path (str, optional): _description_. Defaults to "".
            name (str, optional): _description_. Defaults to "".
            version (str, optional): _description_. Defaults to "".
            name_overwrite (str, optional): _description_. Defaults to "".
            version_overwrite (str, optional): _description_. Defaults to "".
        """
        self.repository = repository
        self.path = path
        self.name = name
        self.version = version.strip()
        self.pulled = False
        self.docker_client = docker_client

        if name_overwrite == "":
            self.name_overwrite = name
        else:
            self.name_overwrite = name_overwrite

        if version_overwrite == "":
            self.version_overwrite = version
        else:
            self.version_overwrite = version_overwrite

        self.image = None

        logger.debug("ContainerImage defined: %s", self.fullPath())

    def __str__(self) -> str:
        return self.fullPath()

    def fullPath(self) -> str:
        return f"{self.repository}{self.path}/{self.name}:{self.version}"

    def targetPath(self, repository: str, path: str = "") -> str:
        if path == "":
            target = f"{repository}/{self.name_overwrite}:{self.version_overwrite}"
        else:
            target = (
                f"{repository}/{path}/{self.name_overwrite}:{self.version_overwrite}"
            )
        target = target.strip()
        return target

    def pull(self) -> bool:
        logger.info("Pulling image: %s", self.fullPath())

        try:
            self.image = self.docker_client.images.pull(repository=self.fullPath())

        except NameError:
            logger.error("Run DockerInit() before working with images")
            exit()
        except Exception as err:
            self.pulled = False
            logger.error("Pulling of image {self.fullPath()} failed. %s", err)
        else:
            self.pulled = True

        return self.pulled

    def push(self, repository: str, path: str = "", **kwargs) -> bool:
        if not self.pulled:
            logger.debug("Image not yet pulled. Starting pull")
            if not self.pull():
                return False

        target = self.targetPath(repository, path)

        logger.info("Pushing image")
        logger.info("from: %s", self.fullPath())
        logger.info("to:   %s", target)

        try:
            self.image.tag(target)

            push_output = self.docker_client.images.push(target, **kwargs)
            for line in push_output.splitlines():
                parsed_line = json.loads(line)
                if "error" in parsed_line:
                    raise DockerException(parsed_line)

        except Exception as err:
            logger.error("Pushing of image %s failed. %s", target, err)
            return False

        return True

    def print(self):
        console.print(f"{self.repository}{self.path}/", end="")
        console.print(self.name, end="", style="red")
        console.print(":", end="")
        console.print(self.version)
