import toml


class Configuration:
    @staticmethod
    def load(path: str) -> dict:
        return toml.load(path)
