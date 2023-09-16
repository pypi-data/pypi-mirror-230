"""
    错误重试装饰器

    参数：
        retry: 失败重试次数
        delay: 错误重试间隔
        on_exceptions: 哪些报错才重试，默认都重试
        ignore_exceptions: 哪些报错不重试，直接抛出
        callback: 执行成功回调结果函数
        error_callback: 执行失败回调结果函数
        raise_exception: 一直失败，最后是否需要抛出错误

    注意：
        有回调函数优先回调函数，走回调函数不会有返回

    示例：
        @Retry(max_retry=3)
        def run():
            raise FileExistsError('文件不存在！')
"""
import time
import traceback
from typing import Callable, Union, List, Type


class Retry:
    def __init__(
            self,
            max_retry: int = 3,
            delay: int = 0,
            on_exceptions: Union[Type[Exception], List[Type[Exception]]] = None,
            ignore_exceptions: Union[Type[Exception], List[Type[Exception]]] = None,
            callback: Callable = None,
            error_callback: Callable = None,
            raise_exception: bool = True,
            print_exception: bool = True,
    ):
        """
        注意：有回调函数优先回调函数，走回调函数不会有返回

        :param max_retry: 失败重试次数
        :param delay: 错误重试间隔
        :param on_exceptions: 哪些报错才重试，默认都重试
        :param ignore_exceptions: 哪些报错不重试，直接抛出
        :param callback: 成功回调函数
        :param error_callback: 错误回调函数（最后一次）
        :param raise_exception: 一直失败，最后是否需要抛出错误
        :param print_exception: 不抛出错误的时候，是否需要打印错误
        """
        self.max_retry = max_retry
        self.delay = delay
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
        failed = 0

        while failed < self.max_retry:
            try:
                result = func(*args, **kwargs)
                if self.callback:
                    return self.callback(result)
                else:
                    return result

            except Exception as e:
                exception = e

                failed += 1

                # 判断是否要重试
                if not self.is_on_exception(e):
                    break

                # 判断是否要忽略，直接抛出
                if self.is_ignore_exception(e):
                    break

                time.sleep(self.delay)

        # 判断是否执行回调
        if self.error_callback:
            return self.error_callback(*args, **kwargs)

        # 是否抛出错误
        if self.raise_exception:
            if self.ignore_exceptions and exception not in self.ignore_exceptions:
                raise exception
            elif self.on_exceptions and exception in self.on_exceptions:
                raise exception
            elif not self.ignore_exceptions and not self.on_exceptions:
                raise exception

        if self.print_exception:
            traceback.print_exception(type(exception), exception, exception.__traceback__)

    def is_on_exception(self, e: Exception) -> bool:
        """
        该报错是否在重试的错误列表内

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


def retry(
        max_retry: int = 3,
        delay: int = 0,
        on_exceptions: Union[Type[Exception], List[Type[Exception]]] = None,
        ignore_exceptions: Union[Type[Exception], List[Type[Exception]]] = None,
        callback: Callable = None,
        error_callback: Callable = None,
        raise_exception: bool = True,
        print_exception: bool = True,
):
    """

    :param max_retry: 失败重试次数
    :param delay: 错误重试间隔
    :param on_exceptions: 哪些报错才重试，默认都重试
    :param ignore_exceptions: 哪些报错不重试，直接抛出
    :param callback: 成功回调函数
    :param error_callback: 错误回调函数
    :param raise_exception: 一直失败，最后是否需要抛出错误
    :param print_exception: 不抛出错误的时候，是否需要打印错误
    :return:
    """
    return Retry(
        max_retry=max_retry,
        delay=delay,
        on_exceptions=on_exceptions,
        ignore_exceptions=ignore_exceptions,
        callback=callback,
        error_callback=error_callback,
        raise_exception=raise_exception,
        print_exception=print_exception
    )
