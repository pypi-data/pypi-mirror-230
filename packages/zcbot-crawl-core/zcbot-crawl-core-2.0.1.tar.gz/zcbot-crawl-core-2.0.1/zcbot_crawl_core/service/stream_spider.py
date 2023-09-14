# -*- coding: utf-8 -*-
from typing import List
from ..model.enums import CommonStatus
from ..util import logger
from ..dao import stream_spider as stream_spider_dao
from ..model.entity import StreamSpider

LOGGER = logger.get('流采爬虫')


def get_spiders(spider_ids: List[str], status: CommonStatus = CommonStatus.ON) -> List[StreamSpider]:
    rows = stream_spider_dao.get_stream_spider(spider_ids=spider_ids, status=status)
    rows = [StreamSpider(**x) for x in rows]
    return rows
