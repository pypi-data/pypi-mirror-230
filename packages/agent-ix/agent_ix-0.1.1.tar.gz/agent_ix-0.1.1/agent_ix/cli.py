import argparse
import os
import subprocess
import pkg_resources


DOCKER_COMPOSE_PATH = pkg_resources.resource_filename(
    "agent_ix", "docker-compose.yml"
)
IX_ENV_TEMPLATE = pkg_resources.resource_filename("agent_ix", "ix.env")
CWD = os.getcwd()
IX_ENV_PATH = os.path.join(CWD, "ix.env")


def init_env():
    # create ix.env file if it doesn't exist
    if not os.path.exists(IX_ENV_PATH):
        with open(IX_ENV_TEMPLATE, "r") as f:
            with open(IX_ENV_PATH, "w") as f2:
                f2.write(f.read())


def get_env():
    init_env()
    nginx_conf = pkg_resources.resource_filename("agent_ix", "nginx.conf")

    return {
        "NGINX_CONF": nginx_conf,
        "IX_IMAGE_TAG": "latest",
        "IX_ENV": IX_ENV_PATH,
        **os.environ,
    }


def run_docker_compose_command(subcommand, *args, **kwargs):
    env = get_env()
    cmd = ["docker-compose", "-f", DOCKER_COMPOSE_PATH, subcommand] + list(
        args
    )
    subprocess.run(cmd, env=env)


def run_manage_py_command(subcommand, *args):
    env = get_env()
    cmd = [
        "docker-compose",
        "-f",
        DOCKER_COMPOSE_PATH,
        "exec",
        "app",
        "./manage.py",
        subcommand,
    ] + list(args)
    subprocess.run(cmd, env=env)


def up(args):
    # destroy static on each startup so that it is always pulled fresh from the
    # container this avoids stale files from a version prior to what is running.
    subprocess.run(["docker", "volume", "rm", "agent_ix_static"])
    run_docker_compose_command(
        "up",
        "-d",
    )


def down(args):
    run_docker_compose_command("down")


def scale(args):
    num = args.num
    run_docker_compose_command("up", "-d", "--scale", f"worker={num}")


def log(args):
    services = args.services
    run_docker_compose_command("logs", "--tail=50", "--follow", *services)


def migrate(args):
    run_manage_py_command("migrate")


def setup(args):
    migrate()
    # run_manage_py_command('setup')
    run_manage_py_command("loaddata", "fake_user")
    run_manage_py_command("loaddata", "node_types")
    run_manage_py_command(
        "loaddata",
        "ix_v2 code_v2 pirate_v1 wikipedia_v1 klarna_v1 bot_smith_v1",
    )


def version(args):
    version = pkg_resources.resource_filename("agent_ix", "VERSION")
    with open(version, "r") as f:
        print(f"IX client v{f.read()}")


def main():
    parser = argparse.ArgumentParser(
        description="Docker-compose and Django CLI wrapper."
    )
    subparsers = parser.add_subparsers(
        title="Subcommands",
        description="Valid subcommands",
        help="Available operations",
    )

    # 'up' subcommand
    parser_version = subparsers.add_parser(
        "version", help="report client version"
    )
    parser_version.set_defaults(func=version)

    # 'up' subcommand
    parser_up = subparsers.add_parser(
        "up", help="Start services in the background"
    )
    # parser_up.add_argument('version', help='Version to load (e.g. 0.1)',
    # default="latest")
    parser_up.set_defaults(func=up)

    # 'down' subcommand
    parser_down = subparsers.add_parser(
        "down",
        help="Stop and remove containers, networks, images, and volumes",
    )
    parser_down.set_defaults(func=down)

    # 'scale' subcommand
    parser_scale = subparsers.add_parser("scale", help="Scale agent workers")
    parser_scale.add_argument(
        "num", type=int, help="Number of agent workers to scale to"
    )
    parser_scale.set_defaults(func=scale)

    # 'log' subcommand
    parser_log = subparsers.add_parser(
        "log",
        help="View output from containers [worker, web, nginx, db, redis]",
    )
    parser_log.add_argument(
        "services", nargs="+", help="Names of the services to show logs for"
    )
    parser_log.set_defaults(func=log)

    # 'migrate' subcommand
    parser_migrate = subparsers.add_parser(
        "migrate", help="Run Django database migrations"
    )
    parser_migrate.set_defaults(func=migrate)

    # 'setup' subcommand
    parser_setup = subparsers.add_parser(
        "setup", help="Initialize database and load fixtures"
    )
    parser_setup.set_defaults(func=setup)

    args = parser.parse_args()

    if "func" in args:
        args.func(args)
    else:
        parser.print_help()
