from main10 import MysqlRowsCompare
from config import args_source_dsn, args_target_dsn

import logging

mrc = MysqlRowsCompare(
    1,
    logging,
    args_source_dsn,
    args_target_dsn,
    "merchant_center_vela_v1",
    "mc_products_cms",
    [("products_id", "int"), ("languages_id", "int")],
)

mrc.compare(
    [
        {"products_id": 407262, "languages_id": 29},
        {"products_id": 407366, "languages_id": 29},
    ]
)
