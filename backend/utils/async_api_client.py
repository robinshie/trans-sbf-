import json
import httpx
from typing import Dict, AsyncGenerator


class AsyncAPIClient:
    """
    通用异步 API 客户端，封装 httpx.AsyncClient 提供 HTTP 请求能力。
    """

    _client = None  # 共享 HTTPX AsyncClient 连接池

    def __init__(self, base_url: str):
        """
        :param base_url: API 根 URL
        """
        self.base_url = base_url

        if not AsyncAPIClient._client:
            AsyncAPIClient._client = self._create_client()
        self.client = AsyncAPIClient._client

    @classmethod
    def _create_client(cls):
        """
        创建全局 HTTPX AsyncClient 实例（使用 `AsyncHTTPTransport` 以支持异步请求）。
        """
        transport = httpx.AsyncHTTPTransport(  # ✅ 改用 AsyncHTTPTransport
            limits=httpx.Limits(
                max_keepalive_connections=10,
                max_connections=100
            )
        )
        return httpx.AsyncClient(transport=transport)

    async def async_stream_request(self, endpoint: str, **kwargs) -> AsyncGenerator[str, None]:
        """
        发送流式请求（streaming），并解析逐步返回的 JSON 数据。
        兼容 DeepSeek 和 OpenAI 的不同格式。
        """
        url = f"{self.base_url}/{endpoint.strip('/')}"

        async with self.client.stream("POST", url, **kwargs) as response:
            if response.status_code != 200:
                error_msg = await response.text()
                raise Exception(f"API error: {error_msg}")

            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    try:
                        chunk = json.loads(line[6:])  # 去掉 "data: " 前缀
                        
                        # ✅ 处理 DeepSeek 格式
                        if "message" in chunk:
                            if "content" in chunk["message"]:
                                yield chunk["message"]["content"]
                            elif "reasoning_content" in chunk["message"]:
                                yield chunk["message"]["reasoning_content"]

                        # ✅ 处理 OpenAI 格式
                        elif "choices" in chunk:
                            delta = chunk["choices"][0].get("delta", {})
                            if "content" in delta:
                                yield delta["content"]
                            elif "refusal" in delta:
                                yield delta["refusal"]

                    except json.JSONDecodeError:
                        continue

