import os


class SQLQuery:
    def __init__(self) -> None:
        self.dir = f"{os.path.dirname(__file__)}/queries"

    def take(self, name: str, **kwargs) -> str:
        try:
            with open(f"{self.dir}/{name}.sql", "r") as file:
                file_content = file.read()
        except Exception as e:
            return str(e)

        for key, value in kwargs.items():
            file_content.replace(f"@{key}", value)

        return file_content
