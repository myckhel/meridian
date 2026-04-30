from app.core.config import get_settings
from app.ui.gradio_app import demo


settings = get_settings()


if __name__ == "__main__":
    demo.launch(server_name=settings.gradio_server_name, server_port=settings.gradio_server_port)