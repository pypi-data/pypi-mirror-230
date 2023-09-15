# -*- coding: utf-8 -*-
"""
重试机制，此装饰器只适用于装饰类中的方法，并且，调用的也是类中的方法，关键处在于：是否接收并传递self
"""
import time

from inspect import isfunction


def __after_exception(*args, **kwargs):
    pass


def __retry_error_callback(*args, **kwargs):
    pass


def retry(max_retry=3, current_times=0, wait=0, after_exception=__after_exception, retry_error_callback=__retry_error_callback, remark=""):
    """
    装饰器实现重试机制
    :param max_retry: 重试次数：默认3次，-1代表一直重试
    :param current_times: 当前重试次数
    :param wait: 每次重试的时间间隔
    :param after_exception: 重试睡眠前调用的函数
    :param retry_error_callback: 重试结束仍然失败时的回调函数
    :param remark: 备注
    :return:
    """

    def catch_exception(func):
        def wrapper(self, *args, **kwargs):
            nonlocal max_retry, current_times
            try:
                # 调用func
                res = func(self, *args, **kwargs)
                current_times = 0
                return res
            except Exception as e:
                current_times += 1
                kwargs["current_times"] = current_times
                kwargs["max_retry"] = max_retry
                kwargs["remark"] = remark

                # 睡眠前调用
                if isfunction(after_exception):
                    after_exception(self, *args, **kwargs)

                # 重试间隔
                time.sleep(wait)

                if max_retry == -1:
                    return wrapper(self, *args, **kwargs)
                elif current_times > max_retry:
                    if isfunction(retry_error_callback):
                        # 重试结束，执行回调函数
                        return retry_error_callback(self, *args, **kwargs)
                    else:
                        # 没有指定回调函数时，弹出错误
                        raise e
                else:
                    return wrapper(self, *args, **kwargs)

        # 设置current_times参数值
        def set_current_times(value):
            nonlocal current_times
            current_times = value

        wrapper.set_current_times = set_current_times
        return wrapper

    return catch_exception
