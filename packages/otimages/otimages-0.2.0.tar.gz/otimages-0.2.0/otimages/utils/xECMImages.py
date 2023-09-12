from . import ContainerImageList, ContainerImage
import logging
import os
import tempfile
import requests
import tarfile
import typer

from docker import DockerClient

logger = logging.getLogger("otimages." + os.path.basename(__file__))


class xECMImages(ContainerImageList):
    def __init__(
        self,
        docker_client: DockerClient,
        version: str,
        repository: str = "artifactory.otxlab.net",
        path: str = "/ot2-paas-dev/ecmcontainerization/",
        helm_base_url: str = "https://artifactory.otxlab.net/artifactory/ot2-helm-dev/ecm/",
        helm_dir: str = "",
        langpacks: bool = False,
        latest: bool = False,
    ):
        self.version = version
        self.repository = repository
        self.latest = latest
        self.langpacks = langpacks
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
            url = self.helm_base_url + "/otxecm/otxecm-" + self.version + "-latest.tgz"
        else:
            url = self.helm_base_url + "/otxecm-" + self.version + ".tgz"

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

        return temp_dir + "/otxecm"

    def __get_images(self):
        logger.debug(
            "Updating %s/platforms/azure.yaml with .global.masterPassword",
            self.helm_dir,
        )

        os.popen(
            f"yq -i '.global.masterPassword = \"Opentext1!\"' {self.helm_dir}/platforms/azure.yaml"
        ).readlines()

        logger.info(
            "Running helm template for %s in %s",
            self.version,
            self.helm_dir,
        )
        if os.path.isfile(f"{self.helm_dir}/otxecm-image-tags.yaml"):
            tagsfile = f"-f {self.helm_dir}/otxecm-image-tags.yaml"
        else:
            tagsfile = ""

        command = f"helm template {self.helm_dir} {tagsfile} -f {self.helm_dir}/platforms/azure.yaml --set global.otpd.enabled=true --set otpd.loadLicense=false --set global.ingressEnabled=false --set otcs.config.documentStorage.type=database --set otiv.amqp.rabbitmq.password=test --set otds.otdsws.cryptKey=12dghfgdh3 --set otds.otdsws.otdsdb.username=otds --set otac.database.port=5432 --set otac.database.name=ac --set otac.database.hostname=otxecm-db --set otac.database.username=ac --set otds.otdsws.otdsdb.password=Opentext1! | yq '..|.image? | select(.)' | sort -u | grep registry.opentext.com | sed 's/registry.opentext.com\///g'"
        logger.debug("%s", command)
        images = os.popen(command).readlines()

        all_images = []
        for image in images:
            name = image.split(":")[0]
            version = image.split(":")[1]
            version_overwrite = version

            if self.latest and name == "otxecm":
                version = version.rsplit(".", 1)[0]

            all_images.append(
                ContainerImage(
                    repository=self.repository,
                    path=self.path,
                    name=name,
                    version=version,
                    version_overwrite=version_overwrite,
                    docker_client=self.docker_client,
                )
            )

        if self.langpacks:
            langpacks_containers = [
                "otxecm-init-lang-ar",
                "otxecm-init-lang-ca-es",
                "otxecm-init-lang-cs-cz",
                "otxecm-init-lang-da-dk",
                "otxecm-init-lang-de",
                "otxecm-init-lang-es",
                "otxecm-init-lang-fi-fi",
                "otxecm-init-lang-fr",
                "otxecm-init-lang-he",
                "otxecm-init-lang-it",
                "otxecm-init-lang-iw",
                "otxecm-init-lang-ja",
                "otxecm-init-lang-kk-kz",
                "otxecm-init-lang-ko-kr",
                "otxecm-init-lang-nb-no",
                "otxecm-init-lang-nl",
                "otxecm-init-lang-pl-pl",
                "otxecm-init-lang-pt",
                "otxecm-init-lang-ru-ru",
                "otxecm-init-lang-sv",
                "otxecm-init-lang-tr-tr",
                "otxecm-init-lang-uk-ua",
                "otxecm-init-lang-zh-cn",
                "otxecm-init-lang-zh-tw",
            ]
            version = self.version.rsplit(".", 1)[0] + ".0"

            for image in langpacks_containers:
                all_images.append(
                    ContainerImage(
                        repository=self.repository,
                        path=self.path,
                        name=image,
                        version=version,
                        docker_client=self.docker_client,
                    )
                )

        return all_images
