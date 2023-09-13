# -*- coding: utf-8 -*-
from typing import Optional, List
from ..client.mongo_client import Mongo
from ..model.entity import StreamSpider
from ..model.enums import CommonStatus


# 获取portainer爬虫配置
def get_stream_spider(spider_ids: List[str], status: CommonStatus) -> Optional[StreamSpider]:
    row = Mongo().get('zcbot_stream_spider', {'spiderId': {'$in': spider_ids}, 'status': status.name})
    if not row:
        return None
    return StreamSpider(**row)


# 获取支持网站平台
def get_platforms_by_spider_id(spider_ids: List[str], status: CommonStatus):
    return Mongo().aggregate('zcbot_platforms', [
        {
            '$lookup': {
                'from': 'zcbot_stream_spider',
                'localField': '_id',
                'foreignField': 'plat_code',
                'as': 'spider'
            }
        },
        {
            '$match': {'spider._id': {'$in': spider_ids}, 'status': status.name}
        },
        {
            '$project': {'spider': 0}
        },
        {'$sort': {'sort': 1}}
    ])
