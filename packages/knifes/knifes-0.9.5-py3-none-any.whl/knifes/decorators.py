from django.http import HttpRequest
from django.core.cache import cache
from django.conf import settings
from django.utils.translation import gettext as _
from knifes.results import ApiResponse
from typing import Union
from itertools import repeat
import time
import functools
import json
import pickle
from knifes.digests import md5
from knifes.constants import X_FOOTER, X_HEADER, CUSTOM_REQUEST_HEADERS
from knifes import aes
import logging
logger = logging.getLogger(__name__)
default_func_cache_timeout = 3600


# 装饰器 修饰的方法 第1个参数是 key
def func_cache(cache_key_prefix: Union[tuple, str]):
    if not isinstance(cache_key_prefix, tuple):
        cache_key_prefix = (cache_key_prefix, default_func_cache_timeout)

    def outer_wrapper(func):
        def wrapper(*args, **kwargs):
            if not args:  # 参数校验
                raise Exception('方法缺少缓存key')
            key = cache_key_prefix[0] + md5(str(args[0]))  # 避免args[0]过长
            result = cache.get(key)  # 尝试读取缓存
            if result:
                return pickle.loads(result)  # 使用pickle支持枚举、自定义类等
            result = func(*args, **kwargs)
            cache.set(key, pickle.dumps(result), timeout=cache_key_prefix[1])  # 写缓存
            return result
        return wrapper
    return outer_wrapper


def update_func_cache(cache_key_prefix: Union[tuple, str], args_0, result):
    if not isinstance(cache_key_prefix, tuple):
        cache_key_prefix = (cache_key_prefix, default_func_cache_timeout)
    key = cache_key_prefix[0] + md5(str(args_0))
    cache.set(key, pickle.dumps(result), timeout=cache_key_prefix[1])


def params_required(param_keys: list, is_get=False):
    def outer_wrapper(view_func):
        def wrapper(request: HttpRequest, *args, **kwargs):
            if param_keys and is_get:
                for param_key in param_keys:
                    if param_key not in request.GET or not request.GET[param_key]:
                        return ApiResponse.missing_param()
            elif param_keys:
                for param_key in param_keys:
                    if param_key not in request.POST or not request.POST[param_key]:
                        return ApiResponse.missing_param()
            return view_func(request, *args, **kwargs)
        return wrapper
    return outer_wrapper


def parse_and_verify_body_data(function=None, *, required_params: set = None, required_signature: bool = False):
    def actual_decorator(view_func):
        @functools.wraps(view_func)
        def wrapper(request: HttpRequest, *args, **kwargs):
            try:
                request.data = json.loads(request.body or '{}')
            except json.decoder.JSONDecodeError:  # 非json格式数据
                request.data = {}
            except UnicodeDecodeError as e:
                logger.critical(f'{e}, {request.body}')  # 报警
                request.data = {}
            # 校验参数
            if required_params and next((True for i in required_params if i not in request.data), False):
                return ApiResponse.missing_param()
            # 验证签名
            if not settings.DEBUG and required_signature:
                custom_headers = sorted({k: request.headers.get(k) for k in CUSTOM_REQUEST_HEADERS if k in request.headers}.items())
                custom_headers_str = "&".join("{}={}".format(k, v) for k, v in custom_headers)

                if request.headers.get(X_FOOTER) != md5(custom_headers_str + (request.body or bytes()).decode('utf-8') + settings.BODY_SIGN_KEY):
                    return ApiResponse.failure(_('非法请求'))
            return view_func(request, *args, **kwargs)
        return wrapper
    if function:
        return actual_decorator(function)
    return actual_decorator


def decrypt_and_verify_header_params(function=None, *, required_params: set = None, aes_header_key: str = None):
    def actual_decorator(view_func):
        @functools.wraps(view_func)
        def wrapper(request: HttpRequest, *args, **kwargs):
            x_header = request.headers.get(X_HEADER) or request.headers.get('vi')  # TODO 废弃vi

            if request.headers.get('vi'):
                logger.error('header还存在vi')

            if not x_header:
                return ApiResponse.missing_param(_('header缺少参数'))

            request.header_params = json.loads(aes.decrypt(x_header, aes_header_key or settings.AES_HEADER_KEY))
            if required_params and next((True for i in required_params if i not in request.header_params), False):
                return ApiResponse.missing_param(_('header缺少参数'))
            return view_func(request, *args, **kwargs)
        return wrapper
    if function:
        return actual_decorator(function)
    return actual_decorator


def retry(times=3, interval=(1, 5, 10), exclude_exception_tuple=()):
    """auto retry when function fails.

    This is designed as a decorator creator. To use the decorator, either use
    @retry() or @retry(times=3, interval=5) or @retry(times=3, interval=[1, 5,
    10])

    A function is considered failed when it raised an unhandled exception.

    Args:
        times: max retry times. so function may run 1 + times in worst case.
        interval: if set to an int/float, means retry after these many seconds. no interval if 0.
                  if set to an iterable, means retry interval for each retry;
                  if interval iterable is shorter than times, the last value
                  will be used for remaining retries.
                  default interval is (1, 5, 10).
        exclude_exception_tuple: exclude exception class

    Return:
        a decorator which when used, will return what the decorated func
        returns, but with auto retry support.

    """
    def gen_wrapper(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            retry_time = 0
            if isinstance(interval, (int, float)):
                interval_iter = repeat(interval)
            else:
                interval_iter = iter(interval)
            while True:
                try:
                    return func(*args, **kwargs)
                except Exception as e:    # pylint: disable=broad-except
                    if retry_time >= times:
                        logger.error(f'{func.__name__}, max retry reached, {retry_time}')
                        raise
                    if exclude_exception_tuple and isinstance(e, exclude_exception_tuple):
                        raise
                    try:
                        seconds = next(interval_iter)  # pylint: disable=redefined-outer-name
                    except StopIteration:
                        interval_iter = repeat(seconds)  # last loop value
                    time.sleep(seconds)
                    retry_time += 1
                    logger.debug(f'{func.__name__} sleeping {seconds} before auto retry')
        return wrapper
    return gen_wrapper
