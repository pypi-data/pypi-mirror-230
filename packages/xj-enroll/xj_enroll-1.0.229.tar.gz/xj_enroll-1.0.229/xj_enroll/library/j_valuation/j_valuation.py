# encoding: utf-8
"""
@project: djangoModel->j_valuation
@author: 孙楷炎
@Email: sky4834@163.com
@synopsis: 计价服务类
@created_time: 2022/10/13 16:58
"""

import re

from xj_enroll.utils.custom_tool import write_to_log
from .j_base_expression import JBaseExpression
from .j_expressions import CalculateExpression


class JValuation(JBaseExpression):
    """
    计算入口类，计算器 对外暴露的类
    """

    def process(self, expression_string):
        # 公式合法性校验：expression_string
        if expression_string is None:
            return "", None
        if not len(re.findall("\(", expression_string)) == len(re.findall("\)", expression_string)):
            write_to_log(prefix="计价公式配置错误，请及时检查", content="语法错误，括号应该成对存在")
            return None, "语法错误，括号应该成对存在"
        # 公式字符串,符号预处里预处理
        expression_string = expression_string.upper().replace(" ", "").replace("=", "==").replace(">==", ">=").replace("<==", "<=")

        # 把自定义公式计算出结果进行替换，得出基础的加减乘除公式字符拆
        parsed_expression_string = self.parse_expression(expression_string)

        # 计算基础加减乘除，然后得出结果并返回
        result = CalculateExpression().process(parsed_expression_string)
        return result, None
