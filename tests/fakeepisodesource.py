class FakeEpisodeSource:
    def __init__(self, payload: str) -> None:
        self.payload = payload
        self.called = 0

    def fetch(self) -> str:
        self.called += 1
        return self.payload
