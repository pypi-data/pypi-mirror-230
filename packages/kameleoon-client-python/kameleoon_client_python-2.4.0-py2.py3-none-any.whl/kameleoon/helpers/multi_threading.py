"""Helpers for running functions in multi-threading"""

import asyncio
import threading
import concurrent.futures
import time
from typing import Any, Callable, Coroutine, Optional


class ThreadEventLoop:
    """
    ThreadEventLoop is helper object to handle asynchronous tasks execution in a separate thread.
    """

    def __init__(self) -> None:
        self.loop: Optional[asyncio.AbstractEventLoop] = None
        self.thread: Optional[threading.Thread] = None

    def __thread_main(self) -> None:
        self.loop = asyncio.new_event_loop()
        self.loop.run_forever()

    def start(self) -> None:
        """Starts the thread and the event loop"""
        if self.thread is not None:
            return
        self.thread = threading.Thread(target=self.__thread_main, daemon=True)
        self.thread.start()

    def __get_loop(self) -> asyncio.AbstractEventLoop:
        while self.loop is None:
            time.sleep(0.01)
        return self.loop

    def stop(self) -> None:
        """Stops the thread and the event loop"""
        if self.thread is None:
            return
        time.sleep(0.001)
        while self.count_tasks() > 0:
            time.sleep(0.01)
        loop = self.__get_loop()
        loop.call_soon_threadsafe(loop.stop)
        self.thread.join()
        loop.close()

    def run_coro(self, coro: Coroutine[Any, Any, Any]) -> concurrent.futures.Future[Any]:
        """
        Puts the specified coroutine to the event loop for background execution.
        :param coro: Coroutine to be executed
        :type coro: Coroutine[Any, Any, Any]
        """
        if self.thread is None:
            self.start()
        return asyncio.run_coroutine_threadsafe(coro, self.__get_loop())

    def count_tasks(self) -> int:
        """
        Returns the number of running tasks.
        """
        return len(asyncio.all_tasks(self.__get_loop()))


def run_in_thread(func: Callable[[], Any], thread_name: Optional[str] = None,
                  with_event_loop=False) -> threading.Thread:
    """
    It's a wrapper function which runs the `func` in another thread.
    :param func: Function need to be called
    :type func: Callable[[], Any]
    :param with_event_loop: Flag enabling management of event loop.
    :type with_event_loop: bool
    :param thread_name: Name of thread if `func` runs in another thread
    :type args: Optional[str]
    :return: Created thread
    :rtype: threading.Thread
    """
    if with_event_loop:
        def target():
            loop = asyncio.new_event_loop()
            func()
            loop.close()
    else:
        target = func
    thread = threading.Thread(target=target)
    thread.daemon = True
    if thread_name:
        thread.setName(thread_name)
    thread.start()
    return thread


def invoke_coro(coro: Coroutine[Any, Any, Any]) -> None:
    """
    Assigns the specified coroutine to a running event loop if has
    otherwise invokes the coroutine in a new event loop.
    """
    try:
        loop = asyncio.get_running_loop()
        loop.create_task(coro)
    except RuntimeError:
        get_loop().run_until_complete(coro)


def get_loop() -> asyncio.AbstractEventLoop:
    """Returns exisitng event loop or newly created one."""
    try:
        return asyncio.get_event_loop()
    except RuntimeError:
        return asyncio.new_event_loop()


def has_running_event_loop() -> bool:
    """Checks if has a running event loop."""
    try:
        asyncio.get_running_loop()
        return True
    except RuntimeError:
        return False
