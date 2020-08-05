from jumpscale.core.exceptions import Input
from .crypto import encrypt_for_node
from .id import _next_workload_id
from jumpscale.clients.explorer.models import K8s, WorkloadType


class KubernetesGenerator:
    def __init__(self, explorer):
        self._nodes = explorer.nodes

    def add_master(self, node_id, network_name, cluster_secret, ip_address, size, ssh_keys, pool_id):
        """Add a master node to a kubernets cluster

        Args:
            reservation (jumpscale.clients.explorer.models.TfgridWorkloadsReservation1): reservation object
            node_id (str): Id of the node to be added
            network_name (str): name of the network to join
            cluster_secret (str): Secret of the cluster to be joined
            ip_address (str): Ip address of the master node
            size (int): size of master node, either 1 or 2
            ssh_keys (list, optional): List of ssh keys to be added to that node. Defaults to [].

        Raises:
            jumpscale.core.exceptions.Input: If size is not supported

        Returns:
            from jumpscale.clients.explorer.models.TfgridWorkloadsReservationK8s1: Master node
        """
        if size not in [1, 2]:
            raise Input("size can only be 1 or 2")

        master = K8s()
        master.info.node_id = node_id
        master.info.workload_type = WorkloadType.Kubernetes
        master.info.pool_id = pool_id

        node = self._nodes.get(node_id)
        master.cluster_secret = encrypt_for_node(node.public_key_hex, cluster_secret).decode()
        master.network_id = network_name
        master.ipaddress = ip_address
        master.size = size
        if not isinstance(ssh_keys, list):
            ssh_keys = [ssh_keys]
        master.ssh_keys = ssh_keys

        return master

    def add_worker(self, node_id, network_name, cluster_secret, ip_address, size, master_ip, ssh_keys, pool_id):
        """Add a worker node to a kubernets cluster

        Args:
            reservation (jumpscale.clients.explorer.models.TfgridWorkloadsReservation1): reservation object
            node_id (str): Id of the node to be added
            network_name (str): name of the network to join
            cluster_secret (str): Secret of the cluster to be joined
            ip_address (str): Ip address of the worker node
            size (int): size of master node, either 1 or 2
            master_ip (str): IP address of a master node
            ssh_keys (list, optional): List of ssh keys to be added to that node. Defaults to [].

        Raises:
            jumpscale.core.exceptions.Input: If size is not supported

        Returns:
            [type]: Worker node
        """
        worker = self.add_master(
            node_id=node_id,
            network_name=network_name,
            cluster_secret=cluster_secret,
            ip_address=ip_address,
            size=size,
            ssh_keys=ssh_keys,
            pool_id=pool_id,
        )
        worker.master_ips = [master_ip]
        return worker
