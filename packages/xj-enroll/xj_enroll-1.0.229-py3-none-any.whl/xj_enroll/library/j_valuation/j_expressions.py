# encoding: utf-8
"""
@project: djangoModel->j_expression
@author: 孙楷炎
@Email: sky4834@163.com
@synopsis: 公式类
@created_time: 2023/6/14 14:41
"""
import math

from xj_enroll.utils.custom_tool import write_to_log
from .j_base_expression import JBaseExpression


class CalculateExpression(JBaseExpression):
    name = ""
    patt = "\([^\(]*?\)"

    def process(self, expression_string):
        try:
            return self.safe_eval(expression_string)  # 加加减乘除
        except ZeroDivisionError:
            return 0  # 0/n  的情况
        except Exception as e:
            write_to_log(level="error", prefix="计价异常（SUMExpression）", err_obj=e)
            return expression_string


class IFExpression(JBaseExpression):
    """
    布尔值判断、三元运算
    """
    name = "IF"
    patt = "IF\([^\(]*?\)"

    def process(self, expression, *args, ):
        bool_expression, yes_expression, no_expression = expression.replace(IFExpression.name, "").replace("(", "").replace(")", "").split(",")
        if CalculateExpression().process(bool_expression):
            return yes_expression
        else:
            return no_expression


class SUMExpression(JBaseExpression):
    """
    求和计算、（多参数在服务中获取）
    """
    name = "SUM"
    patt = "SUM\([^\(]*?\)"  # SUM(a,b,c) == a+b+c

    def process(self, expression):
        try:
            args = expression.replace(self.name, "").replace("(", "").replace(")", "").split(",")
            result = 0
            for i in args:
                result = self.safe_eval(str(result) + "+" + str(i))
            return result
        except Exception as e:
            write_to_log(level="error", prefix="计价异常（SUMExpression）", err_obj=e)
            return 0


class CEILExpression(JBaseExpression):
    """
    取整公式
    """
    name = "CEIL"
    patt = "CEIL\([^\(]*?\)"  # ROUND(num, index, step)

    def process(self, expression):
        try:
            expression = expression.replace(self.name, "").replace("(", "").replace(")", "")
            return math.ceil(self.safe_eval(expression))
        except Exception as e:
            write_to_log(level="error", prefix="计价异常（SUMExpression）", err_obj=e)
            return 0
