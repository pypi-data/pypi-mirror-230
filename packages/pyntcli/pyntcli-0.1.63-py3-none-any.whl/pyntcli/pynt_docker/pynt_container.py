import docker
from docker.errors import DockerException, APIError, ImageNotFound
from docker.types import Mount
import os
import argparse
from typing import List

from pyntcli.ui import ui_thread
from pyntcli.analytics import send as analytics
from pyntcli.store import CredStore
from pyntcli.auth.login import PYNT_CREDENTIALS , PYNT_SAAS

PYNT_DOCKER_IMAGE = "ghcr.io/pynt-io/pynt"

def create_mount(src, destination, mount_type="bind"):
    return Mount(target=destination, source=src, type=mount_type)

class DockerNotAvailableException(Exception):
    pass

class ImageUnavailableException(Exception):
    pass

def get_docker_type():
    try:
        c = docker.from_env()
        version_data = c.version()
        platform = version_data.get("Platform")

        if platform and platform.get("Name"):
            return platform.get("Name")
        
        return ""

    except DockerException:
        raise DockerNotAvailableException()
    except Exception: #TODO: This is since windows is not behaving nice
        raise DockerNotAvailableException()


class PyntBaseConatiner():
    def __init__(self,docker_type,docker_arguments,mounts, environment={}) -> None:
        self.docker_type = docker_type
        self.docker_arguments = docker_arguments
        self.mounts = mounts
        self.environment = environment

class PyntDockerPort:
    def __init__(self, src, dest, name) -> None:
        self.src = src
        self.dest = dest
        self.name = name

def get_container_with_arguments(args: argparse.Namespace , *port_args: PyntDockerPort) -> PyntBaseConatiner:
    docker_arguments = []
    if "desktop" in get_docker_type().lower():
        ports = {}
        for p in port_args:
            ports[str(p.src)] = int(p.dest)
        docker_type = PyntDockerDesktopContainer(ports=ports)
    else:
        docker_type = PyntNativeContainer(network="host")
        for p in port_args: 
            docker_arguments.append(p.name)
            docker_arguments.append(str(p.dest))
   
    if "insecure" in args and args.insecure:
        docker_arguments.append("--insecure")
    
    if "application_id" in args and args.application_id: 
        docker_arguments += ["--application-id",args.application_id]

    if "dev_flags" in args: 
        docker_arguments += args.dev_flags.split(" ")
    
    mounts = []
    if "host_ca" in args and args.host_ca:
        ca_name = os.path.basename(args.host_ca)
        docker_arguments += ["--host-ca", ca_name]
        mounts.append(create_mount(os.path.abspath(args.host_ca), "/etc/pynt/{}".format(ca_name)))
    
    env = {PYNT_CREDENTIALS:CredStore().get_access_token(), "PYNT_SAAS_URL": PYNT_SAAS}

    return PyntBaseConatiner(docker_type, docker_arguments, mounts, env)
    
def _container_image_from_tag(tag: str) -> str:
    if ":" in tag: 
        return tag.split(":")[0]

    return tag

class PyntContainer():
    def __init__(self, image_name, tag, detach, base_container: PyntBaseConatiner) -> None:
        self.docker_client: docker.DockerClient = None
        self.image = image_name if not os.environ.get("IMAGE") else os.environ.get("IMAGE")
        self.tag = tag if not os.environ.get("TAG") else os.environ.get("TAG")
        self.detach = detach
        self.stdout = None 
        self.running = False
        self.container_name = ""
        self.base_container = base_container

    
    def _create_docker_client(self):
        self.docker_client = docker.from_env()
        pat = os.environ.get("DOCKER_PASSWORD")
        username = os.environ.get("DOCKER_USERNAME")
        registry = os.environ.get("DOCKER_REGISTRY")
        if pat and username and registry:
            self.docker_client.login(username=username, password=pat, registry=registry)
    
    def _is_docker_image_up_to_date(self, image):
        return True
    
    def _handle_outdated_docker_image(self, image):
        return image
    
    def kill_other_instances(self):
        for c in self.docker_client.containers.list():
            if len(c.image.tags) and _container_image_from_tag(c.image.tags[0]) == self.image:
                c.kill()
    
    def stop(self):
        if not self.running:
            return 

        self.kill_other_instances()

        self.docker_client.close()
        self.docker_client = None
        self.running = False
    
    def is_alive(self):
        if not self.docker_client or not self.container_name:
            return False

        l = self.docker_client.containers.list(filters={"name": self.container_name})
        if len(l) != 1:
            return False
        
        return l[0].status == "running"
    
    def pull_image(self):
        try:
            return self.docker_client.images.pull(self.image, tag=self.tag)
        except APIError as e:
            analytics.emit(analytics.ERROR,{"error": "Unable to pull image from ghcr: {}".format(e)})
            return None

    def get_image(self):
        try:
            image = self.pull_image()
            if not image:
                image = self.docker_client.images.get('{}:{}'.format(self.image,self.tag))
            return image
        except ImageNotFound:
            raise ImageUnavailableException()

    def run(self): 
        if not self.docker_client:
            self._create_docker_client()
        
        self.running = True
        self.kill_other_instances()

        ui_thread.print(ui_thread.PrinterText("Pulling latest docker", ui_thread.PrinterText.INFO))
        image = self.get_image()
        ui_thread.print(ui_thread.PrinterText("Docker pull done", ui_thread.PrinterText.INFO))
    
        args = self.base_container.docker_arguments if self.base_container.docker_arguments else None
            

        run_arguments = {
                "image":image, 
                "detach":self.detach,
                "mounts":self.base_container.mounts,
                "environment": self.base_container.environment,
                "stream": True,
                "remove": True,
                "command": args
        }

        run_arguments.update(self.base_container.docker_type.get_argumets())

        c = self.docker_client.containers.run(**run_arguments)
        self.container_name = c.name
        self.stdout = c.logs(stream=True)

        PyntContainerRegistery.instance().register_container(self)

class PyntDockerDesktopContainer():
    def __init__(self, ports) -> None:
        self.ports = ports
    
    def get_argumets(self):
        return {"ports": self.ports} if self.ports else {}
        
class PyntNativeContainer():
    def __init__(self, network) -> None:
        self.network = network

    def get_argumets(self):
        return {"network": self.network} if self.network else {}


class PyntContainerRegistery():
    _instance = None

    def __init__(self) -> None:
        self.containers: List[PyntContainer] = []

    @staticmethod
    def instance():
        if not PyntContainerRegistery._instance:
            PyntContainerRegistery._instance = PyntContainerRegistery() 

        return PyntContainerRegistery._instance

    def register_container(self, c: PyntContainer):
        self.containers.append(c) 
    
    def stop_all_containers(self):
        for c in self.containers: 
            c.stop()
