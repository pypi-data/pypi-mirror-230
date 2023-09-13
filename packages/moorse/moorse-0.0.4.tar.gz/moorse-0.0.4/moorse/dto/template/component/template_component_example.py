class TemplateComponentExample:

    header_text: list[str]
    body_text: list[list[str]]
    header_handle: list[str]

    def __init__(
        self, 
        header_text: list[str], 
        body_text: list[list[str]], 
        header_handle: list[str]
    ):
        self.header_text = header_text
        self.body_text = body_text
        self.header_handle = header_handle