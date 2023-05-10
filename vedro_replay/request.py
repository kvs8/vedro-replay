class Request:
    def __init__(self, request: str) -> None:
        self.request = request

    def __str__(self) -> str:
        return str(self.request)
