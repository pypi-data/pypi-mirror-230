import click
import sys
from loguru import logger

from workflow_keeper.server import run
from workflow_keeper.config import (
    get_cli_parser,
    get_default_config,
    load_config,
    save_config,
    Config
)


@click.group()
@click.pass_context
def cli(ctx):
    pass


@cli.command(context_settings=dict(ignore_unknown_options=True, allow_extra_args=True))
@click.pass_context
def init(ctx):
    import sys
    argv = sys.argv[2:]
    logger.info("init with args: {}", argv)
    args = get_cli_parser().parse_args(argv)
    v = get_default_config()
    if args.config is not None:
        v.set_config_file(args.config)
        try:
            v.read_in_config()
        except Exception as e:
            logger.debug(e)
    v.bind_args(vars(args))

    err = save_config(v, path=args.config)
    if err is not None:
        logger.error(err)


@cli.command(context_settings=dict(ignore_unknown_options=True, allow_extra_args=True))
@click.pass_context
def serve(ctx):
    v, err = load_config(argv=sys.argv[2:])
    opt = Config().from_vyper(v)
    run(opt)


if __name__ == '__main__':
    cli()
