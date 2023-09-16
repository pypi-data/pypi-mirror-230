class ParseError(Exception):  # pragma: no cover
    def __init__(self, message: str = "Parse Error !"):
        self.message = message
        super().__init__(self.message)
    # endDef
# endClass
