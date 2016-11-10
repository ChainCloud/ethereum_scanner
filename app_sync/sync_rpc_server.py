import multiprocessing

import asyncio
from concurrent.futures import ThreadPoolExecutor

from constance import config
from mongoengine.connection import disconnect

from app_core.connectors import RpcServerConnector
from app_core.utils import timestamp_to_utc_datetime
from app_sync.mongo_models import Blocks, Transactions

from mongoengine import connect


threads_count = multiprocessing.cpu_count() * 2
THREAD_POOL = ThreadPoolExecutor(threads_count)


def add_block_to_mongo(web3, block_data):
    block = Blocks(**block_data)
    block.created = timestamp_to_utc_datetime(block_data['timestamp'])
    # TODO log exc
    block.save()
    for tx_hash in block.transactions:
        tx_data = web3.eth.getTransaction(tx_hash)
        tx_data['fromAddress'] = tx_data.pop('from')
        tx_data['toAddress'] = tx_data.pop('to')
        tx = Transactions(**tx_data)
        tx.block = block.id
        # TODO log exc
        tx.save()


def sync_block_and_txs(block, web3=None):
    if not web3:
        web3 = RpcServerConnector().get_connection()
    if isinstance(block, str):
        if Blocks.objects(hash=block).count():
            return
    elif isinstance(block, int):
        if Blocks.objects(number=block).count():
            return

    try:
        block_data = web3.eth.getBlock(block)
    except AttributeError:
        raise ValueError('block {} does not exist'.format(block))

    add_block_to_mongo(web3, block_data)


async def call_coroutines(sync_blocks):
    loop = asyncio.get_event_loop()
    futures = [
        loop.run_in_executor(THREAD_POOL, sync_block_and_txs, i, RpcServerConnector().get_connection())
        for i in sync_blocks]
    await asyncio.wait(futures)


def sync_blocks(start_block, end_block):
    connect(config.MONGO_DATABASE_NAME)

    loop = asyncio.get_event_loop_policy().new_event_loop()
    asyncio.set_event_loop(loop)
    loop = asyncio.get_event_loop()

    sync_position = start_block
    with THREAD_POOL:
        while sync_position <= end_block:
            sync_blocks = [i for i in range(sync_position, sync_position + threads_count) if i <= end_block]

            loop.run_until_complete(call_coroutines(sync_blocks))

            sync_position = sync_blocks[-1] + 1
        loop.close()

    disconnect(config.MONGO_DATABASE_NAME)

#        # test sync speed result
        # web3 = RpcServerConnector().get_connection()
        # for block in range(start_block, end_block):
        #     sync_block_and_txs(web3, block)
