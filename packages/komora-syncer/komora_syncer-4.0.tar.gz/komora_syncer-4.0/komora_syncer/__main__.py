import logging
import traceback

import click

from komora_syncer.config import setup_logger
from komora_syncer.processors.Synchronizer import Synchronizer

SYNC_OPTIONS = ['all', 'organizations', 'regions', 'sites', 'devices', 'inventory']

# Initialize logging configuration
setup_logger()
logger = logging.getLogger(__name__)


@click.group()
def cli():
    pass


@click.command()
@click.option('--sync', '-s', type=click.Choice(SYNC_OPTIONS), multiple=True, default=['all'], help="what should be synced")
@click.option('--site', '-t', type=click.STRING, help="Name of site to deploy")
def synchronize(sync, site):
    """
    Synchronize data between Netbox and Komora
    """
    synchronizer = Synchronizer()

    if site and 'sites' not in sync:
        logger.critical(
            "Site option '--site' is only available with sites 'synchronize --sync sites' synchronization")
        logger.critical("Exiting")
        return

    if site and 'sites' in sync:
        try:
            # Syncs Sites / Site, Location
            synchronizer.sync_sites(site_name=site)
            return
        except Exception as e:
            logger.error(f"Unable to synchronize site '{site}' - {e}")
            logger.debug(f"{e}\n{traceback.format_exc()}")
            logger.critical("Exiting")
            return

    if 'all' in sync or 'organizations' in sync:
        try:
            # Syncs Organizations / Tenants
            synchronizer.sync_organizations()
        except Exception as e:
            logger.error(f"Unable to synchronize organizations")
            logger.debug(f"{e}\n{traceback.format_exc()}")
            logger.critical("Exiting")
            return

    if 'all' in sync or 'regions' in sync:
        try:
            # Syncs Regions, Disctricts and Municipalities / Regions
            synchronizer.sync_regions()
        except Exception as e:
            logger.error(f"Unable to synchronize regions")
            logger.debug(f"{e}\n{traceback.format_exc()}")
            logger.critical("Exiting")
            return

    if 'all' in sync or 'sites' in sync:
        try:
            # Syncs Sites / Site, Location
            synchronizer.sync_sites()
        except Exception as e:
            logger.error(f"Unable to synchronize sites")
            logger.debug(f"{e}\n{traceback.format_exc()}")
            logger.critical("Exiting")
            return

    if 'all' in sync or 'devices' in sync:
        try:
            synchronizer.sync_devices()
        except Exception as e:
            logger.error(f"Unable to synchronize devices")
            logger.debug(f"{e}\n{traceback.format_exc()}")
            logger.critical("Exiting")
            return

    if 'all' in sync or 'inventory' in sync:
        try:
            synchronizer.sync_inventory_items()
        except Exception as e:
            logger.error(f"Unable to synchronize inventories")
            logger.debug(f"{e}\n{traceback.format_exc()}")
            logger.critical("Exiting")
            return


cli.add_command(synchronize)


if __name__ == "__main__":
    # Display CLI
    cli()
