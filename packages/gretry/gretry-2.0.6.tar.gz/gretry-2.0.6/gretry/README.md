# gretry

包含以下两个模块

- 错误重试装饰器 retry
- 错误跳转装饰器 error_jump

# 安装

```
pip install gretry
```

# 模块介绍

## retry 模块

用来进行错误重试  
参数如下：

- retry: 失败重试次数（默认 3 次）
- delay: 错误重试间隔（默认 0s）
- on_exceptions: 哪些报错才重试（默认 都重试）
- ignore_exceptions: 哪些报错不重试（默认 无）
- callback: 执行成功回调结果函数
- error_callback: 执行失败回调结果函数
- raise_exception: 一直失败，最后是否需要抛出错误（默认 True）

注意：多个 @retry 装饰器套着用是不可取的，因为一个装饰器重新执行程序，那么其他装饰器也会再次执行

## error_jump 模块

用于执行错误时跳转，当然，正确也可以跳转  
参数如下：

- on_exceptions: 哪些报错才跳转（默认 都跳转）
- ignore_exceptions: 哪些报错不执行跳转（默认 无）
- callback: 执行成功回调结果函数
- error_callback: 执行失败回调结果函数
- raise_exception: 是否需要抛出错误（默认 True）

注意：有多个 @error_jump 装饰器时，不要使用 raise_exception = False 不然其余装饰器无法捕获错误

# 注意点

# exception

on_exceptions 和 ignore_exceptions 只有一个能被设置

## 当有 callback 参数时

- 当有正确的结果时，会将结果作为参数放入 callback 并执行
- 有 callback 则不会返回结果
- 无正确结果则直接抛出

## 当有 error_callback 参数时

- 当执行失败时，会在抛出前，将函数的执行参数，作为参数放入 error_callback 并执行

## 错误的继承类的问题

比如 FileExistsError 类型是 OSError 的子类，这里判断的时候是 FileExistsError 就是 FileExistsError，不会向上识别

# 示例-retry

## 示例 1

【demo】

```
from gretry import retry


def failed(name):
    print('failed', name)


def success(result):
    print('success', result)


@retry(max_retry=3, delay=1, callback=success, error_callback=failed)
def run(name):
    raise FileExistsError('文件不存在！')


if __name__ == '__main__':
    run(name='郭一会儿')

```

【输出】

```
failed 郭一会儿
Traceback (most recent call last):
  File "D:\Program\Python\Pypi\gretry\test.py", line 18, in <module>
    run(name='郭一会儿')
  File "D:\Program\Python\Pypi\gretry\gretry\gretry.py", line 136, in wrapper
    return self.runner(func, *args, **kwargs)
  File "D:\Program\Python\Pypi\gretry\gretry\gretry.py", line 103, in runner
    raise exception
  File "D:\Program\Python\Pypi\gretry\gretry\gretry.py", line 74, in runner
    result = func(*args, **kwargs)
  File "D:\Program\Python\Pypi\gretry\test.py", line 14, in run
    raise FileExistsError('文件不存在！')
FileExistsError: 文件不存在！
```

## 示例 2

on_exceptions、ignore_exceptions 参数可以是错误的类型或者是列表

```
@retry(max_retry=3, on_exceptions=FileExistsError, ignore_exceptions=[OSError])
def run(name):
    raise FileExistsError('文件不存在！')
```

# 示例-error_jump

```
from gretry import retry, error_jump


def error(s):
    print('error1')


def error2(s):
    print('error2')


def success(res):
    print('success', res)


@error_jump(on_exceptions=FileExistsError, error_callback=error)
@error_jump(on_exceptions=FileNotFoundError, error_callback=error2)
@error_jump(callback=success)
def run(s):
    raise FileExistsError('1')


if __name__ == '__main__':
    run(2)
```