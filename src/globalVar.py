import re
import pickle

rex2 = r'<div class=\'tishi\'>(.*?)<\/div>'
rex = r'dateArr = (.*?);'
rex1 = r'\'(.*?)\''
r = re.compile(rex)
r1 = re.compile(rex1)
r2 = re.compile(rex2)

asset_sheet_content = [
    "monetary_funds",  # 货币资金
    "trading_financial_assets",  # 交易性金融资产
    "bill_receivable",  # 应收票据
    "accounts_receivable",  # 应收账款
    "advance_receipts",  # 预收款项
    "other_receivable",  # 其他应收款
    "revenue_related_companies",  # 应收关联公司款
    "interest_receivable",  # 应收利息
    "dividents_receivable",  # 应收股利
    "stock",  # 存货
    "consumable_bio_assets",  # 消耗性生物资产
    "non_current_assets_in_one_year",  # 一年内到期的非流动性资产
    "other_current_assets",  # 其他流动资产
    "total_current_assets",  # 流动资产合计
    "available_for_sail_financial_assets",  # 可供出售金融资产
    "held_to_haturity_investments",  # 持有至到期投资
    "long_term_receivables",  # 长期应收款
    "long_term_investment",  # 长期股权投资
    "investment_properties",  # 投资性房地产
    "fixed_assetes",  # 固定资产
    "under_construction_projects",  # 在建工程
    "construction_materials",  # 工程物资
    "disposal_of_fixed_assets",  # 固定资产清理
    "capitalized_biological_assets",  # 生产性生物资产
    "oil_and_gas_assets",  # 油气资产
    "intangible_assets",  # 无形资产
    "r&d_expenses",  # 开发支出
    "goodwill",  # 商誉
    "long_term_deferred_and_prepaid_expenses",  # 长期待摊费用
    "deferred_income_tax_assets",  # 递延所得税资产
    "other_non_current_assets",  # 其他非流动资产
    "sub_total_of_non_current_assets",  # 非流动资产合计
    "total_assets",  # 资产总计
    "short_term_loans",  # 短期借款
    "trading_financial_liabilities",  # 交易行金融资产
    "notes_payable",  # 应付票据
    "accounts_payable",  # 应付账款
    "accounts_received_in_advance",  # 预收账款
    "employee_compensation_payable",  # 应付职工薪酬
    "taxes_payable",  # 应交税费
    "interest_payable",  # 应付利息
    "dividend_payable",  # 应付股利
    "other_payables",  # 其他应付款
    "due_to_related_companies",  # 应付关联公司款
    "non_current_liabilities_due_within_one_year",  # 一年内到期的非流动负债
    "other_current_liabilities",  # 其他流动负债
    "sub_total_of_current_liabilities",  # 流动负债合计
    "long_term_loans",  # 长期借款
    "bonds_payable",  # 应付债券
    "long_term_accounts_payable",  # 长期应付款
    "special_payable",  # 专项应付款
    "estimatied_liabilities",  # 预计负债
    "deferred_income_tax_liabilities",  # 递延所得税负债
    "other_non_current_liabilities",  # 其他非流动负债
    "sub_total_of_non_current_liabilities",  # 非流动负债合计
    "total_liabilities",  # 负债合计
    "paid_in_capital",  # 实收资本
    "capital_surplus",  # 资本公积
    "surplus_reserve",  # 盈余公积
    "treasury_stock",  # 库存股
    "undistributed_profits",  # 未分配利润
    "minority_stockholders_interest",  # 少数股东权益
    "foreign_currency_capital",  # 外币报表折算差价
    "abnormal_management_project_income_adjusted",  # 非正常经营项目收益调整
    "total_owners_equity_attributable_to_parent",  # 归属母公司所有者权益
    "owners_equity",  # 所有者权益
    "total_liabilities_and_owners_equity"  # 负债和所有者权益
]

profit_sheet_content = [
    "operating_income",  #营业收入
    "operating_cost",  #营业成本
    "operating_tax_and_extra",  #营业税金及附加
    "selling_expenses",  #销售费用
    "management_fees",  #管理费用
    "exporating_expenses",  #勘探费用
    "financial_expenses",  #财务费用
    "assets_impairment_loss",  #资产减值损失
    "income_from_changes_in_fair_value",  #公允价值变动净收益
    "investment_income",  #投资收益
    "joint_enterprises_and_joint_ventures_to_investment_returns",  #对联营企业和合营企业的投资收益
    "influence_operating_profit_of_other_subjects",  #影响营业利润的其他科目
    "operating_profit",  #营业利润
    "subsidies_income",  #补贴收入
    "non_operating_income",  #营业外收入
    "non_operating_revenue",  #营业外支出
    "non_current_assets_disposal_net_loss",  #非流动资产处置净损失
    "influence_of_total_profit_of_other_subjects",  #影响利润总额的其他科目
    "total_profit",  #利润总额
    "income_tax",  #所得税
    "influence_net_profit_of_other_subjects",  #影响净利润的其他科目
    "net_profit",  #净利润
    "owners_net_profit_attributable_to_parent",  #归属于母公司所有者的净利润
    "minority_interest_income",  #少数股东损益
    "earnings_per_share",  #每股收益
    "basic_earnings_per_share",  #基本每股收益
    "diluted_earnings_per_share"  #稀释每股收益
]

cash_sheet_content = [
    "cash_from_sale",  #销售商品、提供劳务收到的现金
    "tax_rebate",  #收到的税费返还
    "other_cash_rel_op",  #收到其他与经营活动有关的现金
    "sub_cash_from_oa",  #经营活动现金流入小计
    "cash_for_good",  #购买商品、接受劳务支付的现金
    "cash_for_emp",  #支付给职工以及为职工支付的现金
    "cash_for_tax",  #支付的各项税费
    "cash_for_op",  #支付其他与经营活动有关的现金
    "sub_cash_out_oa",  #经营活动现金流出小计
    "net_cash_op",  #经营活动产生的现金流量净额
    "cash_rec_invest",  #收回投资收到的现金
    "invest_income_rec",  #取得投资收益收到的现金
    "net_cash_fa",  #处置固定资产、无形资产、和其他长期资产收回的现金净额
    "net_cash_bu",  #处置子公司及其他营业单位收到的现金净额
    "other_cash_rec_invest",  #收到其他与投资活动有关的现金
    "cash_inflow_invest",  #投资活动现金流入小计
    "cash_paid_fa",  #构建固定资产、无形资产和其他长期资产支付的现金
    "cash_paid_invest",  #投资祝福的现金
    "net_cash_paid_bu",  #取得子公司及其他营业单位支付的现金净额
    "other_cash_paid_invest",  #支付其他与投资活动有关的现金
    "cash_outflow_invest",  #投资活动现金流出小计
    "net_cash_flow_invest",  #投资活动产生的现金流量净额
    "cash_rec_contrib",  #吸收投资收到的现金
    "borrowing_rec",  #取得借款收到的现金
    "other_cash_rec_rel_fa",  #收到其他与筹资活动有关的现金
    "cash_inflow_fa",  #筹资活动现金流入小计
    "borrowing_repay",  #偿还债务支付的现金
    "cash_paid_div",  #分配股利、利润或偿付利息支付的现金
    "other_cash_paid_finance",  #支付其他与筹资活动有关的现金
    "other_cash_outflow_finance",  #筹资活动现金流出小计
    "net_cash_finance",  #筹资活动产生的现金流量净额
    "initial_cash",  #期初现金及现金等价物余额
    "final_cash",  #期末现金及现金等价物余额
    "net_profit",  #净利润
	"asset_impairment_loss",  #资产减值准备
	"fixed_assets_depreciation",  #固定资产折旧、油气资产消耗、生产性生物资产折旧
	"intangible_assets_amortize",  #无形资产费用摊销
	"long_term_prepaid_expenses_amortization",  #长期待摊费用摊销
	"the_disposal_of_fixed_assets",  #处置固定资产、无形资产、和其他长期资产收回的损失
	"fixed_assets_scrap_loss"  #固定资产报废损失
	"losses_on_the_changes_in_the_fair_value",  #公允价值变动损失
	"finance_charges",  #财务费用
	"investment_losses",  #投资损失
	"deferred_tax_assets",  #递延所得税资产减少
	"deferred_income_tax_liabilities",  #递延所得税负债增加
	"the_decrease_of_inventory",  #存货的减少
	"a_drop_in_business_receivables",  #经营性应收项目的减少
	"business_to_cope_with_the_increase_of_the_project",  #经营性应付项目的增加
	"other",  #其他
	"business_activities_generated_cash_flow_net_2",  #经营活动产生的现金流量净额
	"a_debt_into_capital",  #负债转为资本
	"convertible_bonds_matured_within_a_year",  #一年内到期的可转换公司债券
	"for_fixed_assets",  #融资租入固定资产
	"the_ending_balance_of_cash",  #现金的期末余额
	"the_beginning_balance_of_cash",  #现金的期初余额
	"cash_equivalents_of_the_final_balance",  #现金等价物的期末余额
	"the_beginning_balance_of_cash_equivalents",  #现金等价物的期初余额
	"other_reasons_the_impact_on_the_cash_2",  #其他原因对现金的影响
	"net_increase_in_cash_and_cash_equivalents"  #现金及现金等价物净增加额
]

season2date = {
    1 : ".03.15",
    2 : ".06.30",
    3 : ".09.30",
    4 : ".12.31"
}

id2name_dict = pickle.load(open("../bin/dict.bin", "rb"))


def safe_div(dividend, divisor):
    try:
        val = float(dividend) / divisor
    except ZeroDivisionError:
        val = 0
    return val


def safe_growth_rate(dividend: float, divisor: float) -> float:
    try:
        val = float(dividend) / divisor - 1
    except ZeroDivisionError:
        val = 0
    return val


def get_ratio(last_data: float, avg_data: float):
    """
    get the ratio between final year indicator and the average data
    :param last_data: one of the company's last year's indicator
    :param avg_data: the industry average data
    :return: the ratio which is safe
    """
    try:
        ratio = last_data / avg_data
    except ZeroDivisionError:
        ratio = 0
    if ratio > 2:
        ratio = 2
    if ratio < 0:
        ratio = 0
    return ratio