class RuleNotFound(Exception):
    def __init__(self, cmd: str):
        super().__init__(f"Rules not matched with command: {cmd}")
