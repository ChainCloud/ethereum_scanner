from django.core.management.base import BaseCommand, CommandError

from app_core.connectors import RpcServerConnector
from app_sync.sync_rpc_server import sync_db_with_rpc_server


class Command(BaseCommand):
    help = 'Sync local database with blockchain'

    def add_arguments(self, parser):
        parser.add_argument('block-start', nargs='+', type=int)
        parser.add_argument('block-end', nargs='+', type=int)

    # TODO logger - synced
    def handle(self, *args, **options):

        end_block = options['block-end'][0]
        start_block = options['block-start'][0]

        sync_db_with_rpc_server(start_block, end_block)

        self.stdout.write(self.style.SUCCESS('Successfully synced "%s" blocks' % (end_block - start_block + 1)))
