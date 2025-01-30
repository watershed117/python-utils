# event_loop - Python 事件循环实现

这是一个基于 Python 的轻量级事件循环实现，支持异步任务处理、参数验证、异常捕获和多线程协作。它适用于需要异步处理任务的场景，例如任务调度、事件驱动编程等。

## 功能特性

- **事件队列管理**：使用 `queue.Queue` 实现事件队列，支持多线程安全的事件添加和处理。
- **参数验证**：通过 `inspect` 模块实现方法参数的动态验证，支持类型检查和默认值处理。
- **异常处理**：自动捕获并返回事件处理过程中的异常，便于调试和错误处理。
- **多线程支持**：通过 `threading` 模块实现多线程协作，支持异步任务处理和结果等待。
- **UUID 事件标识**：每个事件分配唯一的 UUID，便于跟踪和管理事件状态。
- **灵活的事件格式**：支持多种事件格式（字符串、元组、字典），便于扩展和使用。

### 使用示例

以下是一个简单的使用示例：

```python
import time
from event_loop import EventLoop

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
```

### 输出示例

```
已提交事件 [正常调用] ID: 831f013a-841b-4740-a0a9-ec2e7be5c761
2025-01-28 23:22:35,894 - INFO - 事件 831f013a-841b-4740-a0a9-ec2e7be5c761 已处理
已提交事件 [关键字参数调用] ID: 6951edd7-e150-46f2-90ac-7ad41fb321d1
2025-01-28 23:22:35,894 - INFO - 事件 6951edd7-e150-46f2-90ac-7ad41fb321d1 已处理
已提交事件 [无参方法] ID: 4ebe5b55-a222-4c85-b479-8d84b1e80266
2025-01-28 23:22:35,894 - INFO - 事件 4ebe5b55-a222-4c85-b479-8d84b1e80266 已处理
已提交事件 [不存在的方法] ID: 909b9f1f-7373-41a0-9c55-3a6028ce3c95
2025-01-28 23:22:35,894 - INFO - 事件 909b9f1f-7373-41a0-9c55-3a6028ce3c95 已处理
已提交事件 [参数不足] ID: 8016e63c-0f21-4fc3-9a49-df7b4b043a96
2025-01-28 23:22:35,894 - INFO - 事件 8016e63c-0f21-4fc3-9a49-df7b4b043a96 已处理
已提交事件 [错误参数类型] ID: 00bf18b8-2511-49be-9414-2f7e174022d8
2025-01-28 23:22:35,894 - INFO - 事件 00bf18b8-2511-49be-9414-2f7e174022d8 已处理
已提交事件 [耗时任务] ID: 6e189f6c-9158-4731-bed3-daf63a1feb35
事件 [正常调用] 已处理，结果: 3
事件 [关键字参数调用] 已处理，结果: 7
事件 [无参方法] 已处理，结果: success
事件 [不存在的方法] 处理失败: Method 'invalid_method' not found
事件 [参数不足] 处理失败: Invalid arguments for 'test_method': 参数绑定失败: missing a required argument: 'arg2'
事件 [错误参数类型] 处理失败: Invalid arguments for 'test_method': 参数 'arg1' 需要 <class 'int'> 类型，实际得到 <class 'str'>
2025-01-28 23:22:40,901 - INFO - 事件 6e189f6c-9158-4731-bed3-daf63a1feb35 已处理
事件 [耗时任务] 已处理，结果: None
所有事件处理完成
event_results已处理完成
2025-01-28 23:22:40,901 - INFO - 事件循环停止
```

## 代码结构

- **`EventLoop` 类**：核心事件循环实现，包含事件队列管理、参数验证、异常处理等功能。
- **`validate_arguments` 装饰器**：用于验证方法参数的类型和格式。
- **`MethodNotFoundError` 和 `InvalidArgumentsError`**：自定义异常类，用于处理方法和参数错误。
- **`event_results` 字典**：存储事件处理结果，支持多线程访问。
