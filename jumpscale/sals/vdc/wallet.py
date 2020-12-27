from jumpscale.clients.stellar.stellar import Network as StellarNetwork
from jumpscale.core.base import Base, StoredFactory, fields
from jumpscale.loader import j


class VDCWallet(Base):
    vdc_uuid = fields.String()
    wallet_secret = fields.String()
    wallet_network = fields.Enum(StellarNetwork)

    def _init_wallet(self, secret=None):
        if "testnet" in j.core.identity.me.explorer_url or "devnet" in j.core.identity.me.explorer_url:
            self.wallet_network = StellarNetwork.TEST
        else:
            self.wallet_network = StellarNetwork.STD

        wallet = j.clients.stellar.new(self.instance_name, secret=secret, network=self.wallet_network)
        if not secret:
            wallet.activate_through_friendbot()
            if "devnet" not in j.core.identity.me.explorer_url:
                wallet.add_known_trustline("TFT")
        wallet.save()
        self.wallet_secret = wallet.secret

    @property
    def stellar_wallet(self):
        if not j.clients.stellar.find(self.instance_name) and self.wallet_secret:
            self._init_wallet(self.wallet_secret)
        return j.clients.stellar.get(self.instance_name)


class VDCWalletStoredFactory(StoredFactory):
    def new(self, *args, **kwargs):
        instance = super().new(*args, **kwargs)
        instance._init_wallet()
        instance.save()
        return instance


VDC_WALLET_FACTORY = VDCWalletStoredFactory(VDCWallet)
VDC_WALLET_FACTORY.always_reload = True