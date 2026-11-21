import gradio as gr
import uvicorn

from app.main import app as fastapi_app

demo = gr.Interface(fn=lambda x: "WeekendYatri API is live! Visit /health or /docs", inputs="text", outputs="text")
app = gr.mount_gradio_app(fastapi_app, demo, path="/ui")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=7860)
