import click


from .signers.msgsigner import msg_clear_sign_main, msg_container_sign_main


@click.group()
def cli():
    """Pubtools-sign multi command bundle."""
    pass


cli.add_command(msg_clear_sign_main, name="msg-clear-sign")
cli.add_command(msg_container_sign_main, name="msg-container-sign")
