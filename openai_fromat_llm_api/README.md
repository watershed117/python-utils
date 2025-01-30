## 概述

一个与OpenAI格式api进行交互的工具，支持同步和异步两种方式。通过该工具，用户可以轻松地与LLM进行对话、管理聊天记录、处理文件（如图像和音频）并将其转换为模型可接受的格式。项目还提供了聊天记录的保存与加载功能，方便用户在不同会话之间切换。

## 特性

- **与LLM交互**：支持同步和异步方式与LLM进行对话。
- **聊天记录管理**：支持保存、加载、删除聊天记录，并自动管理聊天记录的长度。
- **文件处理**：支持将图像和音频文件转换为Base64编码，并生成符合模型要求的消息格式。
- **工具调用**：支持从聊天记录中提取最近的工具调用记录。
- **异步支持**：使用`httpx`和`aiofiles`库实现异步操作，提升性能。

## 快速开始

### 安装依赖

确保已安装以下Python库：

```bash
pip install requests httpx aiofiles
```

### 使用示例

#### 同步调用

```python
from base_llm import Base_llm
from message_generator import MessageGenerator, GEMINI

# 初始化LLM客户端
chat = Base_llm(
    base_url="https://gemini.watershed.ip-ddns.com/v1",
    model="deepseek-chat",
    api_key="your_api_key",
    storage="path_to_storage",
    system_prompt="使用中文回复",
    proxy=None
)

# 初始化消息生成器
message_generator = MessageGenerator(format="openai", file_format=GEMINI, ffmpeg_path="ffmpeg")

# 生成包含图像的消息
message = message_generator.gen_user_msg("分析图片内容", ["path_to_image.png"])

# 发送消息并获取响应
result = chat.send(messages=message)
print(result)
```

#### 异步调用

```python
import asyncio
from base_llm import Async_Base_llm

async def main():
    # 初始化异步LLM客户端
    chat = Async_Base_llm(
        base_url="https://open.bigmodel.cn/api/paas/v4",
        model="glm-4-flash",
        api_key="your_api_key",
        storage="path_to_storage",
        limit="8k",
        proxy=None
    )

    # 加载聊天记录
    conversation_id = await chat.load("conversation_id")
    print(conversation_id)

    # 获取最近的工具调用记录
    tool_recall = chat.latest_tool_recall(chat.chat_history, "tool_name")
    print(tool_recall)

    # 获取最新的助手消息
    latest_message = chat.get_latest_message(chat.chat_history)
    print(latest_message)

    # 获取所有对话记录
    conversations = await chat.get_conversations()
    print(conversations)

    # 发送消息并获取响应
    result = await chat.send({"role": "user", "content": "你好"})
    print(result)

    # 保存聊天记录
    save_result = await chat.save(conversation_id)
    print(save_result)

    # 删除聊天记录
    chat.delete_conversation(conversation_id)

asyncio.run(main())
```

## 主要类与方法

### `Base_llm` 类

- **`__init__`**: 初始化LLM客户端，设置API密钥、模型、存储路径等。
- **`send`**: 发送消息到LLM并获取响应。
- **`save`**: 保存当前聊天记录到文件。
- **`load`**: 从文件加载聊天记录。
- **`clear_history`**: 清除聊天记录，保留系统提示。
- **`tokenizer`**: 计算消息的token数量。
- **`del_earliest_history`**: 删除最早的聊天记录。
- **`limiter`**: 限制聊天记录的长度，确保不超过最大token限制。
- **`latest_tool_recall`**: 获取最近的工具调用记录。
- **`get_latest_message`**: 获取最新的助手消息。

### `Async_Base_llm` 类

继承自`Base_llm`，提供异步版本的`send`、`save`、`load`等方法。

### `MessageGenerator` 类

- **`gen_user_msg`**: 生成包含文本和文件（图像或音频）的用户消息。
- **`audio_to_base64`**: 将音频文件转换为Base64编码。
- **`image_to_base64`**: 将图像文件转换为Base64编码。
- **`ffmpeg_convert`**: 使用ffmpeg转换文件格式。

## 文件格式支持

### `File_Format` 类

定义了支持的图像和音频文件格式。

- **`CHATGPT`**: 支持`.png`, `.jpeg`, `.jpg`, `.webp`, `.gif`等图像格式，以及`.wav`, `.mp3`等音频格式。
- **`GEMINI`**: 支持更多的图像和音频格式，如`.heic`, `.heif`, `.aiff`, `.aac`, `.ogg`, `.flac`等。

## 许可证

本项目采用MIT许可证，详情请参阅LICENSE文件。
