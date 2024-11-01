from rococo.repositories.mysql import MySqlRepository
from common.models import BillingInfo


class BillingInfoRepository(MySqlRepository):
    def __init__(self, adapter, message_adapter, message_queue_name):
        super().__init__(adapter, BillingInfo, message_adapter, message_queue_name)
