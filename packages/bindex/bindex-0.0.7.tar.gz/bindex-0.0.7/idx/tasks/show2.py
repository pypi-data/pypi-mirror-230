from __future__ import annotations

import asyncio
import datetime
from enum import IntEnum
from typing import Any, Final, cast

import typer
from beni import bcolor, bhttp, bstore, btask, btime
from beni.bfunc import Counter, syncCall, toAny
from beni.btype import Null
from prettytable import PrettyTable

_BUY_COUNT = 3

# 首选基金
_FUND_DICT: dict[str, str] = {
    '中证红利': '易方达中证红利ETF联接A（009051）',
    '央视50': '招商央视财经50指数A（217027）',
    '沪深300': '易方达沪深300ETF联接A（110020）',
    '上证红利': '华泰柏瑞红利ETF联接A（012761）',
    '深证红利': '工银深证红利ETF联接A（481012）',
    '红利低波': '创金合信中证红利低波动指数A（005561）',
    '消费红利': '宏利消费红利指数A（008928）',
    '300红利LV': '嘉实沪深300红利低波动ETF联接A（007605）',
    'SHS红利成长LV': '景顺长城中证沪港深红利低波A（007751）',
    '上证50': '天弘上证50指数A（001548）',
    '深证100': '易方达深证100ETF联接A（110019）',
    '中证100': '华宝中证100ETF联接A（240014）',
    '上证180': '华安上证180ETF联接A（040180）',
    '全指医药': '广发医药卫生联接A（001180）',
    '中证医疗': '华宝医疗ETF联接A（162412）',
    '中证白酒': '招商中证白酒指数（161725）',
    '国证食品': '国泰国证食品饮料行业指数A（160222）',
    '中证环保': '广发中证环保ETF联接A（001064）',
    '全指可选': '广发可选消费联接A（001133）',
    '创业板指': '易方达创业板ETF联接A（110026）',
    '养老产业': '广发中证养老产业A（000968）',
    '东证竞争': '东方红中证竞争力指数A（007657）',
    '中证消费': '汇添富中证主要消费ETF联接A（000248）',
    '中证500': '南方中证500ETF联接（160119）',
    '500SNLV': '景顺长城中证500低波动（003318）',
    'TMT50': '招商深证TMT50ETF联接A（217019）',
    'CS电子': '天弘中证电子ETF联接A（001617）',
    '全指信息': '广发信息技术联接A（000942）',
    '中证传媒': '广发中证传媒ETF联接A（004752）',
}

# 指数分组
_GROUP_SET: dict[str, set[str]] = {
    '红利': {
        '中证红利',
        '上证红利',
        '深证红利',
        '红利低波',
        '消费红利',
        '300红利LV',
        'SHS红利成长LV',
    },
    '沪深头部': {
        '上证50',
        '深证100',
        '中证100',
        '上证180',
        '沪深300',
    },
    '中小股':
    {
        '中证500',
        '500SNLV',
    },
    '医药医疗': {
        '全指医药',
        '中证医疗',
    },
    '食品饮料': {
        '中证白酒',
        '国证食品',
    },
}
_GROUP_DICT = {name: groupName for groupName, nameSet in _GROUP_SET.items() for name in nameSet}

# 屏蔽指数
_DISABLED_DICT: dict[str, str] = {
    '国证A指': '范围太大',
    '中证1000': '范围太大',
    '深证成指': '范围太大',
    '深证F60': '没搞懂',
    '深证F120': '没搞懂',
    'MSCI': '没搞懂',
}

_RENAME_DICT: dict[str, str] = {
    'SHS红利成长LV(人民币)': 'SHS红利成长LV',
    'MSCI中国A股国际通实时(人民币)': 'MSCI',
}

_indexes: list[Index] = []


app: Final = btask.app


@app.command('show')
@syncCall
async def show(
    is_reload: bool = typer.Option(False, '--reload', '-r', help="清空缓存重新请求"),
    is_desc: bool = typer.Option(False, '--desc', '-d', help="显示指数描述"),
    is_target: bool = typer.Option(False, '--target', '-t', help="显示指数描述"),
):
    '展示指数信息'
    # test start ------------------------------
    # clear = True
    # is_desc = True
    # test end --------------------------------
    storeKey = 'idx'
    if is_reload:
        await bstore.clear(storeKey)
    cache = await bstore.get(storeKey)
    cacheTime: datetime.datetime = Null
    if cache:
        try:
            cacheTime, ary = cache
            _indexes.extend(toAny(ary))
        except:
            pass
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
        await bstore.set(storeKey, (btime.datetime(), _indexes))
    if not _indexes:
        btask.abort('数据异常，无法获取数据')
    _sortIndexes()
    _handle()
    if not is_target:
        _showDisabledTable(is_desc)
    _showTable(is_desc, is_target)
    _showTime(cacheTime)


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


def _sortIndexes():
    '指数综合排序'
    ary1 = sorted(_indexes, key=lambda x: x.pe)
    ary2 = sorted(_indexes, key=lambda x: x.pePercentile)
    _indexes.clear()
    for i in range(1, len(ary1) + 1):
        xx = set(ary1[:i]).intersection(set(ary2[:i]))
        subAry = list(xx - set(_indexes))
        subAry.sort(key=lambda x: (x.pe, x.pePercentile))
        _indexes.extend(subAry)
    aryLow: list[Index] = []
    aryMiddle: list[Index] = []
    aryHigh: list[Index] = []
    for item in _indexes:
        if item.level is IndexLevel.low:
            aryLow.append(item)
        elif item.level is IndexLevel.high:
            aryHigh.append(item)
        else:
            aryMiddle.append(item)
    _indexes.clear()
    _indexes.extend(aryLow + aryMiddle + aryHigh)


def _handle():
    # 重命名
    for item in _indexes:
        item.name = _RENAME_DICT.get(item.name, item.name)
    # isPb 自动添加到 disabledDict
    for item in _indexes:
        if item.isPb:
            if item.name not in _DISABLED_DICT:
                _DISABLED_DICT[item.name] = '强周期'
    # 整理买入建议
    buyCount = _BUY_COUNT
    buyGroups: set[str] = set()
    for item in filter(lambda x: x.name not in _DISABLED_DICT, _indexes):
        if item.level is not IndexLevel.low:
            break
        groupName = _GROUP_DICT.get(item.name, '')
        if groupName:
            if groupName in buyGroups:
                continue
            else:
                buyGroups.add(groupName)
        item.isBuy = True
        buyCount -= 1
        if not buyCount:
            break


def _showDisabledTable(isShowDesc: bool):
    table = PrettyTable()
    table.title = bcolor.magenta('屏蔽的指数')
    _setTableFields(table, [
        '排序>',
        '指数名称',
        '屏蔽原因',
        '描述',
    ])
    counter = Counter()
    ary = [x for x in _indexes if x.name in _DISABLED_DICT.keys()]
    ary.sort(key=lambda x: _DISABLED_DICT.get(x.name, ''))
    for item in ary:
        reason = _DISABLED_DICT[item.name]
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


def _showTable(isShowDesc: bool, isTarget: bool):
    # 显示
    table = PrettyTable()
    table.title = bcolor.magenta('关注的指数')
    _setTableFields(table, [
        '排序>',
        '指数名称',
        '百分位>',
        'PE>',
        'ROE>',
        '分组',
        '基金',
        '描述',
    ])
    counter = Counter()
    outputDict = {
        IndexLevel.low: bcolor.green,
        IndexLevel.high: bcolor.red,
    }
    ary = [x for x in _indexes if x.name not in _DISABLED_DICT]
    if isTarget:
        ary = [x for x in ary if (x.level is IndexLevel.low and x.isBuy) or (x.level is IndexLevel.high)]
    for item in ary:
        output = outputDict.get(item.level, bcolor.yellow)
        fundOutput = bcolor.white
        if item.isBuy:
            fundOutput = bcolor.green
        elif item.level is IndexLevel.high:
            fundOutput = bcolor.red
        table.add_row([
            output(str(counter())),
            output(item.name),
            output(f'{item.pePercentile*100:.2f}%'),
            output(f'{item.pe:.2f}'),
            output(f'{item.roe*100:.2f}%'),
            output(_GROUP_DICT.get(item.name, '')),
            fundOutput(_FUND_DICT.get(item.name, '')),
            output(item.desc),
        ])
    print(
        table.get_string(
            fields=table.field_names[:len(table.field_names) - 0 if isShowDesc else -1]
        )
    )


def _showTime(cacheTime: datetime.datetime):
    if cacheTime:
        now = btime.datetime()
        if cacheTime.date() == now.date():
            timeDesc = '当天'
        else:
            timeDesc = f'{(cacheTime-now).days}天前'
        bcolor.printMagenta(f'缓存时间：{cacheTime.strftime(r"%Y-%m-%d %H:%M:%S")}（{timeDesc}）')
    else:
        bcolor.printMagenta('本次请求为实时请求，无缓存')


def _setTableFields(table: PrettyTable, fields: list[str]):
    leftFields: list[str] = []
    rightFields: list[str] = []
    for i in range(len(fields)):
        field = fields[i]
        if field.endswith('<'):
            field = field[:-1]
            fields[i] = field
            leftFields.append(field)
        elif field.endswith('>'):
            field = field[:-1]
            fields[i] = field
            rightFields.append(field)
    table.field_names = [bcolor.magenta(x) for x in fields]
    for field in leftFields:
        table.align[bcolor.magenta(field)] = 'l'
    for field in rightFields:
        table.align[bcolor.magenta(field)] = 'r'


class IndexLevel(IntEnum):
    low = 1
    middle = 2
    high = 3


class Index:

    def __init__(self, id: str, name: str) -> None:
        self.id = id
        self.name = name
        self.isBuy = False

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
    def level(self):
        if self.pePercentile < 0.3:
            return IndexLevel.low
        elif self.pePercentile > 0.7:
            return IndexLevel.high
        else:
            return IndexLevel.middle

# todo 整理分组，选择基金，屏蔽基金
