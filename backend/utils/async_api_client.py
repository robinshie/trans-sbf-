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

    async def async_request(self, method: str, endpoint: str, **kwargs) -> Dict:
        """
        发送异步 HTTP 请求（支持 GET / POST）。
        """
        url = f"{self.base_url}/{endpoint.strip('/')}"
        
        try:
            response = await self.client.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise Exception(f"HTTP Error: {e.response.status_code} - {e.response.text}")
        except json.JSONDecodeError:
            raise Exception("Invalid JSON response from API")

    async def async_stream_request(self, endpoint: str, **kwargs) -> AsyncGenerator[str, None]:
        """
        发送流式请求（streaming），并解析逐步返回的 JSON 数据。
        """
        url = f"{self.base_url}/{endpoint.strip('/')}"
        
        async with self.client.stream("POST", url, **kwargs) as response:
            if response.status_code != 200:
                error_msg = await response.text()
                raise Exception(f"API error: {error_msg}")
            async for line in response.aiter_lines(): 
                try:
                    chunk = json.loads(line)
                    # 解析 `content`
                    if "message" in chunk and "content" in chunk["message"]:
                        yield chunk["message"]["content"]
                    # 解析 `reasoning_content`
                    elif "reasoning_content" in chunk:
                        yield chunk["reasoning_content"]
                except json.JSONDecodeError:
                    continue

