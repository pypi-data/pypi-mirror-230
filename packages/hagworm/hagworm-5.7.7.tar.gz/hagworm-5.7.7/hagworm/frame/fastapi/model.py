# -*- coding: utf-8 -*-

__author__ = r'wsb310@gmail.com'

import typing
import pydantic
import fastapi

from inspect import Signature, Parameter


class ModelMetaclass(pydantic.main.ModelMetaclass):

    def __init__(cls, _what, _bases=None, _dict=None):

        super().__init__(_what, _bases, _dict)

        if cls.__fields__:

            # 原始参数类型清单
            annotations = typing.get_type_hints(cls)

            func_params = []

            for field in cls.__fields__.values():

                func_params.append(
                    Parameter(
                        field.name, Parameter.POSITIONAL_OR_KEYWORD,
                        default=field.field_info,
                        annotation=annotations.get(field.name, Parameter.empty)
                    )
                )

            # 更新类方法
            cls.params = lambda **kwargs: kwargs
            cls.params.__signature__ = Signature(func_params)


class BaseModel(pydantic.main.BaseModel, metaclass=ModelMetaclass):
    pass


class Depends(fastapi.params.Depends):

    def __init__(self, dependency=None, *, use_cache=True):

        if hasattr(dependency, r'params') and callable(dependency.params):
            super().__init__(dependency=dependency.params, use_cache=use_cache)
        else:
            super().__init__(dependency=dependency, use_cache=use_cache)
