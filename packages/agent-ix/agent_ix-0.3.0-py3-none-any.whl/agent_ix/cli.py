import argparse
import os
import subprocess
from getpass import getpass

import pkg_resources

from agent_ix.ix_env import IX_ENV

IMAGE = "ghcr.io/kreneskyp/ix/sandbox"
DOCKER_COMPOSE_PATH = pkg_resources.resource_filename("agent_ix", "docker-compose.yml")
IX_ENV_TEMPLATE = pkg_resources.resource_filename("agent_ix", "ix.env")
CWD = os.getcwd()
IX_ENV_PATH = os.path.join(CWD, "ix.env")
IX_INIT = os.path.join(CWD, ".ix")


# ==============================
#  Setup and environment
# ==============================


def initial_env():
    # create ix.env file if it doesn't exist
    if os.path.exists(IX_ENV_PATH):
        return

    # Initialize to an empty string
    open_api_key = ""

    # Loop until a non-empty API key is entered
    while not open_api_key:
        open_api_key = getpass("Please enter your OpenAI API key (hidden): ")
        if not open_api_key:
            print("API key is required.")

    with open(IX_ENV_PATH, "w") as f:
        f.write(IX_ENV.format(OPENAI_API_KEY=open_api_key))


def initial_setup(args):
    """Sets up the IX database on the first run

    While this is safe to run on every startup, it's not necessary and will
    auto-trigger migrations or re-run fixtures. The main concern is that fixtures
    will override any changes made to the database.
    """
    if os.path.exists(IX_INIT):
        return

    setup(args)


def migrate(args):
    print("Running IX database migrations")
    run_manage_py_command("migrate")


def setup(args):
    """create database and load fixtures"""
    migrate(args)
    run_manage_py_command("setup")


def get_env(env=None):
    nginx_conf = pkg_resources.resource_filename("agent_ix", "nginx.conf")

    return {
        "NGINX_CONF": nginx_conf,
        "IX_IMAGE_TAG": "latest",
        "IX_ENV": IX_ENV_PATH,
        **os.environ,
        **(env or {}),
    }


# ==============================
#  Compose helpers
# ==============================


def run_docker_compose_command(subcommand, *args, **kwargs):
    runtime_env = kwargs.get("env", {})
    env = get_env(env=runtime_env)
    cmd = ["docker-compose", "-f", DOCKER_COMPOSE_PATH, subcommand] + list(args)
    subprocess.run(cmd, env=env)


def run_manage_py_command(subcommand, *args):
    env = get_env()
    cmd = [
        "docker-compose",
        "-f",
        DOCKER_COMPOSE_PATH,
        "exec",
        "web",
        "./manage.py",
        subcommand,
    ] + list(args)
    subprocess.run(cmd, env=env)


# ==============================
#  Server management
# ==============================


def up(args):
    env = {"IX_IMAGE_TAG": "latest"}
    if args.version:
        env["IX_IMAGE_TAG"] = args.version

    print("Starting IX Sandbox")
    print(f"image: {IMAGE}:{env['IX_IMAGE_TAG']}")
    print(f"env: {IX_ENV_PATH}")
    print("------------------------------------------------")

    # destroy static on each startup so that it is always pulled fresh from the
    # container this avoids stale files from a version prior to what is running.
    subprocess.run(["docker", "volume", "rm", "agent_ix_static"])

    # manually pull the image to ensure we have the latest version
    subprocess.run(["docker", "pull", f"{IMAGE}:{env['IX_IMAGE_TAG']}"])

    # startup the containers
    run_docker_compose_command("up", "-d", env=env)

    # run initial setup - requires app and database are running
    initial_setup(args)

    # app is ready!
    print_welcome_message(version=env["IX_IMAGE_TAG"])


def print_welcome_message(version):
    print("================================================")
    print(f"IX Sandbox ({version}) is running on http://localhost:8000")
    print()
    print("Edit ix.env to set global keys for LLMs and other services.")
    print()
    print("---- Management Commands ----")
    print("stop       : ix down")
    print("restart    : ix restart")
    print("scale      : ix scale 3")
    print("web log    : ix log web nginx")
    print("worker log : ix log worker")


def down(args):
    print("Stopping IX Sandbox")
    run_docker_compose_command("down")


def restart(args):
    down(args)
    up(args)


def scale(args):
    num = args.num
    print(f"Scaling IX agent workers to {num}")
    run_docker_compose_command("up", "-d", "--scale", f"worker={num}")


def log(args):
    services = args.services
    run_docker_compose_command("logs", "--tail=50", "--follow", *services)


# ==============================
#  Main
# ==============================


def version(args):
    version = pkg_resources.resource_filename("agent_ix", "VERSION")
    with open(version, "r") as f:
        print(f"IX client v{f.read()}")


DESCRIPTION = """Agent IX control.

This command line tool is used to manage a local Agent IX cluster. The application
including frontend, backend, database, and related services are all run in Docker
containers. This tool is used to start, stop, and scale the containers.

The ix.env file is used to configure default global keys for OpenAI and other
services. This file is created on first run and can be edited to set your keys.

This tool will pull and run the IX docker images. By default the `latest` tag will
be run. To run a specific version of IX, use the --version flag.

    ix up --version 0.8
    ix up --version dev
    ix up --version latest
"""


def main():
    initial_env()

    parser = argparse.ArgumentParser(
        description=DESCRIPTION, formatter_class=argparse.RawTextHelpFormatter
    )
    subparsers = parser.add_subparsers(
        title="Subcommands",
        description="Valid subcommands",
        help="Available operations",
    )

    # 'up' subcommand
    parser_version = subparsers.add_parser("version", help="report client version")
    parser_version.set_defaults(func=version)

    # 'up' subcommand
    parser_up = subparsers.add_parser("up", help="Start services in the background")
    parser_up.add_argument(
        "--version", type=str, default=None, help="IX sandbox image tag run (e.g. 0.1.1)"
    )
    parser_up.set_defaults(func=up)

    # 'down' subcommand
    parser_down = subparsers.add_parser(
        "down",
        help="Stop and remove containers, networks, images, and volumes",
    )
    parser_down.set_defaults(func=down)

    # 'restart' subcommand
    parser_restart = subparsers.add_parser("restart", help="Restart all services")
    parser_restart.set_defaults(func=restart)

    # 'scale' subcommand
    parser_scale = subparsers.add_parser("scale", help="Scale agent workers")
    parser_scale.add_argument("num", type=int, help="Number of agent workers to scale to")
    parser_scale.set_defaults(func=scale)

    # 'log' subcommand
    parser_log = subparsers.add_parser(
        "log",
        help="View output from containers [worker, web, nginx, db, redis]",
    )
    parser_log.add_argument("services", nargs="+", help="Names of the services to show logs for")
    parser_log.set_defaults(func=log)

    # 'migrate' subcommand
    parser_migrate = subparsers.add_parser("migrate", help="Run Django database migrations")
    parser_migrate.set_defaults(func=migrate)

    # 'setup' subcommand
    parser_setup = subparsers.add_parser("setup", help="Initialize database and load fixtures")
    parser_setup.set_defaults(func=setup)

    args = parser.parse_args()

    if "func" in args:
        args.func(args)
    else:
        parser.print_help()
