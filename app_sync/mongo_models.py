from mongoengine import StringField, IntField, ListField, FloatField, DynamicDocument, LongField


class EthBlocks(DynamicDocument):
    # totalDifficulty = LongField(required=True)
    mixHash = StringField(required=False)
    miner = StringField(required=True)
    gasUsed = IntField(required=True)
    logsBloom = StringField(required=True)
    sha3Uncles = StringField(required=True)
    uncles = ListField(required=False)
    extraData = StringField(required=True)
    difficulty = IntField(required=True)
    size = IntField(required=True)
    number = IntField(required=True, unique=True)
    transactionsRoot = StringField(required=True)
    timestamp = IntField(required=True)
    receiptRoot = StringField(required=False)
    receiptsRoot = StringField(required=False)
    parentHash = StringField(required=True)
    transactions = ListField(required=False)
    nonce = StringField(required=True)
    hash = StringField(required=True, unique=True)
    stateRoot = StringField(required=True)
    gasLimit = IntField(required=True)

    meta = {
        'indexes': [
            'number',
            'timestamp',
        ],
    }


class EthTransactions(DynamicDocument):
    fromAddress = StringField(required=True)
    toAddress = StringField(required=False)
    input = StringField(required=True)
    blockHash = StringField(required=True)
    hash = StringField(required=True, unique=True)
    nonce = IntField(required=True)
    value = FloatField(required=True)
    transactionIndex = IntField(required=True)
    gas = IntField(required=True)
    gasPrice = IntField(required=True)
    blockNumber = IntField(required=True)
    timestamp = IntField(required=True)

    meta = {
        'indexes': [
            'fromAddress',
            'toAddress',
            'hash',
            'blockNumber',
            'timestamp'

        ]
    }
