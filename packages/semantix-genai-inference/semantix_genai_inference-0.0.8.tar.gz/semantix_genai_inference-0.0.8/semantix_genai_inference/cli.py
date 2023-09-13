import click

@click.group()
def cli():
    """ CLI util to call models running on Semantix GenAI Hub platform."""
    pass

@cli.command()
@click.option('--prompt', '-p', help='The prompt to use in the model.')
def inference(prompt):
    """SA python client library to make it easier to call Semantix GenAI model inference endpoint"""
    click.echo('CLI is being developed, use this as a module. Your prompt {0}.'.format(prompt))

if __name__ == '__main__':
    cli()