import docker.errors


class DockerException(docker.errors.DockerException):
    """
    Raised if a remote docker repository returns an error. Usually due to a failed push or pull.
    """

    def __init__(self, error_dict):
        self.response = error_dict["error"]
        self.explanation = error_dict["errorDetail"]["message"]
