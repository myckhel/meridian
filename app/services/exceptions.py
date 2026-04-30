class ChatServiceError(Exception):
    pass


class ChatConfigurationError(ChatServiceError):
    pass


class UpstreamServiceError(ChatServiceError):
    pass