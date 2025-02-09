import json
import httpx
from typing import Dict, AsyncGenerator, Optional


class AsyncAPIClient:
    """
    通用异步 API 客户端，封装 httpx.AsyncClient 提供 HTTP 请求能力。
    支持流式请求（streaming）和非流式请求，兼容 DeepSeek 和 OpenAI 的响应格式。
    """

    _client: Optional[httpx.AsyncClient] = None  # 共享 HTTPX AsyncClient 连接池

    def __init__(self, base_url: str, timeout: int = 30):
        """
        初始化异步 API 客户端。

        :param base_url: API 根 URL
        :param timeout: 请求超时时间（秒），默认 30 秒
        """
        self.base_url = base_url
        self.timeout = timeout

        if not AsyncAPIClient._client:
            AsyncAPIClient._client = self._create_client()
        self.client = AsyncAPIClient._client

    @classmethod
    def _create_client(cls) -> httpx.AsyncClient:
        """
        创建全局 HTTPX AsyncClient 实例（使用 `AsyncHTTPTransport` 以支持异步请求）。

        :return: httpx.AsyncClient 实例
        """
        transport = httpx.AsyncHTTPTransport(
            limits=httpx.Limits(
                max_keepalive_connections=10,
                max_connections=100,
            )
        )
        return httpx.AsyncClient(transport=transport, follow_redirects=True)

    async def close(self):
        """
        关闭全局 HTTPX AsyncClient 实例，释放资源。
        """
        if AsyncAPIClient._client:
            await AsyncAPIClient._client.aclose()
            AsyncAPIClient._client = None

    async def async_request(self, method: str, endpoint: str, **kwargs) -> Dict:
        """
        发送非流式请求，返回完整的 JSON 响应。

        :param method: HTTP 方法（如 "GET", "POST"）
        :param endpoint: API 端点路径
        :param kwargs: 其他请求参数（如 headers, json, params 等）
        :return: 解析后的 JSON 响应
        :raises Exception: 如果请求失败或响应状态码非 200
        """
        url = f"{self.base_url}/{endpoint.strip('/')}"
        try:
            response = await self.client.request(
                method, url, timeout=self.timeout, **kwargs
            )
            response.raise_for_status()  # 如果状态码非 2xx，抛出异常
            return response.json()
        except httpx.HTTPStatusError as e:
            error_msg = await e.response.aread()
            raise Exception(f"API error: {error_msg}")
        except json.JSONDecodeError:
            raise Exception("Failed to decode JSON response")

    async def async_stream_request(self, endpoint: str, **kwargs) -> AsyncGenerator[str, None]:
        """
        发送流式请求（streaming），并逐步解析返回的 JSON 数据。
        兼容 DeepSeek 和 OpenAI 的不同格式。

        :param endpoint: API 端点路径
        :param kwargs: 其他请求参数（如 headers, json, params 等）
        :return: 异步生成器，逐步返回解析后的内容
        :raises Exception: 如果请求失败或响应状态码非 200
        """
        url = f"{self.base_url}/{endpoint.strip('/')}"

        async with self.client.stream("POST", url, timeout=self.timeout, **kwargs) as response:
            if response.status_code != 200:
                error_msg = await response.aread()
                raise Exception(f"API error: {error_msg}")

            async for line in response.aiter_lines():
                line = line.strip()
                if line.startswith(": keep-alive"):
                    continue
                if not line:
                    continue
                if not line or not line.startswith("data: "):
                    chunk = json.loads(line)  # 解析 JSON，去掉 "data: " 前缀
                    yield self._extract_content(chunk)  # 提取内容

                try:
                    chunk = json.loads(line[6:])  # 解析 JSON，去掉 "data: " 前缀
                    yield self._extract_content(chunk)  # 提取内容
                except json.JSONDecodeError:
                    continue  # 跳过解析失败的 JSON 数据

    def _extract_content(self, chunk: Dict) -> str:
        """
        从 JSON 数据块中提取内容，兼容 DeepSeek 和 OpenAI 格式。

        :param chunk: JSON 数据块
        :return: 提取的内容
        """
        # 处理 DeepSeek 格式
        if "message" in chunk:
            if "content" in chunk["message"]:
                return chunk["message"]["content"]
            elif "reasoning_content" in chunk["message"]:
                return chunk["message"]["reasoning_content"]

        # 处理 OpenAI 格式
        elif "choices" in chunk:
            delta = chunk["choices"][0].get("delta", {})
            if "content" in delta:
                return delta["content"]
            elif "refusal" in delta:
                return delta["refusal"]

        return ""  # 如果没有匹配的内容，返回空字符串