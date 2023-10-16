from __future__ import annotations

from typing import Any, Final

from beni import bcolor, btask
from beni.bfunc import Counter, syncCall
from playwright.async_api import async_playwright
from prettytable import PrettyTable

app: Final = btask.app

_disabledDict = {
    '养老产业': '近期曾修改编制',
    '中证100': '近期曾修改编制',
    '中证1000': '回报太低',
    '中证军工': '回报太低',
    '标普红利': '没有相关基金',
    '50AH优选': '没有相关基金',
    '恒生国企': '没有相关基金',
    '深证100': '与沪深300有重合',
    '证券公司': '强周期不考虑',
}
_fundDict = {
    '中证环保': '广发中证环保产业ETF联接A（001064）',
}


# @app.command('show')
@syncCall
async def show():
    '展示'
    ary = await _getIndexEvalList()
    _showDisabledTable(ary)
    _showTable(ary)


def _showDisabledTable(ary: list[_IdxModel]):
    table = PrettyTable()
    table.title = bcolor.magenta('屏蔽的指数')
    table.field_names = [bcolor.magenta(x) for x in ['排序', '指数名称', '屏蔽原因']]
    counter = Counter()
    ary = [x for x in ary if x.name in _disabledDict.keys()]
    ary.sort(key=lambda x: _disabledDict.get(x.name, ''))
    for item in ary:
        reason = _disabledDict[item.name]
        table.add_row([
            counter(),
            item.name,
            reason,
        ])
    table.print_empty = True
    print(table.get_string())


def _showTable(ary: list[_IdxModel]):
    ary = [x for x in ary if x.name not in _disabledDict.keys()]
    pxAry = sorted(ary, key=lambda x: x.px)
    roeAry = sorted(ary, key=lambda x: x.roe, reverse=True)
    ary.clear()
    for i in range(1, len(pxAry) + 1):
        xx = set(pxAry[:i]).intersection(set(roeAry[:i]))
        subAry = list(xx - set(ary))
        subAry.sort(key=lambda x: x.px)
        ary.extend(subAry)
    highAry: list[_IdxModel] = []
    midAry: list[_IdxModel] = []
    lowAry: list[_IdxModel] = []
    for item in ary:
        if item.px_percentile < 0.3:
            lowAry.append(item)
        elif item.px_percentile > 0.7:
            highAry.append(item)
        else:
            midAry.append(item)
    ary = lowAry + midAry + highAry
    table = PrettyTable()
    table.title = bcolor.magenta('关注的指数')
    table.field_names = [bcolor.magenta(x) for x in ['排序', '指数名称', '百分位', 'PE/PB', 'ROE', '基金']]
    for fieldName in ['排序', '百分位', 'PE/PB', 'ROE']:
        table.align[bcolor.magenta(fieldName)] = 'r'
    counter = Counter()
    for item in ary:
        if item in lowAry:
            output = bcolor.green
        elif item in highAry:
            output = bcolor.red
        else:
            output = bcolor.yellow
        table.add_row([output(x) for x in [
            str(counter()),
            item.name,
            f'{item.px_percentile*100:.2f}%',
            f'{item.px:.2f}',
            f'{item.roe*100:.2f}%',
            _fundDict.get(item.name, ''),
        ]])
    print(table.get_string())


async def _getIndexEvalList():
    async with async_playwright() as p:
        async with await p.chromium.launch(headless=True, channel='chrome') as browser:
            async with await browser.new_context() as context:
                async with await context.new_page() as page:
                    async with page.expect_response("https://qieman.com/pmdj/v2/idx-eval/latest") as response_info:
                        await page.goto("https://qieman.com/idx-eval")
                    response = await response_info.value
                    data = await response.json()
                    return [_IdxModel(x) for x in data['idxEvalList']]


class _IdxModel:

    def __init__(self, data: dict[str, Any]) -> None:
        self._data = data

    @property
    def id(self) -> str:
        '指数id'
        return self._data['indexCode']

    @property
    def name(self) -> str:
        '指数名称'
        return self._data['indexName']

    @property
    def isPB(self) -> bool:
        '是否使用PB'
        return not not self._data['scoreBy']

    @property
    def px(self) -> float:
        'PE 或 PB'
        return self._data['pb'] if self.isPB else self._data['pe']

    @property
    def px_percentile(self) -> float:
        'PE 或 PB 的历史百分位'
        return self._data['pbPercentile'] if self.isPB else self._data['pePercentile']

    @property
    def roe(self) -> float:
        '净资产收益率，可参考为年化收益率'
        return self._data['roe']
