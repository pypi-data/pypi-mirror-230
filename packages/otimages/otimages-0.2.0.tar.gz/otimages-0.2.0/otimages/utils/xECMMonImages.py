from . import ContainerImageList, ContainerImage
import logging
import os
import tempfile
import requests
import tarfile
import typer

from docker import DockerClient

logger = logging.getLogger("otimages." + os.path.basename(__file__))


class xECMMonImages(ContainerImageList):
    def __init__(
        self,
        version: str,
        docker_client: DockerClient,
        repository: str = "artifactory.otxlab.net",
        path: str = "/ot2-paas-dev/ecmcontainerization/",
        helm_base_url: str = "https://artifactory.otxlab.net/artifactory/ot2-helm-dev/ecm/",
        helm_dir: str = "",
        latest: bool = False,
    ):
        self.version = version
        self.repository = repository
        self.latest = latest
        self.docker_client = docker_client

        stage = "latest" if self.latest else "released"

        if (
            helm_base_url
            == "https://artifactory.otxlab.net/artifactory/ot2-helm-dev/ecm/"
        ):
            self.helm_base_url = helm_base_url + stage
        else:
            self.helm_base_url = helm_base_url

        self.path = path + stage

        if helm_dir == "":
            self.helm_dir = self.__get_helm_dir()
        else:
            self.helm_dir = helm_dir

        self.images = self.__get_images()

    def __get_helm_dir(self):
        temp_dir = tempfile.mkdtemp()
        helm_tgz = temp_dir + "/otxecm.tgz"

        logger.debug("Creating temporary directory for helm %s ", temp_dir)

        if self.latest:
            url = (
                self.helm_base_url
                + "/xecm-monitoring/xecm-mon-"
                + self.version
                + "-latest.tgz"
            )
        else:
            url = self.helm_base_url + "/xecm-mon-" + self.version + ".tgz"

        logger.debug("Downloading Helm Chart from %s", url)

        try:
            r = requests.get(url, timeout=10)
            with open(helm_tgz, "wb") as f:
                f.write(r.content)

            # open file
            file = tarfile.open(helm_tgz)
            file.extractall(temp_dir)
            file.close()

        except tarfile.ReadError:
            logger.error("Helmchart could not be downloaded from: %s", url)
            raise typer.Exit(code=1)

        except Exception as err:
            raise err

        return temp_dir + "/xecm-mon"

    def __get_images(self):
        logger.info(f"Running helm template for {self.version} in {self.helm_dir}")
        command = f"helm template xecm-mon {self.helm_dir} | yq '..|.image? | select(.)' | sort -u | grep registry.opentext.com | sed 's/registry.opentext.com\///g'"
        logger.debug(f"{command}")
        images = os.popen(command).readlines()

        all_images = []
        for image in images:
            name = image.split(":")[0]
            version = image.split(":")[1]
            all_images.append(
                ContainerImage(
                    repository=self.repository,
                    path=self.path,
                    name=name,
                    version=version,
                    docker_client=self.docker_client,
                )
            )
        all_images.append(
            ContainerImage(
                repository=self.repository,
                path=self.path,
                name="xecm-mon-operator",
                version=version,
                docker_client=self.docker_client,
            )
        )
        return all_images
