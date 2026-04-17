import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict
from agent.react_agent import ReactAgent

app = FastAPI()

# 允许跨域
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载静态文件（前端）
app.mount("/static", StaticFiles(directory="static"), name="static")

# 挂载Vue构建的静态文件
@app.get("/dist/{path:path}")
async def serve_vue_dist(path: str):
    """服务Vue构建的静态文件"""
    from fastapi.responses import FileResponse
    import os

    file_path = os.path.join("static/dist", path)
    if os.path.exists(file_path):
        return FileResponse(file_path)
    raise HTTPException(status_code=404, detail="File not found")

# 服务Vue应用的主入口
@app.get("/{path:path}")
async def serve_vue_app(path: str = ""):
    """服务Vue应用的HTML入口"""
    from fastapi.responses import FileResponse
    import os

    # 如果是API路由，不处理
    if path.startswith("chat") or path.startswith("static"):
        raise HTTPException(status_code=404, detail="Not found")

    # 服务Vue应用的index.html
    index_path = "frontend/index.html"
    if os.path.exists(index_path):
        return FileResponse(index_path)

    # 如果Vue应用不存在，返回简单的错误信息
    raise HTTPException(status_code=404, detail="Vue应用未找到，请先构建前端")

# 全局 Agent 实例
agent = ReactAgent()

class ChatRequest(BaseModel):
    messages: List[Dict[str, str]]

@app.post("/chat")
async def chat(request: ChatRequest):
    try:
        return StreamingResponse(
            agent.execute_stream(request.messages),
            media_type="text/plain; charset=utf-8"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)