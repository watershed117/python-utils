# event_loop - Python 事件循环实现

这是一个基于 Python 的轻量级事件循环实现，支持异步任务处理、参数验证、异常捕获和多线程协作。它适用于需要异步处理任务的场景，例如任务调度、事件驱动编程等。

---

## 功能特性

- **事件队列管理**：使用 `queue.Queue` 实现线程安全的事件队列，支持高效的任务调度和处理。
- **参数验证**：通过 `pydantic` 实现方法参数的动态验证，支持类型检查和默认值处理。
- **异常处理**：自动捕获并返回事件处理过程中的异常，提供详细的错误信息，便于调试和错误处理。
- **多线程支持**：通过 `threading` 模块实现多线程协作，支持异步任务处理和结果等待。
- **UUID 事件标识**：每个事件分配唯一的 UUID，便于跟踪和管理事件状态。
- **彩色日志输出**：通过 `colorama` 实现彩色日志输出，提升日志可读性。
- **线程安全设计**：使用 `threading.Lock` 和 `threading.Condition` 保证共享资源的线程安全。

---

## 使用示例

以下是一个简单的使用示例：

```python
if __name__ == "__main__":
    import time
    logger = setup_logging("root", False)

    class Test:        
        def test_method(self, arg1: int, arg2: int):
            """测试方法"""
            return arg1 + arg2

        def test_method2(self):
            """无参数测试方法"""
            return "success"
        
        def long_time_task(self):
            """耗时任务"""
            time.sleep(5)
            return None

    test_instance = Test()
    event_loop = EventLoop()
    t = threading.Thread(target=event_loop.run, daemon=True)
    t.start()

    # 提交测试用例
    event_ids = []
    event_ids.append(event_loop.add_event(test_instance.test_method, 1, 2))              # 正常调用
    event_ids.append(event_loop.add_event(test_instance.test_method, arg1=3,arg2=4))     # 关键字参数调用
    event_ids.append(event_loop.add_event(test_instance.test_method2))                   # 无参方法
    event_ids.append(event_loop.add_event(test_instance.test_method, 1))                 # 参数不足
    event_ids.append(event_loop.add_event(test_instance.test_method, "a", "b"))          # 错误参数类型
    event_ids.append(event_loop.add_event(test_instance.long_time_task))                 # 耗时任务

    # 等待测试用例处理完成
    for eid in event_ids[:]:
        result = event_loop.get_event_result(eid)
        if result["status"] == "error":
            logger.error(f"\n事件 {eid} 处理失败: {result['result']}")
        else:
            logger.info(f"\n事件 {eid} 已处理，结果: {result['result']}")
        event_ids.remove(eid)  # 移除已处理的事件ID

    logger.info("\n所有事件处理完成")
    if not event_loop.event_results:
        logger.info("\nevent_results已处理完成")
    else:
        logger.error("\nevent_results存在未处理的结果")
        logger.error(event_loop.event_results)

    # 发送停止事件
    event_loop.add_event("stop")
    t.join(timeout=1)
```

---

## 输出示例

```
2025-02-02 15:00:58 - EventLoop - DEBUG - 
事件 fdb34198-e7ce-425a-a1ad-cf6f61fad65e 处理成功: 
结果: 3
2025-02-02 15:00:58 - EventLoop - DEBUG - 
事件 fdb34198-e7ce-425a-a1ad-cf6f61fad65e 已处理
2025-02-02 15:00:58 - root - INFO - 
事件 fdb34198-e7ce-425a-a1ad-cf6f61fad65e 已处理，结果: 3
2025-02-02 15:00:58 - EventLoop - DEBUG - 
事件 d770e3bc-9508-48da-ad15-41c9b23b0d9c 处理成功:      
结果: 7
2025-02-02 15:00:58 - EventLoop - DEBUG - 
事件 d770e3bc-9508-48da-ad15-41c9b23b0d9c 已处理
2025-02-02 15:00:58 - root - INFO - 
事件 d770e3bc-9508-48da-ad15-41c9b23b0d9c 已处理，结果: 7
2025-02-02 15:00:58 - EventLoop - DEBUG - 
事件 3e3f2249-d48a-4182-9844-4f1c1170e56c 处理成功: 
结果: success
2025-02-02 15:00:58 - EventLoop - DEBUG - 
事件 3e3f2249-d48a-4182-9844-4f1c1170e56c 已处理
2025-02-02 15:00:58 - root - INFO -
事件 3e3f2249-d48a-4182-9844-4f1c1170e56c 已处理，结果: success
2025-02-02 15:00:58 - EventLoop - ERROR - 
事件 01c3ad60-62a0-45c2-aedf-320c8315eeb3 处理失败:
Invalid arguments for 'test_method':
参数校验失败 (arg2): Missing required argument
2025-02-02 15:00:58 - EventLoop - DEBUG - 
事件 01c3ad60-62a0-45c2-aedf-320c8315eeb3 已处理
2025-02-02 15:00:58 - root - ERROR -
事件 01c3ad60-62a0-45c2-aedf-320c8315eeb3 处理失败: Invalid arguments for 'test_method':
参数校验失败 (arg2): Missing required argument
2025-02-02 15:00:58 - EventLoop - ERROR - 
事件 16ffd59c-7688-4db9-b8d4-722bacfa2bfa 处理失败:
Invalid arguments for 'test_method':
参数校验失败 (0): Input should be a valid integer, unable to parse string as an integer
参数校验失败 (1): Input should be a valid integer, unable to parse string as an integer
2025-02-02 15:00:58 - EventLoop - DEBUG - 
事件 16ffd59c-7688-4db9-b8d4-722bacfa2bfa 已处理
2025-02-02 15:00:58 - root - ERROR -
事件 16ffd59c-7688-4db9-b8d4-722bacfa2bfa 处理失败: Invalid arguments for 'test_method':
参数校验失败 (0): Input should be a valid integer, unable to parse string as an integer
参数校验失败 (1): Input should be a valid integer, unable to parse string as an integer
2025-02-02 15:01:03 - EventLoop - DEBUG - 
事件 ab22c116-ff43-40ce-86b2-7a85e71c1413 处理成功: 
结果: None
2025-02-02 15:01:03 - EventLoop - DEBUG - 
事件 ab22c116-ff43-40ce-86b2-7a85e71c1413 已处理
2025-02-02 15:01:03 - root - INFO -
事件 ab22c116-ff43-40ce-86b2-7a85e71c1413 已处理，结果: None
2025-02-02 15:01:03 - root - INFO -
所有事件处理完成
2025-02-02 15:01:03 - root - INFO -
event_results已处理完成
2025-02-02 15:01:03 - EventLoop - INFO - 
事件循环停止
```

---

## 代码结构

### 核心类与方法

- **`EventLoop` 类**：事件循环的核心实现。
  - `add_event(func, *args, **kwargs)`：添加事件到队列，返回事件 ID。
  - `get_event_result(event_id)`：获取事件处理结果，支持阻塞等待。
  - `run()`：事件循环主逻辑，持续处理队列中的事件。
  - `call_function(func, *args, **kwargs)`：调用函数并处理参数验证和异常捕获。
  - `process_event(event)`：处理单个事件并返回结果或异常。

- **`ColoredFormatter` 类**：自定义日志格式，支持彩色输出。
  - `COLORS`：定义不同日志级别对应的颜色。
  - `format(record)`：格式化日志消息并添加颜色。

- **`setup_logging(name, color=True)`**：配置日志记录器，支持彩色日志输出。

### 自定义异常

- **`EventLoopError`**：事件循环异常基类。
- **`MethodNotFoundError`**：方法不存在异常。
- **`InvalidArgumentsError`**：参数无效异常，提供详细的错误信息。

---

## 适用场景

- **任务调度**：异步执行耗时任务，避免阻塞主线程。
- **事件驱动编程**：处理来自不同来源的事件（如网络请求、用户输入）。
- **批处理任务**：批量处理任务并收集结果。

---

## 依赖项

- Python 3.7+
- `pydantic`：用于参数验证。
- `colorama`：用于彩色日志输出。

---
