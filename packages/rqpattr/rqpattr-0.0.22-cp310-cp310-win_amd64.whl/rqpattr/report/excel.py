# -*- coding: utf-8 -*-
from typing import List, Dict
from collections import defaultdict

from rqpattr.const import AnalysisModel
from rqpattr.report.templcate_based_excel import PABrinsonTemplate, PAFactorTemplate, ExcelTemplate, PAFactorV2Template

ATTRIBUTION_EXCEL_TRANSLATION = {
    'beta': '贝塔',
    'book_to_price': '账面市值比',
    'earnings_yield': '盈利率',
    'growth': '成长性',
    'leverage': '杠杆率',
    'liquidity': '流动性',
    'momentum': '动量',
    'non_linear_size': '非线性市值',
    'residual_volatility': '残余波动率',
    'size': '规模',
    'comovement': '市场联动',
    'specific_return': '残余收益',
    'cash': '现金',
    'ShenWan': '申万',
    'style': '风格因子',
    'industry': '行业因子',
    'styles': '风格因子',
    'industries': '行业因子',
    'specific_risk': '残余风险',
    'other': "其它资产",
    # factor_v2 relative
    "earnings_variability": "盈利波动",
    "earnings_quality": "盈利质量",
    "profitability": "盈利能力",
    "dividend_yield": "股息率",
    "longterm_reversal": "长期反转",
    "investment_quality": "投资质量"
}


def get_performance_attribution_excel(report: Dict) -> ExcelTemplate:
    """ generage excel according to given attribution `report`.

    :param report: attribution report, requires the following fields:
       * template: which template is used to generate report, it can be one of `rqpattr.const.AnalysisModel`
       * result: attribution result, it can be generated from `rqpattr.api.performance_attribute`
       * benchmark: benchmark input argument
       * start_date: start_date input argument
       * end_date: end_date input argument
    """
    template = report["template"]
    if template == AnalysisModel.BRINSON:
        template = generate_brinson_report(report)
    elif template in (AnalysisModel.FACTOR, AnalysisModel.FACTOR_V2):
        template = generate_factor_report(report, template)
    else:
        raise ValueError(("Sorry, template %s excel report temporarily not supported") % template)
    return template


def _flat_return_decomposition_help(rv: list, rd: list, indent: int):
    for item in rd:
        rv.append({"factor": " " * indent + item["factor"], "value": item["value"]})
        child = item.get("children")
        if child:
            _flat_return_decomposition_help(rv, child, indent + 4)


def flat_return_decomposition(rd: List[dict]) -> List[dict]:
    rv = []
    _flat_return_decomposition_help(rv, rd, 0)
    return rv


def flat_factor_exposure(rd):
    data = defaultdict(dict)
    for doc in rd:
        factor = doc['factor']
        for d in doc['data']:
            date = d['date']
            data[date][factor] = d['portfolio']
            data[date]['date'] = date
    return sorted(data.values(), key=lambda x: x['date'])


def _reform_factor_result(report):
    # 因子归因
    factor_attribution = []
    # 总计相关的数据.
    p_return, b_return, a_return, p_risk, b_risk, a_risk = 0, 0, 0, 0, 0, 0

    for category in report:
        prefix = '  '
        if category['type'] in {'style', 'industry'}:
            factor_attribution.append({
                'factor': ATTRIBUTION_EXCEL_TRANSLATION.get(category['type'], category['type']),
                'portfolio_return': sum(v['portfolio_return'] for v in category['factors']),
                'benchmark_return': sum(v['benchmark_return'] for v in category['factors']),
                'active_return': sum(v['active_return'] for v in category['factors']),
                'portfolio_risk': sum(v['portfolio_risk'] for v in category['factors']),
                'benchmark_risk': sum(v['benchmark_risk'] for v in category['factors']),
                'active_risk': sum(v['active_risk'] for v in category['factors']),
            })
            prefix = '    '

        for v in category['factors']:
            # 因子名称翻译
            v['factor'] = prefix + ATTRIBUTION_EXCEL_TRANSLATION.get(v['factor'], v['factor'])
            p_return += v['portfolio_return'] or 0.0
            b_return += v['benchmark_return'] or 0.0
            a_return += v['active_return'] or 0.0
            p_risk += v['portfolio_risk'] or 0.0
            b_risk += v['benchmark_risk'] or 0.0
            a_risk += v['active_risk'] or 0.0
            factor_attribution.append(v)

    factor_attribution.insert(0, {
        'factor': '总计',
        'portfolio_return': p_return,
        'benchmark_return': b_return,
        'active_return': a_return,
        'portfolio_risk': p_risk,
        'benchmark_risk': b_risk,
        'active_risk': a_risk,
    })
    return factor_attribution


def _generate_factor_report(template, report):
    result = report["result"]
    # 收益分解
    return_decomposition = flat_return_decomposition(result["returns_decomposition"])
    decomposition_fields = ["factor", "value"]
    template.load_data("returns_decomposition", area="returns_decomposition", data=[
        [i[field] for field in decomposition_fields]
        for i in return_decomposition
    ])

    # 风格分析
    # 原json数据 把每个factor所有日期的数据放在一起 如下
    # [{'factor': '国防军工', 'data': [{'date': '2017-07-21', 'portfolio': 0.0}, ..]}
    # {'factor': 'beta', 'data': [{'date': '2017-07-21', 'portfolio': 0.0}, ... ]}
    # ....]
    # 需要的格式 需要所有因子每天的表现以字典的形式存成行 如下
    #  日期	beta	liquidity	residual_volatility
    # 2017-07-21	0.00%	0.00%	0.00%
    # 2017-07-24	0.00%	0.00%	0.00%
    # 2017-07-25	0.00%	0.00%	0.00%
    # 2017-07-26	0.00%   0.00%   0.00%
    exposure = flat_factor_exposure(result["attribution"]['factor_exposure'])
    if isinstance(template, PAFactorTemplate):
        exposure_fields = [
            "date", "beta", "book_to_price", "earnings_yield", "growth", "leverage", "liquidity", "momentum",
            "non_linear_size", "residual_volatility", "size", ]
    else:
        exposure_fields = [
            "date", "beta", "book_to_price", "earnings_yield", "growth", "leverage", "liquidity", "momentum",
            "mid_cap", "residual_volatility", "size",
            "earnings_variability", "earnings_quality", "profitability", "dividend_yield",
            "longterm_reversal", "investment_quality"
        ]
    template.load_data("factor_exposure", area="factor_exposure", data=[
        [i[field] for field in exposure_fields]
        for i in exposure
    ])

    factor_attribution = _reform_factor_result(result['attribution']['factor_attribution'])
    factor_attribution_fields = [
        "factor", "portfolio_exposure", "benchmark_exposure", "active_exposure", "portfolio_return", "benchmark_return",
        "active_return", "portfolio_risk", "benchmark_risk", "active_risk", ]
    template.load_data("factor_attribution", area="factor_attribution", data=[
        [i.get(field, "--") for field in factor_attribution_fields]
        for i in factor_attribution
    ])

    # for user input arguments
    # benchmark_name = report['benchmark'].get('id', '')
    benchmark_name = report["benchmark"]
    input_args = {
        'benchmark': benchmark_name,
        'start_date': report['start_date'], 'end_date': report['end_date']
    }
    template.load_data("analysis_arguments", data=input_args)
    return template


def generate_factor_report(report: Dict, model: AnalysisModel) -> ExcelTemplate:
    template = PAFactorTemplate() if model == AnalysisModel.FACTOR else PAFactorV2Template()
    return _generate_factor_report(template, report)


def generate_brinson_report(report: Dict) -> ExcelTemplate:
    template = PABrinsonTemplate()
    result = report["result"]

    # 收益分解
    return_decomposition = flat_return_decomposition(result["returns_decomposition"])
    decomposition_fields = ["factor", "value"]
    template.load_data("returns_decomposition", area="returns_decomposition", data=[
        [i[field] for field in decomposition_fields]
        for i in return_decomposition
    ])

    # 行业归因
    brinson_fields = [
        "industry", "portfolio_weight", "benchmark_weight", "diff", "selection_return", "allocation_return",
        "selection_risk", "allocation_risk"
    ]
    brinson = result['attribution']['brinson']
    for row in brinson:
        row['diff'] = row['portfolio_weight'] - row['benchmark_weight']
        row['industry'] = '  ' + ATTRIBUTION_EXCEL_TRANSLATION.get(
            row['industry'], row['industry']
        )
    brinson.insert(0, {
        'industry': '总计',
        'portfolio_weight': sum(v['portfolio_weight'] for v in brinson),
        'benchmark_weight': sum(v['benchmark_weight'] for v in brinson),
        'diff': 0,
        'allocation_return': sum(v['allocation_return'] for v in brinson),
        'allocation_risk': sum(v['allocation_risk'] for v in brinson),
        'selection_return': sum(v['selection_return'] for v in brinson),
        'selection_risk': sum(v['selection_risk'] for v in brinson),
    })
    template.load_data("industry_attribution", area="industry_attribution", data=[
        [i[field] for field in brinson_fields]
        for i in brinson
    ])

    # for user input arguments
    # benchmark_name = report['benchmark'].get('id', '')
    benchmark_name = report["benchmark"]
    input_args = {
        'benchmark': benchmark_name,
        'start_date': report['start_date'], 'end_date': report['end_date']
    }
    template.load_data("analysis_arguments", data=input_args)
    return template
