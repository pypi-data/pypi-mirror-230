import asyncio
import os
import subprocess
import sys

import openai
import questionary
import rich
from rich.markdown import Markdown

from shell_whiz.argparse import create_argument_parser
from shell_whiz.config import sw_config, sw_edit_config
from shell_whiz.console import console
from shell_whiz.constants import (
    INV_CLI_ARGS_EXIT_CODE,
    OPENAI_ERROR_EXIT_CODE,
    SW_ERROR,
    SW_ERROR_EXIT_CODE,
    SW_WAIT_MSG,
)
from shell_whiz.exceptions import (
    ShellWhizEditError,
    ShellWhizTranslationError,
    ShellWhizWarningError,
)
from shell_whiz.openai import (
    edit_shell_command,
    get_explanation_of_shell_command,
    recognize_dangerous_command,
    translate_nl_to_shell_command,
)


def print_explanation(explanation):
    rich.print(
        " ================== [bold green]Explanation[/] =================="
    )
    console.print(Markdown(explanation))
    print()


def print_command(shell_command):
    rich.print(
        "\n ==================== [bold green]Command[/] ====================\n"
    )

    for line in shell_command.splitlines():
        print(f" {line}")

    print()


async def shell_whiz_ask(prompt):
    first_run = True
    edit_prompt = ""

    try:
        with console.status(SW_WAIT_MSG, spinner="dots"):
            shell_command = translate_nl_to_shell_command(prompt)
    except ShellWhizTranslationError:
        rich.print(f"{SW_ERROR}: Shell Whiz doesn't know how to do this.")
        sys.exit(SW_ERROR_EXIT_CODE)

    while True:
        if first_run:
            first_run = False
        elif edit_prompt != "":
            try:
                shell_command = await edit_shell_command(
                    shell_command, edit_prompt
                )
            except ShellWhizEditError:
                pass

        print_command(shell_command)

        explanation_task = asyncio.create_task(
            get_explanation_of_shell_command(shell_command)
        )

        with console.status(SW_WAIT_MSG, spinner="dots"):
            try:
                (
                    is_dangerous,
                    dangerous_consequences,
                ) = recognize_dangerous_command(shell_command)
                if not is_dangerous:
                    explanation = await explanation_task
            except ShellWhizWarningError:
                is_dangerous = False
                explanation = await explanation_task

        if is_dangerous:
            rich.print(
                " [bold red]Warning[/]: [bold yellow]{0}[/]\n".format(
                    dangerous_consequences
                )
            )

            with console.status(SW_WAIT_MSG, spinner="dots"):
                explanation = await explanation_task

        print_explanation(explanation)

        edit_prompt = ""

        choice = await questionary.select(
            "Select an action",
            choices=[
                "Run this command",
                "Revise query",
                "Edit manually",
                "Exit",
            ],
        ).unsafe_ask_async()
        if choice == "Exit":
            sys.exit()
        elif choice == "Revise query":
            edit_prompt = await questionary.text(
                message="Revise query"
            ).unsafe_ask_async()
        elif choice == "Edit manually":
            shell_command = await questionary.text(
                "Edit command", default=shell_command, multiline=True
            ).unsafe_ask_async()
        elif choice == "Run this command":
            subprocess.run(shell_command, shell=True)
            return


async def run_ai_assistant(args):
    await sw_config()

    os.environ["SW_MODEL"] = args.model

    shell_command = " ".join(args.prompt).strip()
    if shell_command == "":
        rich.print(f"{SW_ERROR}: Please provide a valid prompt.")
        sys.exit(INV_CLI_ARGS_EXIT_CODE)

    await shell_whiz_ask(shell_command)


async def main():
    args = create_argument_parser().parse_args()

    if args.sw_command == "config":
        await sw_edit_config()
    elif args.sw_command == "ask":
        await run_ai_assistant(args)


def run():
    try:
        asyncio.run(main())
    except openai.error.APIError:
        rich.print(
            f"{SW_ERROR}: An error occurred while connecting to the OpenAI API. Please retry your request after a brief wait. The problem is on the side of the OpenAI. Visit https://status.openai.com for more information."
        )
        sys.exit(OPENAI_ERROR_EXIT_CODE)
    except openai.error.Timeout:
        rich.print(
            f"{SW_ERROR}: OpenAI API request timed out. Please retry your request after a brief wait."
        )
        sys.exit(OPENAI_ERROR_EXIT_CODE)
    except openai.error.APIConnectionError:
        rich.print(
            f"{SW_ERROR}: OpenAI API request failed to connect. Please check your internet connection and try again."
        )
        sys.exit(OPENAI_ERROR_EXIT_CODE)
    except openai.error.InvalidRequestError as e:
        rich.print(
            f"{SW_ERROR}: Your request was malformed or missing some required parameters, such as a token or an input. {e}"
        )
        sys.exit(OPENAI_ERROR_EXIT_CODE)
    except openai.error.AuthenticationError:
        rich.print(
            f"{SW_ERROR}: You are not authorized to access the OpenAI API. You may have entered the wrong API key. Your API key is invalid, expired or revoked. Please run [bold green]sw config[/] to set up the API key. Visit https://platform.openai.com/account/api-keys to get your API key."
        )
        sys.exit(OPENAI_ERROR_EXIT_CODE)
    except openai.error.PermissionError:
        rich.print(
            f"{SW_ERROR}: Your API key or token does not have the required scope or role to perform the requested action. Make sure your API key has the appropriate permissions for the action or model accessed."
        )
        sys.exit(OPENAI_ERROR_EXIT_CODE)
    except openai.error.RateLimitError:
        rich.print(
            f"{SW_ERROR}: OpenAI API request exceeded rate limit. If you are on a free plan, please upgrade to a paid plan for a better experience with Shell Whiz. Visit https://platform.openai.com/account/billing/limits for more information."
        )
        sys.exit(OPENAI_ERROR_EXIT_CODE)
    except openai.error.ServiceUnavailableError:
        rich.print(
            f"{SW_ERROR}: OpenAI API request failed due to a temporary server-side issue. Please retry your request after a brief wait. The problem is on the side of the OpenAI. Visit https://status.openai.com for more information."
        )
        sys.exit(OPENAI_ERROR_EXIT_CODE)
    except openai.error.OpenAIError:
        rich.print(
            f"{SW_ERROR}: An unknown error occurred while connecting to the OpenAI API. Please retry your request after a brief wait."
        )
        sys.exit(OPENAI_ERROR_EXIT_CODE)
    except KeyboardInterrupt:
        print("\nExiting...")
        sys.exit(0)
