import math
import os
import asyncio
import functools
import re
from datetime import datetime, timedelta
from .utils import get

res = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'template')

# type 0 普通常驻任务深渊 1 新闻 2 蛋池 3 限时活动H5
event_data = {
    'cn': [],
}

event_updated = {
    'cn': '',
}

lock = {
    'cn': asyncio.Lock(),
}

ignored_key_words = [
    '有奖问卷',
    '公平运营',
    '防沉迷',
    '游戏优化',
    '保密测试',
    '社群',
    '社媒聚合页'
]

ignored_ann_ids = [
    '194',
    '185'
]

list_api = 'https://hkrpg-api.mihoyo.com/common/hkrpg_cn/announcement/api/getAnnList?game=hkrpg&game_biz=hkrpg_cn&lang=zh-cn&bundle_id=hkrpg_cn&platform=pc&region=prog_gf_cn&level=55&uid=100000000'
detail_api = 'https://hkrpg-api.mihoyo.com/common/hkrpg_cn/announcement/api/getAnnContent?game=hkrpg&game_biz=hkrpg_cn&lang=zh-cn&bundle_id=hkrpg_cn&platform=pc&region=prod_gf_cn&level=55&uid=100000000'


def cache(ttl=timedelta(hours=1), arg_key=None):
    def wrap(func):
        cache_data = {}

        @functools.wraps(func)
        async def wrapped(*args, **kw):
            nonlocal cache_data
            default_data = {"time": None, "value": None}
            ins_key = 'default'
            if arg_key:
                ins_key = arg_key + str(kw.get(arg_key, ''))
                data = cache_data.get(ins_key, default_data)
            else:
                data = cache_data.get(ins_key, default_data)

            now = datetime.now()
            if not data['time'] or now - data['time'] > ttl:
                try:
                    data['value'] = await func(*args, **kw)
                    data['time'] = now
                    cache_data[ins_key] = data
                except Exception as e:
                    raise e

            return data['value']

        return wrapped

    return wrap


@cache(ttl=timedelta(hours=3), arg_key='url')
async def query_data(url):
    try:
        req = await get(url)
        return req.json()
    except:
        pass
    return None


async def load_event_cn():
    result = await query_data(url=list_api)
    detail_result = await query_data(url=detail_api)
    if result and 'retcode' in result and result['retcode'] == 0 and detail_result and 'retcode' in detail_result and \
            detail_result['retcode'] == 0:
        event_data['cn'] = []
        event_detail = {}
        for data in detail_result['data']['list']:
            event_detail[data['ann_id']] = data

            ignore = False
            for ann_id in ignored_ann_ids:
                if ann_id == data["ann_id"]:
                    ignore = True
                    break
            if ignore:
                continue

            for keyword in ignored_key_words:
                if keyword in data['title']:
                    ignore = True
                    break
            if ignore:
                continue

            if event_detail[data["ann_id"]]:
                content = event_detail[data["ann_id"]]['content']
                searchObj = re.search(
                    r'(\d+)\/(\d+)\/(\d+)\s(\d+):(\d+):(\d+)', content, re.M | re.I)
                try:
                    datelist = searchObj.groups()  # ('2021', '9', '17')
                    ctime = datetime.strptime(
                            f'{datelist[0]}-{datelist[1]}-{datelist[2]} {datelist[3]}:{datelist[4]}:{datelist[5]}', r"%Y-%m-%d %H:%M:%S")
                except Exception as e:
                    pass

            event = {
                'title': data['title'],
                'banner': data['banner'],
                'color': '#2196f3',
                'start': None,
                'end': ctime
            }
            if '概率UP' in data['title']:
                event['start'] = '版本更新后'
                event['color'] = '#73BF00'
                event['banner'] = data['banner']

            if '无名勋礼' in data['title']:
                event['start'] = '版本更新后'
                event['color'] = '#F00078'
                event['banner'] = data['banner']

            if '位面分裂' in data['title']:
                content = event_detail[data["ann_id"]]['content']
                Obj = re.findall(r'&lt;t class=\"t_lc\"&gt;(\d+)\/(\d+)\/(\d+)\s(\d+):(\d+):(\d+)&lt;/t&gt;', content)

                start = datetime.strptime(
                        f'{Obj[0][0]}-{Obj[0][1]}-{Obj[0][2]} {Obj[0][3]}:{Obj[0][4]}:{Obj[0][5]}', r"%Y-%m-%d %H:%M:%S")
                end = datetime.strptime(
                        f'{Obj[1][0]}-{Obj[1][1]}-{Obj[1][2]} {Obj[1][3]}:{Obj[1][4]}:{Obj[1][5]}', r"%Y-%m-%d %H:%M:%S")

                event['start'] = datetime.strftime(start, r"%m-%d")
                event['end'] = end
                event['color'] = '#E9AB17'
                event['banner'] = data['banner']

            event_data['cn'].append(event)
        return 0
    return 1


async def load_event(server):
    if server == 'cn':
        return await load_event_cn()
    return 1


async def get_events(server, offset, days):
    events = []
    pcr_now = datetime.now()
    if pcr_now.hour < 4:
        pcr_now -= timedelta(days=1)
    pcr_now = pcr_now.replace(
        hour=18, minute=0, second=0, microsecond=0)  # 用晚6点做基准

    await lock[server].acquire()
    try:
        t = pcr_now.strftime('%y%m%d')
        if event_updated[server] != t:
            if await load_event(server) == 0:
                event_updated[server] = t
    finally:
        lock[server].release()

    start = pcr_now + timedelta(days=offset)
    end = start + timedelta(days=days)
    end -= timedelta(hours=18)  # 晚上12点结束

    for event in event_data[server]:
        event['left_days'] = math.floor((event['end'] - start) / timedelta(days=1))  # 还有几天结束
        events.append(event)

    return events
