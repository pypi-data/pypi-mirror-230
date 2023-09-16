"""
    用于错误跳转
    示例:
        @error_jump(on_exceptions=FileExistsError, error_callback=error)
        @error_jump(on_exceptions=FileNotFoundError, error_callback=error2)
        @error_jump(callback=success)
        def run(s):
            return s * 2
"""
import traceback
from typing import Callable, Union, List, Type


class ErrorJump:
    def __init__(
            self,
            on_exceptions: Union[Type[Exception], List[Type[Exception]]] = None,
            ignore_exceptions: Union[Type[Exception], List[Type[Exception]]] = None,
            callback: Callable = None,
            error_callback: Callable = None,
            raise_exception: bool = True,
            print_exception: bool = True,
    ):
        """
        注意：有回调函数优先回调函数，走回调函数不会有返回

        :param on_exceptions: 哪些报错才执行回调，默认所有
        :param ignore_exceptions: 哪些报错不执行回调，默认无
        :param callback: 成功回调函数
        :param error_callback: 错误回调函数
        :param raise_exception: 是否需要抛出错误
        :param print_exception: 不抛出错误的时候，是否需要打印错误
        """
        self.callback = callback
        self.error_callback = error_callback
        self.raise_exception = raise_exception
        self.print_exception = print_exception

        if on_exceptions and not isinstance(on_exceptions, list) and issubclass(on_exceptions, Exception):
            on_exceptions = [on_exceptions]
        self.on_exceptions = on_exceptions or []

        if ignore_exceptions and not isinstance(ignore_exceptions, list) and issubclass(ignore_exceptions, Exception):
            ignore_exceptions = [ignore_exceptions]
        self.ignore_exceptions = ignore_exceptions or []

    def runner(self, func: Callable, *args, **kwargs):
        """
        执行器

        :param func: 函数
        :param args:
        :param kwargs:
        :return:
        """
        try:
            result = func(*args, **kwargs)
            if self.callback:
                self.callback(result)
            else:
                return result

        except Exception as e:

            # 判断是否在忽略列表，不在执行回调
            if self.ignore_exceptions and not self.is_ignore_exception(e) and self.error_callback:
                return self.error_callback(*args, **kwargs)

            # 判断是否执行回调
            elif self.is_on_exception(e) and self.error_callback:
                return self.error_callback(*args, **kwargs)

            # 是否抛出错误
            if self.raise_exception:
                if self.ignore_exceptions and e not in self.ignore_exceptions:
                    raise e
                elif self.on_exceptions and e in self.on_exceptions:
                    raise e
                elif not self.ignore_exceptions and not self.on_exceptions:
                    raise e

            if self.print_exception:
                traceback.print_exception(type(e), e, e.__traceback__)

    def is_on_exception(self, e: Exception) -> bool:
        """
        该报错是否在跳转的错误列表内

        :param e:
        :return:
        """
        if len(self.on_exceptions) == 0:
            return True

        for exception in self.on_exceptions:
            if e.__class__ is exception:
                return True

        return False

    def is_ignore_exception(self, e: Exception) -> bool:
        """
        该报错是否在忽略的错误列表内

        :param e:
        :return:
        """
        for exception in self.ignore_exceptions:
            if e.__class__ is exception:
                return True

        return False

    def __call__(self, func: Callable):
        def wrapper(*args, **kwargs):
            return self.runner(func, *args, **kwargs)

        return wrapper


def error_jump(
        on_exceptions: Union[Type[Exception], List[Type[Exception]]] = None,
        ignore_exceptions: Union[Type[Exception], List[Type[Exception]]] = None,
        callback: Callable = None,
        error_callback: Callable = None,
        raise_exception: bool = True,
        print_exception: bool = True,
):
    """

    :param on_exceptions: 哪些报错才执行回调，默认所有
    :param ignore_exceptions: 哪些报错不执行回调，默认无
    :param callback: 成功回调函数
    :param error_callback: 错误回调函数
    :param raise_exception: 是否需要抛出错误
    :param print_exception: 不抛出错误的时候，是否需要打印错误
    :return:
    """
    return ErrorJump(
        on_exceptions=on_exceptions,
        ignore_exceptions=ignore_exceptions,
        callback=callback,
        error_callback=error_callback,
        raise_exception=raise_exception,
        print_exception=print_exception
    )
