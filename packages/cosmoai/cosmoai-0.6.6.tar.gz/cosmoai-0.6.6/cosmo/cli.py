"""
Right off the bat, to any contributors (a message from Killian):

First of all, THANK YOU. Open Cosmo is ALIVE, ALL OVER THE WORLD because of YOU.

While this project is rapidly growing, I've decided it's best for us to allow some technical debt.

The code here has duplication. It has imports in weird places. It has been spaghettified to add features more quickly.

In my opinion **this is critical** to keep up with the pace of demand for this project.

At the same time, I plan on pushing a significant re-factor of `cosmo.py` and `code_cosmo.py` ~ September 16th.

After the re-factor, Open Cosmo's source code will be much simpler, and much more fun to dive into.

Especially if you have ideas and **EXCITEMENT** about the future of this project, chat with me on discord: https://discord.gg/6p3fD6rBVm

- killian
"""

import argparse
import os
from dotenv import load_dotenv
import requests
from packaging import version
import pkg_resources
from rich import print as rprint
from rich.markdown import Markdown
import inquirer

# Load .env file
load_dotenv()

def check_for_update():
    # Fetch the latest version from the PyPI API
    response = requests.get(f'https://pypi.org/pypi/open-cosmo/json')
    latest_version = response.json()['info']['version']

    # Get the current version using pkg_resources
    current_version = pkg_resources.get_distribution("open-cosmo").version

    return version.parse(latest_version) > version.parse(current_version)

def cli(cosmo):
  """
  Takes an instance of cosmo.
  Modifies it according to command line flags, then runs chat.
  """

  try:
    if check_for_update():
      print("A new version is available. Please run 'pip install --upgrade open-cosmo'.")
  except:
    # Fine if this fails
    pass

  # Load values from .env file with the new names
  AUTO_RUN = os.getenv('COSMO_CLI_AUTO_RUN', 'False') == 'True'
  FAST_MODE = os.getenv('COSMO_CLI_FAST_MODE', 'False') == 'True'
  LOCAL_RUN = os.getenv('COSMO_CLI_LOCAL_RUN', 'False') == 'True'
  DEBUG = os.getenv('COSMO_CLI_DEBUG', 'False') == 'True'
  USE_AZURE = os.getenv('COSMO_CLI_USE_AZURE', 'False') == 'True'

  # Setup CLI
  parser = argparse.ArgumentParser(description='Chat with Open Cosmo.')
  
  parser.add_argument('-y',
                      '--yes',
                      action='store_true',
                      default=AUTO_RUN,
                      help='execute code without user confirmation')
  parser.add_argument('-f',
                      '--fast',
                      action='store_true',
                      default=FAST_MODE,
                      help='use gpt-3.5-turbo instead of gpt-4')
  parser.add_argument('-l',
                      '--local',
                      action='store_true',
                      default=LOCAL_RUN,
                      help='run fully local with code-llama')
  parser.add_argument(
                      '--falcon',
                      action='store_true',
                      default=False,
                      help='run fully local with falcon-40b')
  parser.add_argument('-d',
                      '--debug',
                      action='store_true',
                      default=DEBUG,
                      help='prints extra information')
  
  parser.add_argument('--model',
                      type=str,
                      help='model name (for OpenAI compatible APIs) or HuggingFace repo',
                      default="",
                      required=False)
  
  parser.add_argument('--max_tokens',
                      type=int,
                      help='max tokens generated (for locally run models)')
  parser.add_argument('--context_window',
                      type=int,
                      help='context window in tokens (for locally run models)')
  
  parser.add_argument('--api_base',
                      type=str,
                      help='change your api_base to any OpenAI compatible api',
                      default="",
                      required=False)
  
  parser.add_argument('--use-azure',
                      action='store_true',
                      default=USE_AZURE,
                      help='use Azure OpenAI Services')
  
  parser.add_argument('--version',
                      action='store_true',
                      help='display current Open Cosmo version')

  args = parser.parse_args()


  if args.version:
    print("Open Cosmo", pkg_resources.get_distribution("open-cosmo").version)
    return

  if args.max_tokens:
    cosmo.max_tokens = args.max_tokens
  if args.context_window:
    cosmo.context_window = args.context_window

  # Modify cosmo according to command line flags
  if args.yes:
    cosmo.auto_run = True
  if args.fast:
    cosmo.model = "gpt-3.5-turbo"
  if args.local and not args.falcon:



    # Temporarily, for backwards (behavioral) compatability, we've moved this part of llama_2.py here.
    # This way, when folks hit cosmo --local, they get the same experience as before.
    
    rprint('', Markdown("**Open Cosmo** will use `Code Llama` for local execution. Use your arrow keys to set up the model."), '')
        
    models = {
        '7B': 'TheBloke/CodeLlama-7B-Instruct-GGUF',
        '13B': 'TheBloke/CodeLlama-13B-Instruct-GGUF',
        '34B': 'TheBloke/CodeLlama-34B-Instruct-GGUF'
    }
    
    parameter_choices = list(models.keys())
    questions = [inquirer.List('param', message="Parameter count (smaller is faster, larger is more capable)", choices=parameter_choices)]
    answers = inquirer.prompt(questions)
    chosen_param = answers['param']

    # THIS is more in line with the future. You just say the model you want by name:
    cosmo.model = models[chosen_param]
    cosmo.local = True

  
  if args.debug:
    cosmo.debug_mode = True
  if args.use_azure:
    cosmo.use_azure = True
    cosmo.local = False


  if args.model != "":
    cosmo.model = args.model

    # "/" in there means it's a HF repo we're going to run locally:
    if "/" in cosmo.model:
      cosmo.local = True

  if args.api_base:
    cosmo.api_base = args.api_base

  if args.falcon or args.model == "tiiuae/falcon-180B": # because i tweeted <-this by accident lol, we actually need TheBloke's quantized version of Falcon:

    # Temporarily, for backwards (behavioral) compatability, we've moved this part of llama_2.py here.
    # This way, when folks hit cosmo --falcon, they get the same experience as --local.
    
    rprint('', Markdown("**Open Cosmo** will use `Falcon` for local execution. Use your arrow keys to set up the model."), '')
        
    models = {
        '7B': 'TheBloke/CodeLlama-7B-Instruct-GGUF',
        '40B': 'YokaiKoibito/falcon-40b-GGUF',
        '180B': 'TheBloke/Falcon-180B-Chat-GGUF'
    }
    
    parameter_choices = list(models.keys())
    questions = [inquirer.List('param', message="Parameter count (smaller is faster, larger is more capable)", choices=parameter_choices)]
    answers = inquirer.prompt(questions)
    chosen_param = answers['param']

    if chosen_param == "180B":
      rprint(Markdown("> **WARNING:** To run `Falcon-180B` we recommend at least `100GB` of RAM."))

    # THIS is more in line with the future. You just say the model you want by name:
    cosmo.model = models[chosen_param]
    cosmo.local = True


  # Run the chat method
  cosmo.chat()
