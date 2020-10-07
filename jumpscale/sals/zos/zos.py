import binascii

from jumpscale.clients.explorer.conversion import AlreadyConvertedError
from jumpscale.clients.explorer.models import Reservation
from jumpscale.clients.explorer.workloads import Decoder
from jumpscale.core import identity
from jumpscale.loader import j

from .billing import Billing
from .container import ContainerGenerator
from .gateway import GatewayGenerator
from .gateway_finder import GatewayFinder
from .kubernetes import KubernetesGenerator
from .network import NetworkGenerator
from .node_finder import NodeFinder
from .pools import Pools
from .reservation import Reservation
from .signature import sign_workload
from .volumes import VolumesGenerator
from .workloads import Workloads
from .zdb import ZDBGenerator


class Zosv2:
    """ """

    @property
    def _explorer(self):
        return j.core.identity.me.explorer

    @property
    def network(self):
        return NetworkGenerator(self._explorer)

    @property
    def container(self):
        return ContainerGenerator()

    @property
    def volume(self):
        return VolumesGenerator()

    @property
    def zdb(self):
        return ZDBGenerator(self._explorer)

    @property
    def kubernetes(self):
        return KubernetesGenerator(self._explorer)

    @property
    def nodes_finder(self):
        return NodeFinder(self._explorer)

    @property
    def gateways_finder(self):
        return GatewayFinder(self._explorer)

    @property
    def billing(self):
        return Billing()

    @property
    def pools(self):
        return Pools(self._explorer)

    @property
    def workloads(self):
        return Workloads(self._explorer)

    @property
    def gateway(self):
        return GatewayGenerator(self._explorer)

    def conversion(self):
        me = j.core.identity.me

        try:
            raw = self._explorer.conversion.initialize()
        except AlreadyConvertedError as err:
            j.logger.info(str(err))
            return

        if raw:
            for i, data in enumerate(raw):
                w = Decoder.from_dict(datadict=data)
                signature = sign_workload(w, me.nacl.signing_key)
                raw[i]["customer_signature"] = binascii.hexlify(signature).decode()

            self._explorer.conversion.finalize(raw)

    def _escrow_to_qrcode(self, escrow_address, escrow_asset, total_amount, message="Grid resources fees"):
        """Converts escrow info to qrcode

        Args:
          escrow_address(str): escrow address
          total_amount(float): total amount of the escrow
          message(str, optional): message encoded in the qr code. Defaults to "Grid resources fees".
          escrow_asset:

        Returns:
          str: qrcode string representation

        """
        qrcode = f"{escrow_asset}:{escrow_address}?amount={total_amount}&message={message}&sender=me"
        return qrcode
