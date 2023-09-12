from prompt_toolkit import PromptSession
from prompt_toolkit import print_formatted_text
session = PromptSession()
input = session.prompt
print = print_formatted_text

import newbie.commands
import newbie.docker
