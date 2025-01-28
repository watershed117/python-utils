import queue
import logging
import inspect
import threading
import uuid
from typing import Any, Callable, Dict, Tuple, Optional, Union

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class EventLoopError(Exception):
    """事件循环异常基类"""
    pass

class MethodNotFoundError(EventLoopError):
    """方法不存在异常"""
    def __init__(self, method_name: str):
        super().__init__(f"Method '{method_name}' not found")
        self.method_name = method_name

class InvalidArgumentsError(EventLoopError):
    """参数验证失败异常"""
    def __init__(self, method_name: str, error: str):
        super().__init__(f"Invalid arguments for '{method_name}': {error}")
        self.method_name = method_name
        self.error = error

class EventLoop:
    def __init__(self):
        self.event_results = {}
        self.event_queue = queue.Queue()
        self.lock = threading.Lock()
        self.condition = threading.Condition(self.lock)

    @staticmethod
    def validate_arguments(func: Callable) -> Callable:
        """参数验证装饰器（带类型检查）"""
        def wrapper(self, *args: Any, **kwargs: Any) -> Any:
            sig = inspect.signature(func)
            try:
                bound = sig.bind(self, *args, **kwargs)
                bound.apply_defaults()
            except TypeError as e:
                error_msg = f"参数绑定失败: {str(e)}"
                raise InvalidArgumentsError(func.__name__, error_msg) from e

            for name, value in bound.arguments.items():
                if name == 'self':
                    continue
                    
                param = sig.parameters[name]
                ann = param.annotation
                
                if ann is inspect.Parameter.empty:
                    continue
                    
                if getattr(ann, '__origin__', None) is Union:
                    allowed_types = ann.__args__
                    if not isinstance(value, allowed_types):
                        raise InvalidArgumentsError(
                            func.__name__,
                            f"参数 '{name}' 需要 {ann} 类型，实际得到 {type(value)}"
                        )
                else:
                    if not isinstance(value, ann):
                        raise InvalidArgumentsError(
                            func.__name__,
                            f"参数 '{name}' 需要 {ann} 类型，实际得到 {type(value)}"
                        )

            return func(self, *args, **kwargs)
        
        return wrapper

    def call_method(self, method_name: str, *args: Any, **kwargs: Any) -> Any:
        """调用方法并处理异常"""
        if not hasattr(self, method_name):
            raise MethodNotFoundError(method_name)
            
        method = getattr(self, method_name)
        if not callable(method):
            raise TypeError(f"属性 {method_name} 不可调用")
            
        return method(*args, **kwargs)

    def _parse_event(self, event: Any) -> Tuple[str, Tuple, Dict]:
        if isinstance(event, tuple) and len(event) >= 1:
            method_name = event[0]
            args = event[1] if len(event) > 1 and isinstance(event[1], tuple) else ()
            kwargs = event[2] if len(event) > 2 and isinstance(event[2], dict) else {}
            return method_name, args, kwargs
        elif isinstance(event, str):
            return event, (), {}
        else:
            raise EventLoopError(f"无效事件格式: {type(event)}")

    def process_event(self, event: Any) -> Any:
        """处理事件并返回结果或异常"""
        try:
            method_name, args, kwargs = self._parse_event(event)
            return self.call_method(method_name, *args, **kwargs)
        except Exception as e:
            return e

    def add_event(self, event: Any) -> uuid.UUID:
        """添加事件并返回UUID作为ID"""
        event_id = uuid.uuid4()
        with self.lock:
            self.event_results[event_id] = {"status": "pending", "result": None}
        self.event_queue.put((event_id, event))
        return event_id

    def get_event_result(self, event_id: uuid.UUID) -> Optional[Any]:
        """获取结果，如果结果未就绪则等待"""
        with self.condition:
            if event_id not in self.event_results:
                raise EventLoopError(f"Event {event_id} does not exist or has been removed")
            
            # 等待事件完成的通知
            while self.event_results[event_id]["status"] == "pending":
                self.condition.wait()  # 释放锁并等待，收到通知后重新获取锁
            
            result = self.event_results[event_id]["result"]
            del self.event_results[event_id]  # 删除结果
            return result
        
    def run(self):
        """事件循环主逻辑"""
        while True:
            event_id, event = self.event_queue.get()
            try:
                if event == "stop":
                    logging.info("事件循环停止")
                    break
                
                result = self.process_event(event)
                
                with self.condition:
                    self.event_results[event_id] = {"status": "completed", "result": result}
                    self.condition.notify_all()  # 通知所有等待的线程
                
                logging.info(f"事件 {event_id} 已处理")
                
            finally:
                self.event_queue.task_done()


if __name__ == "__main__":
    import time
    class Test(EventLoop):
        @EventLoop.validate_arguments
        def test_method(self, arg1: int, arg2: int):
            """测试方法"""
            return arg1 + arg2

        @EventLoop.validate_arguments
        def test_method2(self):
            """无参数测试方法"""
            return "success"
        
        @EventLoop.validate_arguments
        def long_time_task(self):
            """耗时任务"""
            time.sleep(5)
            return None

    test = Test()
    t = threading.Thread(target=test.run, daemon=True)
    t.start()

    # 定义测试用例
    test_cases = [
        ("正常调用", ("test_method", (1, 2), {})),
        ("关键字参数调用", ("test_method", (), {"arg1": 3, "arg2": 4})),
        ("无参方法", ("test_method2",)),
        ("不存在的方法", ("invalid_method",)),
        ("参数不足", ("test_method", (1,))),
        ("错误参数类型", ("test_method", ("a", "b"))),
        ("耗时任务", ("long_time_task",)),  # 添加耗时任务
        ("停止事件", "stop")
    ]

    # 提交测试用例
    event_ids = []
    for desc, event in test_cases[:-1]:  # 最后一个事件（停止事件）单独处理
        eid = test.add_event(event)
        event_ids.append((desc, eid))
        print(f"已提交事件 [{desc}] ID: {eid}")

    # 等待所有事件完成

    for desc, eid in event_ids:
        result = test.get_event_result(eid)
        if isinstance(result, Exception):
            print(f"事件 [{desc}] 处理失败: {result}")
        else:
            print(f"事件 [{desc}] 已处理，结果: {result}")
        event_ids.remove((desc, eid))

    # while event_ids:
    #     for desc, eid in event_ids[:]:  # 使用 event_ids[:] 创建副本以避免修改迭代中的列表
    #         if eid in test.event_results:
    #             status = test.event_results[eid]["status"]
    #             if status == "completed":
    #                 result = test.get_event_result(eid)
    #                 if isinstance(result, Exception):
    #                     print(f"事件 [{desc}] 处理失败: {result}")
    #                 else:
    #                     print(f"事件 [{desc}] 已处理，结果: {result}")
    #                 event_ids.remove((desc, eid))  # 从列表中移除已完成的任务
    #             else:
    #                 pass
    #                 # print(f"事件 [{desc}] 仍在进行中")
    #         else:
    #             print(f"事件 [{desc}] 不存在或已被移除")
    #             event_ids.remove((desc, eid))  # 从列表中移除无效的任务
    #     time.sleep(1)  # 每隔 1 秒检查一次

    print("所有事件处理完成")
    if not test.event_results:
        print("event_results已处理完成")
    else:
        print("event_results存在未处理的结果")

    # 发送停止事件
    test.add_event("stop")
    t.join(timeout=1)
