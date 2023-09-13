import click

from . import builder


@click.group()
@click.option("--src", default="src", help="Where are the templates")
@click.option("--dest", default="public", help="Where should the output be placed")
@click.pass_context
def cli(ctx, src, dest):
    ctx.ensure_object(dict)
    ctx.obj["src"] = src
    ctx.obj["dest"] = dest


@cli.command()
@click.pass_context
def build(ctx):
    """
    Build the site.
    """
    builder.build(src=ctx.obj["src"], dest=ctx.obj["dest"])


if __name__ == "__main__":
    cli(obj={})
