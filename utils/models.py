from pydantic import BaseModel

# 定义请求体模型
class CodeRequest(BaseModel):
    language: str
    code: str