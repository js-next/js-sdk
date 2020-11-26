from .size import VDCFlavor
from .vdc import UserVDC

from jumpscale.loader import j
from jumpscale.core.base import StoredFactory

VDC_INSTANCE_NAME_FORMAT = "vdc_{}_{}"


class VDCStoredFactory(StoredFactory):
    def new(self, vdc_name, owner_tname, flavor):
        if isinstance(flavor, str):
            flavor = VDCFlavor(flavor.lower())
        owner_tname = j.data.text.removesuffix(owner_tname, ".3bot")
        instance_name = VDC_INSTANCE_NAME_FORMAT.format(vdc_name, owner_tname)
        return super().new(instance_name, vdc_name=vdc_name, owner_tname=owner_tname, flavor=flavor)

    def find(self, name=None, vdc_name=None, owner_tname=None, load_info=False):
        owner_tname = j.data.text.removesuffix(owner_tname, ".3bot") if owner_tname else None
        instance_name = name or VDC_INSTANCE_NAME_FORMAT.format(vdc_name, owner_tname)
        instance = super().find(instance_name)
        if not instance:
            return
        if owner_tname and instance.owner_tname != owner_tname:
            return
        if load_info:
            instance.load_info()
        return instance

    def list(self, owner_tname, load_info=False):
        owner_tname = j.data.text.removesuffix(owner_tname, ".3bot")
        _, _, instances = self.find_many(owner_tname=owner_tname)
        if not load_info:
            return instances

        result = []
        for instance in instances:
            instance.load_info()
            result.append(instance)
        return result


VDCFACTORY = VDCStoredFactory(UserVDC)
VDCFACTORY.always_relaod = True


def export_module_as():
    return VDCFACTORY
