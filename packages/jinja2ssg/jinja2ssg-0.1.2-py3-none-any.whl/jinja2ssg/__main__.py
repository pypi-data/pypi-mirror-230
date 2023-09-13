import click

from . import builder


@click.group()
@click.option("--src", default="src", help="Where are the templates")
@click.option("--dest", default="public", help="Where should the output be placed")
@click.option(
    "-e",
    "--ext",
    default=[".html", ".txt"],
    help="What file extensions should we use. All others will be ignored.",
)
@click.pass_context
def cli(ctx, src, dest, ext):
    ctx.ensure_object(dict)
    ctx.obj["src"] = src
    ctx.obj["dest"] = dest
    ctx.obj["ext"] = dest


@cli.command()
@click.pass_context
def build(ctx):
    """
    Build the site.
    """
    builder.build(src=ctx.obj["src"], dest=ctx.obj["dest"], ext=ctx.obj["ext"])


if __name__ == "__main__":
    cli(obj={})
