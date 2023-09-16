
class Salt:

    def __init__(self, salt: str):
        self.type = None
        self.text = None
        self.params = None

        if not salt:
            raise ValueError("salt must be a non-empty string")
        if salt[0] != "$":
            raise ValueError("salt string must start with '$'")

        try:
            index = 1
            extent = salt.index("$", index)
            self.type = int(salt[index:extent])

            index = extent + 1
            if index == len(salt):
                raise ValueError()

            extent = salt.find("$", index)
            if extent != -1 and "=" in salt[index:extent]:
                self.params = salt[index:extent]
                index = extent + 1
                if index == len(salt):
                    raise ValueError()
                extent = salt.find("$", index)

            self.text = salt[index:] if extent == -1 else salt[index:extent]

        except ValueError:
            raise ValueError("invalid salt format") from None

    def bytes(self, max_length: int, encoding="UTF-8"):
        return self.text.encode(encoding)[0:max_length]
