from gevent import monkey

monkey.patch_all(subprocess=False)  # noqa: E402

import os
import requests
from jumpscale.loader import j
from jumpscale.packages.backup.actors.threebot_deployer import Backup


def main():
    BACKUP_ACTOR = Backup()

    instance_name = os.environ.get("INSTANCE_NAME")
    threebot_name = os.environ.get("THREEBOT_NAME")
    domain = os.environ.get("DOMAIN")
    backup_password = os.environ.get("BACKUP_PASSWORD", None)
    test_cert = os.environ.get("TEST_CERT")

    tname = f"{threebot_name}_{instance_name}"
    email = f"{tname}@threefold.me"
    words = j.data.encryption.key_to_mnemonic(backup_password.encode().zfill(32))

    new = True

    resp = requests.get("https://explorer.grid.tf/explorer/users", params={"name": tname})
    if resp.json():
        new = False

    j.logger.info("Generating guest identity ...")
    identity_main = j.core.identity.new(
        "main", tname=tname, email=email, words=words, explorer_url="https://explorer.grid.tf/explorer"
    )
    identity_test = j.core.identity.new(
        "test", tname=tname, email=email, words=words, explorer_url="https://explorer.testnet.grid.tf/api/v1"
    )

    identities = [identity_main, identity_test]
    for identity in identities:
        identity.admins.append(f"{threebot_name}.3bot")
        identity.register()
        identity.save()

    j.core.identity.set_default("test")

    if backup_password:
        try:
            BACKUP_ACTOR.init(backup_password, new=new)
            if not new:
                snapshots = j.data.serializers.json.loads(BACKUP_ACTOR.snapshots())
                if snapshots.get("data"):
                    j.logger.info("Restoring backup ...")
                    BACKUP_ACTOR.restore()
            else:
                j.logger.info("Taking backup ...")
                # Create a funded wallet to the threebot testnet
                j.clients.stellar.create_testwallet(f"{threebot_name}_{instance_name}")
                BACKUP_ACTOR.backup(tags="init")
        except Exception as e:
            j.logger.error(str(e))

    j.logger.info("Starting threebot ...")

    if test_cert == "true":
        j.servers.threebot.start_default(wait=True, local=False)
    else:
        j.servers.threebot.start_default(wait=True, local=False, domain=domain, email=email)


if __name__ == "__main__":
    main()
