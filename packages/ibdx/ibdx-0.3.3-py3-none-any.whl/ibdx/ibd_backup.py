import zipfile
from pathlib import Path
import fnmatch

from . import __version__
from .mysql_db_quick import MysqlConn
from .configs import DB_CONFIG


def ibd_backup(
    dbname: str,
    tables_pattern: str,
    out_fpath: str,
    datadir: str = '',
) -> None:
    db = MysqlConn(dbname, DB_CONFIG)

    if not datadir:
        res = db.query('show variables like \'datadir\';').fetchone()
        if res is None:
            raise Exception('cannot get datadir')
        datadir = res[1]
        if not Path(datadir).exists():
            raise Exception('datadir does not exists')

    db_dpath = Path(datadir) / dbname
    assert db_dpath.is_dir()

    _out_fpath = Path(out_fpath)

    if not _out_fpath.exists():
        with zipfile.ZipFile(_out_fpath, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            zip_file.writestr(f'.ibdx.v{__version__}', f'{__version__}')

    tables = fnmatch.filter(db.get_tables(), tables_pattern)

    with zipfile.ZipFile(_out_fpath, 'a', zipfile.ZIP_DEFLATED) as zip_file:
        for table in tables:
            print(f"backup table: {table}")

            db.query(f"flush tables `{table}` for export;")
            try:
                sql_create = db.query(f'show create table `{table}`;').fetchall()[0][1]
                zip_file.writestr(f'{table}.sql', sql_create)
                zip_file.write(db_dpath / f'{table}.ibd', f'{table}.ibd')
                zip_file.write(db_dpath / f'{table}.cfg', f'{table}.cfg')
            finally:
                db.query('unlock tables;')
