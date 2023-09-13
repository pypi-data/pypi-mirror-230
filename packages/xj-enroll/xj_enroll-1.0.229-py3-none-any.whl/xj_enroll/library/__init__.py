# encoding: utf-8
"""
@project: djangoModel->__init__
@author: 孙楷炎
@Email: sky4834@163.com
@synopsis: 抽象库、监听者模式、策略模式设计。
@note: 该目录下面所有文件不专注页具体业务，不专注服务于主框架。实现面向零散功能的逻辑代码，
note 如：微信登录和框架镖行业务的登录关系,镖行登录调用微信登录。 所有类不可模型。
@created_time: 2023/6/14 14:05
"""
from .j_valuation.j_valuation import JValuation

__all__ = [
    JValuation
]
