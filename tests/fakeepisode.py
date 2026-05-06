class FakeEpisode:
    def __init__(self, label: str) -> None:
        self.empty = False
        self._label = label

    def __str__(self) -> str:
        return self._label
