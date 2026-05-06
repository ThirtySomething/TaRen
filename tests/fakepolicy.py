class FakePolicy:
    def __init__(self, payload: bytes | None) -> None:
        self.payload = payload
        self.calls: list[tuple[str, dict[str, str]]] = []

    def fetch(self, url: str, headers: dict[str, str]) -> bytes | None:
        self.calls.append((url, headers))
        return self.payload
