import click


@click.group()
def cli():
    pass


def closed_alpha_message():
    click.echo(
        "Multinode is currently in closed alpha. "
        "You can join the waitlist at https://multinode.io"
    )


@cli.command()
def login():
    closed_alpha_message()


@cli.command()
def run():
    closed_alpha_message()


@cli.command()
def deploy():
    closed_alpha_message()


@cli.command()
def undeploy():
    closed_alpha_message()


@cli.command()
def describe():
    closed_alpha_message()


@cli.command()
def logs():
    closed_alpha_message()


if __name__ == "__main__":
    cli()