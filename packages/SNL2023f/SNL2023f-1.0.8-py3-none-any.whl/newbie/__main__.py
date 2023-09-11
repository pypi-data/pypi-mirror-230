import click
import newbie

__version__ = "1.0.8"

@click.version_option(prog_name="SNL2023f", version=__version__)
@click.group()
def main():
    pass

@main.command("server")
def server():
    newbie.commands.server()

@main.command("container")
def container():
    newbie.commands.container()

@main.command("client")
def client():
    newbie.commands.client()

if __name__ == "__main__":
    main()
