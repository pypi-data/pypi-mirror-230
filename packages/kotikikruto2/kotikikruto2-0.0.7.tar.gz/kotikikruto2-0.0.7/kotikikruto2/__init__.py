import click

@click.command()
@click.option("--count", default=1)
@click.option("--text")
def f(count, text):
    """Программа"""
    for i in range(count):
        click.echo(i * text)
f()