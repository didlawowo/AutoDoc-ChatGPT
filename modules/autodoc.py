import os
from time import sleep

from colorama import init as colorama_init

from revChatGPT.V1 import Chatbot
from modules.prompt import Prompt
from modules.divider import Divider
from modules.settings import *
from modules.result import Result

from rich.console import Console

console = Console()

colorama_init()


class AutoDoc:
    def __init__(self, token: str, code: str, language: str, example: str = ""):
        self.__token = token
        if not isinstance(self.__token, str):
            exit(f"[{RED}Error{RESET}] Token is must be a string")
        elif len(self.__token) == 0:
            exit(f"[{RED}Error{RESET}] Token is empty")

        self.__code = code
        if not isinstance(self.__code, str):
            exit(f"[{RED}Error{RESET}] Code is must be a string")
        elif len(self.__code) == 0:
            exit(f"[{RED}Error{RESET}] Code is empty")

        self.__language = language
        if not self.__language in Settings.supported_languages:
            exit(f"[{RED}Error{RESET}] .{self.__language} language not supported")

        self.__example = example
        if not isinstance(self.__example, str):
            exit(f"[{RED}Error{RESET}] Example is must be a string")
        elif len(self.__example) > 0:
            self.__language = "example"

    def __ask(self, code) -> str:
        response = None
        conversation = None
        try:
            for data in self.__chatbot.ask(
                Prompt(self.__language, code).create(),
                conversation_id=self.__conversation,
                parent_id=None,
            ):
                response = data["message"]
                conversation = data["conversation_id"]
            if not self.__conversation:
                self.__conversation = conversation
            return response
        except:
            raise ValueError("ChatGPT error")

    def start(self):
        with console.status("[bold green] Please wait...") as status:
            print(f"[{BLUE}1{RESET}] {BOLD}Dividing text{RESET}")
            self.__divided = Divider(self.__code, self.__language).divide()

            if len(self.__divided) == 0:
                print(
                    f"[{RED}END{RESET}] {BOLD}There is nothing to comment in the code{RESET}"
                )
                exit(0)

            print(
                f"[{BLUE}2{RESET}] {BOLD}Text is divided into {len(self.__divided)} parts{RESET}"
            )

            print(f"[{BLUE}3{RESET}] {BOLD}Connecting to ChatGPT{RESET}")
            self.__chatbot = Chatbot({"session_token": self.__token})
            self.__conversation = None

            self.__count = 1
            self.__comments = []
            for entity in self.__divided:
                print(
                    f"[{BLUE}4.{self.__count}{RESET}] {BOLD}Chatbot generating comments ({self.__count}/{len(self.__divided)}){RESET}"
                )
                response = self.__ask(entity)
                self.__comments.append(response)
                sleep(1)
                self.__count += 1

            print(f"[{BLUE}5{RESET}] {BOLD}Merge file and comments{RESET}")
            self.__commented_code = self.__code
            for comment in self.__comments:
                self.__commented_code = Result(
                    self.__commented_code, comment, self.__language
                ).get()

            print(f"[{BLUE}6{RESET}] {BOLD}Ready. Thanks for using!{RESET}"),
            return self.__commented_code