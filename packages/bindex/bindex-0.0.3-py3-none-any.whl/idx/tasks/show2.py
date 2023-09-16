from __future__ import annotations

import asyncio
from enum import IntEnum
from typing import Any, Final, cast
import typer
from beni import bcolor, bhttp, bstore, btask
from beni.bfunc import Counter, syncCall, toAny
from prettytable import PrettyTable

_renameDict: dict[str, str] = {
    'SHS红利成长LV(人民币)': 'SHS红利成长LV',
    'MSCI中国A股国际通实时(人民币)': 'MSCI',
}

_disabledDict: dict[str, str] = {
    # '中证煤炭': '强周期',
}

_fundDict: dict[str, str] = {
}

_groupSet: dict[str, set[str]] = {
    '红利': {
        'SHS红利成长LV',
        '红利低波',
        '中证红利',
        '上证红利',
    },
}
_groupDict = {name: groupName for groupName, nameSet in _groupSet.items() for name in nameSet}

app: Final = btask.app

_indexes: list[Index] = []


@app.command('show')
@syncCall
async def show(
    clear: bool = typer.Option(False, '--clear-cache', '-c', help="清空缓存重新请求"),
    is_desc: bool = typer.Option(False, '--desc', '-d', help="显示指数描述"),
):
    '展示指数信息'
    storeKey = 'xxiioo'
    if clear:
        bcolor.printYellow('清空缓存')
        await bstore.clear(storeKey)
    cache = await bstore.get(storeKey)
    if cache:
        bcolor.printYellow('使用缓存')
        _indexes.extend(toAny(cache))
    if not _indexes:
        categories = await _getCategories()
        await asyncio.gather(*[
            _getIndexes(k, v) for k, v in categories.items()
        ])
        await asyncio.gather(*[
            _getIndexData(x) for x in _indexes
        ])
        for item in [x for x in _indexes if not hasattr(x, 'pe')]:
            _indexes.remove(item)
        await bstore.set(storeKey, _indexes)
    if not _indexes:
        btask.abort('数据异常，无法获取数据')

    _handle()
    await _sortIndexes()
    await _showDisabledTable(is_desc)
    await _showTable(is_desc)


async def _getCategories():
    '获取指数分类'
    url = 'https://danjuanfunds.com/djapi/fundx/base/index/category'
    data = await bhttp.getJson(url)
    result: dict[str, set[str]] = {}
    for item in data['data']['items']:
        categoryName = item['category_name']
        subCategoryNames = set([x['sub_category_name'] for x in item['subs']])
        result[categoryName] = subCategoryNames
    return result

_indexIdSet: set[str] = set()


async def _getIndexes(categoryName: str, subCategoryNames: set[str]):
    '获取有估值的指数'
    url = 'https://danjuanfunds.com/djapi/fundx/base/index/sub_desc?category_name={0}&sub_names={1}'
    url = url.format(categoryName, ','.join(subCategoryNames))
    data = await bhttp.getJson(url)
    ary: list[Any] = []
    for item in data['data']['items']:
        ary.extend(item['index_desc_vos'])
    # {'symbol': 'CSI930949', 'name': '价值回报', 'desc': 'xx', 'nav_grw_td': 0.14, 'nav_grw_r1y': -13.1165, 'transaction_heat': 0, 'eva_type': 'low'}
    for item in ary:
        if item['eva_type'] != 'unsort':
            indexId = item['symbol']
            indexName = item['name']
            if indexId not in _indexIdSet:
                _indexIdSet.add(indexId)
                _indexes.append(
                    Index(indexId, indexName)
                )


async def _getIndexData(index: Index):
    '获取指数数据'
    detailUrl = 'https://danjuanfunds.com/djapi/index_eva/detail/{0}'
    data: dict[str, Any] = await bhttp.getJson(detailUrl.format(index.id))
    if data.get('data'):
        baseData = data['data']
        descUrl = 'https://danjuanfunds.com/djapi/fundx/base/index/detail?symbol={0}'
        data = await bhttp.getJson(descUrl.format(index.id))
        desc = (cast(dict[str, str], data['data'])).get('desc', '')
        historyUrl = 'https://danjuanfunds.com/djapi/index_eva/{0}_history/{1}?day=all'
        data = await bhttp.getJson(historyUrl.format('pe', index.id))
        peList = [x['pe'] for x in data['data']['index_eva_pe_growths']]
        data = await bhttp.getJson(historyUrl.format('roe', index.id))
        roeList = [x['roe'] for x in data['data']['index_eva_roe_growths']]
        index.update(
            desc,
            baseData,
            peList,
            roeList,
        )


def _handle():
    # 重命名
    for item in _indexes:
        item.name = _renameDict.get(item.name, item.name)
    # isPb 自动添加到 disabledDict
    for item in _indexes:
        if item.isPb:
            if item.name not in _disabledDict:
                _disabledDict[item.name] = '强周期'


async def _sortIndexes():
    '指数综合排序'
    ary1 = sorted(_indexes, key=lambda x: x.pe)
    ary2 = sorted(_indexes, key=lambda x: x.roe, reverse=True)
    _indexes.clear()
    for i in range(1, len(ary1) + 1):
        xx = set(ary1[:i]).intersection(set(ary2[:i]))
        subAry = list(xx - set(_indexes))
        subAry.sort(key=lambda x: (x.pe, x.roe))
        _indexes.extend(subAry)
    aryLow: list[Index] = []
    aryMiddle: list[Index] = []
    aryHigh: list[Index] = []
    for item in _indexes:
        if item.group is IndexGroup.low:
            aryLow.append(item)
        elif item.group is IndexGroup.high:
            aryHigh.append(item)
        else:
            aryMiddle.append(item)
    _indexes.clear()
    _indexes.extend(aryLow + aryMiddle + aryHigh)


async def _showDisabledTable(isShowDesc: bool):
    table = PrettyTable()
    table.title = bcolor.magenta('屏蔽的指数')
    table.field_names = [bcolor.magenta(x) for x in ['排序', '指数名称', '屏蔽原因', '描述']]
    counter = Counter()
    ary = [x for x in _indexes if x.name in _disabledDict.keys()]
    ary.sort(key=lambda x: _disabledDict.get(x.name, ''))
    for item in ary:
        reason = _disabledDict[item.name]
        table.add_row([
            counter(),
            item.name,
            reason,
            item.desc,
        ])
    table.print_empty = True
    print(
        table.get_string(
            fields=table.field_names[:len(table.field_names) - 0 if isShowDesc else -1]
        )
    )


async def _showTable(isShowDesc: bool):
    table = PrettyTable()
    table.title = bcolor.magenta('关注的指数')
    table.field_names = [bcolor.magenta(x) for x in ['排序', '指数名称', '百分位', 'PE', 'ROE', '分组', '基金', '描述']]
    for fieldName in ['排序', '百分位', 'PE/PB', 'ROE']:
        table.align[bcolor.magenta(fieldName)] = 'r'
    counter = Counter()
    outputDict = {
        IndexGroup.low: bcolor.green,
        IndexGroup.high: bcolor.red,
    }
    for item in filter(lambda x: x.name not in _disabledDict, _indexes):
        output = outputDict.get(item.group, bcolor.yellow)
        table.add_row([output(x) for x in [
            str(counter()),
            item.name,
            f'{item.pePercentile*100:.2f}%',
            f'{item.pe:.2f}',
            f'{item.roe*100:.2f}%',
            _groupDict.get(item.name, ''),
            _fundDict.get(item.name, ''),
            item.desc,
        ]])
    print(
        table.get_string(
            fields=table.field_names[:len(table.field_names) - 0 if isShowDesc else -1]
        )
    )


class IndexGroup(IntEnum):
    low = 1
    middle = 2
    high = 3


class Index:

    def __init__(self, id: str, name: str) -> None:
        self.id = id
        self.name = name

    def update(self, desc: str, data: dict[str, Any], peList: list[float], roeList: list[float]):
        self.desc = desc
        self.yeild = float(data['yeild'])
        self.isPb = not not data['pb_flag']
        if peList:
            self.pe = peList[-1]
            ary = sorted(peList)
            self.pePercentile = ary.index(self.pe) / len(ary)
        if roeList:
            self.roe = sum(roeList) / len(roeList)

    @property
    def group(self):
        if self.pePercentile < 0.3:
            return IndexGroup.low
        elif self.pePercentile > 0.7:
            return IndexGroup.high
        else:
            return IndexGroup.middle

# todo 增加分组，避免买入时候过于集中
# todo 找出每个指数对应的购买基金
