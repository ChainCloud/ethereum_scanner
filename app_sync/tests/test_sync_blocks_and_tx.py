import copy
from unittest import TestCase
from unittest.mock import patch

import pytz
from constance import config
from mongoengine import connect
from mongoengine.connection import disconnect
from pymongo import MongoClient
from web3.eth import Eth

from app_core.connectors import RpcServerConnector
from app_core.tests.utils import set_mongo_test_db
from app_core.utils import timestamp_to_utc_datetime
from app_sync.sync_rpc_server import sync_blocks, sync_block_and_txs
from app_sync.tests.data_for_tests import test_block_data, test_tx_data


class SyncBlocksTestCase(TestCase):
    def setUp(self):
        super(SyncBlocksTestCase, self).setUp()
        self.test_block_data = test_block_data
        self.test_tx_data = test_tx_data

    @patch.object(Eth, 'getTransaction')
    @patch.object(Eth, 'getBlock')
    @set_mongo_test_db
    def test_sync_blocks(self, mock_get_block, mock_get_transaction):
        mock_get_block.return_value = copy.deepcopy(self.test_block_data)
        mock_get_transaction.return_value = copy.deepcopy(self.test_tx_data)

        sync_blocks(1, 1)

        client = MongoClient()
        db = client[config.MONGO_TEST_DATABASE_NAME]

        self.assertEqual(db.blocks.count(), 1)
        self.assertEqual(db.transactions.count(), 1)


class SyncBlocksAndTxsTestCase(TestCase):
    def setUp(self):
        super(SyncBlocksAndTxsTestCase, self).setUp()
        self.test_block_data = test_block_data
        self.test_tx_data = test_tx_data
        self.web3 = RpcServerConnector().get_connection()

    @patch.object(Eth, 'getTransaction')
    @patch.object(Eth, 'getBlock')
    @set_mongo_test_db
    def test_sync_block_with_tx_by_number(self, mock_get_block, mock_get_transaction):
        mock_get_block.return_value = copy.deepcopy(self.test_block_data)
        mock_get_transaction.return_value = copy.deepcopy(self.test_tx_data)

        connect(config.MONGO_DATABASE_NAME)

        sync_block_and_txs(1, self.web3)

        disconnect(config.MONGO_DATABASE_NAME)

        client = MongoClient()
        db = client[config.MONGO_TEST_DATABASE_NAME]

        self.assertEqual(db.blocks.count(), 1)
        self.assertEqual(db.transactions.count(), 1)

        block = db.blocks.find_one()
        self.assertEqual(self.test_block_data['hash'], block['hash'])
        self.assertEqual(timestamp_to_utc_datetime(self.test_block_data['timestamp']),
                         block['created'].replace(tzinfo=pytz.utc))

        tx = db.transactions.find_one()
        self.assertEqual(self.test_tx_data['hash'], tx['hash'])
        self.assertEqual(self.test_tx_data['to'], tx['toAddress'])
        self.assertEqual(self.test_tx_data['from'], tx['fromAddress'])
        self.assertEqual(block['_id'], tx['block'])
