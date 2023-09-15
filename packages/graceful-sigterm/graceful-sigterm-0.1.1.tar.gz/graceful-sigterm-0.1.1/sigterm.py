"""接收来自操作系统的kill信号，并优雅地等待工作线程结束。

接收kill命令发出的TERM信号，以及接收Ctrl+C发出的INT信号，等待工作线程安全退出。
如果需要实现`kill HUP`类似的功能，可以自行设计signal.SIGHUP的回调函数，并注册该回调函数。

要求所有具体工作都在工作线程中执行。
主线程仅用于接收操作系统信号，以及等待工作线程结束。

注意：当接收到退出信号时，程序应该立即准备退出，包括：
1、尽快保存工作状态。
2、已获取但还没有开始的任务应该考虑放回队列。
3、所有阻塞式等待都应该设置超时时间，超时时间必须小于退出等待时间。
"""
import time
import signal
import logging
import threading

__all__ = [
    "set_graceful_timeout",
    "is_stopped",
    "wait_until_stop",
    "register_worker_thread",
    "register_worker",
    "setup",
    "execute",
]

_logger = logging.getLogger(__name__)

_STOP_EVENT = threading.Event()
_STOP_FLAG = False
_STOP_TIME = None
_WORKERS = []
_GRACEFUL_TIMEOUT = 300  # 等待工作线程退出的时间，默认300秒（5分钟）


def set_graceful_timeout(timeout):
    """重新设置退出等待时间。单位：秒。"""
    global _GRACEFUL_TIMEOUT
    _GRACEFUL_TIMEOUT = timeout


def default_handler(*args, **kwargs):
    """默认的退出事件回调函数。主要完成：

    1. 设置程序退出标识。
    2. 设置程序退出事件。
    3. 等待所有工作线程退出。如果工作线程在规定时间内没有退出，则强制退出。
    """
    _logger.info("get TERM signal, prepare to stop server...")
    global _STOP_FLAG
    global _STOP_TIME
    global _STOP_EVENT
    _STOP_FLAG = True
    _STOP_EVENT.set()
    _STOP_TIME = time.time()
    for t in _WORKERS:
        timeout = _GRACEFUL_TIMEOUT - (time.time() - _STOP_TIME)
        t.join(timeout=timeout)


def is_stopped():
    """判断程序是否已经接收到了退出事件。"""
    return _STOP_FLAG


def wait_until_stop(timeout=None):
    """等待程序退出事件。"""
    _STOP_EVENT.wait(timeout=timeout)


def register_worker_thread(thread):
    """注册工作线程。"""
    _WORKERS.append(thread)
    return thread


def register_worker(worker):
    """注册工作回调函数，并自动生成工作线程。"""
    t = threading.Thread(target=worker, daemon=True)
    _WORKERS.append(t)
    return t


def setup(sig=signal.SIGTERM, handler=default_handler):
    """注册KILL事件回调函数。"""
    _logger.info("signal setup: sig={}, handler={}".format(sig, handler))
    signal.signal(sig, handler)


def execute():
    """启动工作线程，主线程进入等待。"""
    _logger.info("start workers...")
    for t in _WORKERS:
        t.start()
    while not is_stopped():
        for t in _WORKERS:
            try:
                t.join(3600)
                _logger.info("worker {} end.".format(t))
            except Exception as error:
                _logger.warning("main thread waiting error: {}".format(error))
    _logger.info("main thread end.")
