import typer

from .ibd_backup import ibd_backup
from .ibd_restore import ibd_restore
from .tools import zipfile_ls
from .deps import complete_filename


cli = typer.Typer()


@cli.command()
def backup(
    dbname: str = typer.Option(..., '--db', '-d'),
    tables_pattern: str = typer.Option('*', '--tables', '-t'),
    output_filename: str = typer.Option(..., '--file', '-f', autocompletion=complete_filename),
    datadir: str = typer.Option(''),
):
    try:
        ibd_backup(dbname, tables_pattern, output_filename, datadir)
    except Exception as e:
        typer.echo(f'ibdx error: {e}')


@cli.command()
def restore(
    dbname: str = typer.Option(..., '--db', '-d'),
    tables_pattern: str = typer.Option('*', '--tables', '-t'),
    input_filename: str = typer.Option(..., '--file', '-f', autocompletion=complete_filename),
    datadir: str = typer.Option(''),
):
    try:
        ibd_restore(dbname, tables_pattern, input_filename, datadir)
    except Exception as e:
        typer.echo(f'ibdx error: {e}')


@cli.command()
def ls(zipfile_name: str = typer.Argument('', autocompletion=complete_filename)):
    try:
        for name in zipfile_ls(zipfile_name):
            typer.echo(name)
    except Exception as e:
        typer.echo(f'ibdx error: {e}')
