import json

class ContentItem:
    """
    用于表示一个通用的 content 项，通过 'type' 字段区分不同类型。
    """
    def __init__(self, type_, **kwargs):
        """
        :param type_: 表示类型，比如 "text" 或 "image_url" 等
        :param kwargs: 存放与此类型相关的其他字段
        """
        self.type_ = type_
        self.fields = kwargs  # 其他字段动态保存在 fields

    def to_dict(self):
        """
        根据 self.type_ 输出对应的字典结构。
        也可在这里面做更多条件判断，以处理不同类型的特殊字段。
        """
        # 这里做一个简单的映射示例：
        if self.type_ == "text":
            # 需要: {"type": "text", "text": "..."}
            return {
                "type": "text",
                "text": self.fields.get("text", "")
            }
        elif self.type_ == "image_url":
            # 需要: {"type": "image_url", "image_url": "data:image/png;base64,xxx"}
            base64_str = self.fields.get("image_base64", "")
            return {
                "type": "image_url",
                "image_url": f"data:image/png;base64,{base64_str}"
            }
        else:
            # 对于没特判的其他类型，保留原样或根据业务需求定制
            return {
                "type": self.type_,
                **self.fields
            }


class Message:
    """
    将多个 ContentItem 收集并生成 {"content": [...]} 的结构。
    """
    def __init__(self):
        self.content_list = []

    def add_item(self, type_, **kwargs):
        """
        使用 type_ 和额外参数 (kwargs) 创建 ContentItem，再放入 self.content_list。
        """
        item = ContentItem(type_, **kwargs)
        self.content_list.append(item)

    def to_dict(self) -> dict:
        """
        输出整个 Message 的字典形式
        {
            "content": [item1, item2, ...]
        }
        """
        return {
            "content": [i.to_dict() for i in self.content_list]
        }

    def to_json(self, **json_kwargs) -> str:
        """
        将字典结构序列化为 JSON 字符串
        """
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2, **json_kwargs)


# ===== 使用示例 =====
if __name__ == "__main__":
    msg = Message()

    # 添加一个文本类型
    msg.add_item("text", text="这是一个文本")

    # 添加一个图片类型（这里示例 base64）
    test_base64 = "iVBORw0KGgoAAAANSUhEU..."
    msg.add_item("image_url", image_base64=test_base64)

    # 也可以随意添加其它自定义类型
    msg.add_item("audio_url", url="http://example.com/music.mp3", duration=30)

    # 获取 Python 字典
    data_dict = msg.to_dict()
    print("Dict:", data_dict)

    # 获取 JSON 字符串
    data_json = msg.to_json()
    print("\nJSON:", data_json)
