class FakeConfig:
    def __init__(self, values: dict[str, str]) -> None:
        self._values = values

    def value_get(self, section: str, key: str) -> str:
        return self._values[f"{section}.{key}"]
