import os
from dotenv import load_dotenv
import click
import socketio
import os.path as osp
from yaspin import yaspin
from yaspin.spinners import Spinners

from genesia.templates_manager import create_project_from_template, available_templates

load_dotenv()
ENVIRONMENT = os.getenv("ENVIRONMENT", "production")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if ENVIRONMENT == "development":
    print("You are using the CLI in development mode. See your .env file.")


class DynamicText:
    def __init__(self, init_value):
        self.value = init_value

    def update(self, new_value):
        self.value = new_value

    def __str__(self):
        return self.value


@click.group()
def cli():
    pass


def validate_openai_key(ctx, param, value):
    if value.startswith("sk"):
        return value
    else:
        raise click.BadParameter("openai-api-key should start with 'sk'")


@cli.command("create")
@click.option("--name", help="Name of the project", required=True)
@click.option(
    "--template",
    type=click.Choice(available_templates),
    help="Template to use (see more https://github.com/ThomasCloarec/genesia-templates)",
    required=True,
)
@click.option(
    "--prompt",
    prompt="Describe what you want to do",
    help="Describe what you want to do",
    required=True,
)
# @click.option(
#     "--openai-api-key",
#     default=OPENAI_API_KEY,
#     prompt="OpenAI API key",
#     help="OpenAI API key",
#     required=True,
#     callback=validate_openai_key,
# )
# def create_project(name, template, prompt, openai_api_key):
def create_project(name, template, prompt):
    assert not osp.exists(name), f"Project {name} already exists"

    text = DynamicText("Connecting to our AI (it may take a few minutes)...")

    with yaspin(Spinners.pong, text=text, color="yellow") as spinner:
        sio = socketio.Client()

        def on_create_project_response(data):
            if data["status"] == "error":
                print(data["message"])
            elif data["status"] == "success":
                assert "result" in data, "[Internal Error] No result in response"
                result = data["result"]
                create_project_from_template(template, name, result)
                print("Project {} created".format(name))
            sio.disconnect()

        @sio.on("connect")
        def on_connect():
            text.update("Generating your project...")
            sio.emit(
                "create_project",
                {
                    "name": name,
                    "template": template,
                    "prompt": prompt,
                    # "api_key": openai_api_key,
                },
                callback=on_create_project_response,
            )

        @sio.on("create_project")
        def on_create_project(msg):
            spinner.write(text)
            text.update(msg)

        @sio.on("disconnect")
        def on_disconnect():
            sio.disconnect()

        if ENVIRONMENT == "development":
            sio.connect("http://127.0.0.1:8000/", wait=False)
        else:
            sio.connect("https://genesia-api.onrender.com/", wait=False)

        try:
            sio.wait()
        except KeyboardInterrupt:
            pass
        finally:
            sio.disconnect()


def run_cli():
    try:
        cli()
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    run_cli()
