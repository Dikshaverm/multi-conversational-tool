import fastapi

from langchain_openai import ChatOpenAI, AzureChatOpenAI
from langchain_groq import ChatGroq
from domains.settings import config_settings
from domains.retreival.chat_handler import StreamingLLMCallbackHandler
from loguru import logger


def get_chat_model(model_key: str ="CHAT_MODEL_NAME", temperature=0.0):
    try:
        if config_settings.LLM_SERVICE == "openai":
            return ChatOpenAI(
                model=config_settings.LLMS.get(model_key, "gpt-4o"),
                temperature=temperature,
                api_key=config_settings.OPENAI_API_KEY,
            )

        elif config_settings.LLM_SERVICE == "groq":
            return ChatGroq(
                model=config_settings.GROQ_MODEL_SETTINGS.get(model_key, "gpt-4o"),
                temperature=temperature,
            )

    except Exception as e:
        logger.error(f"Error while getting chat model: {e}")
        return None


def get_chat_model_with_streaming(
    websocket: fastapi.WebSocket,
    model_key: str = "CHAT_MODEL_NAME",
    temperature: float = 0.0,
):
    try:
        if config_settings.LLM_SERVICE == "openai":
            return ChatOpenAI(
                model=config_settings.LLMS.get(model_key, "gpt-4o-mini"),
                temperature=temperature,
                streaming=True,
                callbacks=[StreamingLLMCallbackHandler(websocket)],
                stream_usage=True,
                api_key=config_settings.OPENAI_API_KEY,
            )

        elif config_settings.LLM_SERVICE == "groq":
            return ChatGroq(
                model=config_settings.GROQ_MODEL_SETTINGS.get(model_key, None),
                temperature=temperature,
            )

    except Exception as e:
        logger.error(f"Failed to get chat model with streaming: {e}")
        raise
