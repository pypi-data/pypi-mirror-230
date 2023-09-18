import colorama

colorama.init(autoreset=True)


class Message:
    def __init__(self) -> None:
        self.info_text = colorama.Fore.GREEN
        self.warn_text = colorama.Fore.LIGHTRED_EX
        self.error_text = colorama.Fore.RED
        self.hint_text = colorama.Fore.YELLOW

    def printit(self, text: str, message_type: str = "info") -> None:
        if message_type == "info":
            print(self.info_text + text)
        elif message_type == "warn":
            print(self.warn_text + text)
        elif message_type == "error":
            print(self.error_text + text)
        else:
            print(self.hint_text + text)
