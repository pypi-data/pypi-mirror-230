from abc import ABC, abstractmethod


class LLMModel(ABC):
    @abstractmethod
    def __init__(
        self,
        model_name: str,
        api_key: str = None,
        api_secret: str = None,
        api_region: str = None,
    ):
        pass

    @staticmethod
    def _raise_api_error(credential_id: str, credential_name):
        raise ValueError(
            "Please provide "
            + credential_id
            + " parameter or set the "
            + credential_name
            + " environment variable."
        )

    @abstractmethod
    def chat(self, chat_input: str, parameters: dict = {}, is_stream: bool = False):
        pass


class LLMVendorClient(ABC):
    MODEL_MAPPING = {}

    def __init__(
        self, api_key: str = None, api_secret: str = None, api_region: str = None
    ):
        self.api_key = api_key
        self.api_secret = api_secret
        self.api_region = api_region

    def get_model(self, model_name: str):
        model_class_name = self.MODEL_MAPPING.get(model_name)
        if not model_class_name:
            raise ValueError(f"Unknown model: {model_name}")

        model_class = getattr(self, model_class_name)
        return model_class(
            model_name=model_name,
            api_key=self.api_key,
        )
