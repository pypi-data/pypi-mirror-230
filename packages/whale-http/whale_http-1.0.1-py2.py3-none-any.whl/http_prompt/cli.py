import os
import sys
from http.cookies import SimpleCookie

import click
from httpie.output.formatters.colors import Solarized256Style
from prompt_toolkit import prompt
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.completion import merge_completers
from prompt_toolkit.formatted_text import to_formatted_text
from prompt_toolkit.history import FileHistory
from prompt_toolkit.lexers import PygmentsLexer
from prompt_toolkit.styles.pygments import style_from_pygments_cls
from pygments.styles import get_style_by_name
from pygments.util import ClassNotFound

from . import __version__, config
from .completer import HttpPromptCompleter
from .context import Context
from .execution import execute
from .lexer import HttpPromptLexer
from .projectcollect import ProjectCollect
from .projectcompleter import ProjectCollectCompleter
from .projectconfig import get_project_conf


def update_cookies(base_value, cookies):
    cookie = SimpleCookie(base_value)
    for k, v in cookies.items():
        cookie[k] = v
    return str(cookie.output(header="", sep=";").lstrip())


class ExecutionListener(object):
    def __init__(self, cfg):
        self.cfg = cfg

    def context_changed(self, context):
        pass

    def response_returned(self, context, response):
        if not response.cookies:
            return

        cookie_pref = self.cfg.get("set_cookies") or "auto"
        if (cookie_pref == "auto") or (
            cookie_pref == "ask"
            and click.confirm("Cookies incoming! Do you want to set them?")
        ):
            existing_cookie = context.headers.get("Cookie")
            new_cookie = update_cookies(existing_cookie, dict(response.cookies))
            context.headers["Cookie"] = new_cookie
            click.secho(message=f"Cookies set: {new_cookie}")


def run(project_name: str = ""):
    copied, config_path = config.initialize()
    if copied:
        click.echo(f"Config file not found. Initialized a new one: {config_path}")

    cfg = config.load()

    # httpie使用了 less 命令，windows没有此命令
    if sys.platform != "win32":
        os.environ["PAGER"] = cfg["pager"]
        os.environ["LESS"] = "-RXF"

    context = Context()

    prjColl = ProjectCollect.load_from_file(config.get__projectcollect_file())

    if output_style := cfg.get("output_style"):
        context.options["--style"] = output_style

    lexer = PygmentsLexer(HttpPromptLexer)

    def make_history_and_completer(project_path):
        history = FileHistory(os.path.join(project_path, "history"))
        completer = merge_completers(
            [
                HttpPromptCompleter(context),
                ProjectCollectCompleter(prjColl.project_names, prjColl.project_dict),
            ]
        )
        return history, completer

    def loadcontext_from_projectpath(context, project_path):
        context.update(Context())
        prjconfig = get_project_conf(project_path)
        context.url = prjconfig.host

    if not project_name and len(prjColl.project_names) > 0:
        project_name = prjColl.project_names[0]
    prjloc = prjColl.get_path(project_name)
    if not prjloc:
        click.echo(f"{project_name} not exists, please create first")
        return
    history, completer = make_history_and_completer(prjloc)
    loadcontext_from_projectpath(context, prjloc)

    try:
        style_class = get_style_by_name(cfg["command_style"])
    except ClassNotFound:
        style_class = Solarized256Style
    style = style_from_pygments_cls(style_class)

    listener = ExecutionListener(cfg)

    while True:
        try:
            text = prompt(
                to_formatted_text(f"{context.url} > ", style="fg:#00ff00 italic"),
                completer=completer,
                lexer=lexer,
                style=style,
                # style_transformation=True,
                history=history,
                # complete_while_typing=False,
                auto_suggest=AutoSuggestFromHistory(),
                #   enable_history_search=True,
                vi_mode=cfg["vi"],
            )

        except KeyboardInterrupt:
            continue  # Control-C pressed
        except EOFError:
            break  # Control-D pressed
        else:
            execute(text, context, listener=listener, style=style_class)
            if context.should_reload:
                prjloc = prjColl.get_path(context.project_name)
                history, completer = make_history_and_completer(prjloc)
                loadcontext_from_projectpath(context, prjloc)
                context.should_reload = False
            if context.should_exit:
                break

    click.echo("Goodbye!")


@click.group(
    invoke_without_command=True,
    context_settings={"ignore_unknown_options": True},
    help="do http requests in project by option(-p|--project)",
)
@click.option("-p", "--project", default="", help="project name")
@click.version_option(message="%(version)s")
@click.pass_context
def cli(ctx, project):
    click.secho(message=f"Version: {__version__}", fg="red")
    if ctx.invoked_subcommand is None:
        run(project)


@cli.command(
    "new", help="create a new project by options(-n|--name, -u|--url, -p|--path)"
)
@click.option("-n", "--name", default="", help="project name")
@click.option("-u", "--url", default="", help="root url of project")
@click.option("-p", "--path", default="", help="local path of project files")
def newproject(name, path, url):
    config.newproject(name, path, url)
    run(name)


@cli.command("delete", help="delete a project by option (-n|--name)")
@click.confirmation_option(prompt="Do you want to delete this project ?")
@click.option("-n", "--name", help="given project name to be deleted")
def deleteproject(name):
    prjColl = ProjectCollect.load_from_file(config.get__projectcollect_file())
    prjColl.delete_project(name)
    click.echo(f"{name} deleted")
