import click

@click.command()
@click.option("--count", default=1)
@click.option("--text")
def f(count, text):
    """Программа повторяет введенный текст от одного до count раз"""
    try:
        for i in range(count):
            click.echo(text * (i+1))
    except:
        print("Не введен обязательный параметр.")
f()