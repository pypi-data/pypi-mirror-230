import zipfile
from pathlib import Path
from contextlib import suppress
import fnmatch

from .mysql_db_quick import MysqlConn
from .configs import DB_CONFIG


def ibd_restore(
    dbname: str,
    tables_pattern: str,
    in_fpath: str,
    datadir: str,
) -> None:
    db = MysqlConn(dbname, DB_CONFIG)

    if not zipfile.is_zipfile(in_fpath):
        raise Exception('in_fpath is not a zip file')

    if not datadir:
        res = db.query('show variables like \'datadir\';').fetchone()
        if res is None:
            raise Exception('cannot get datadir')
        datadir = res[1]

    db_path = Path(datadir) / dbname
    assert db_path.is_dir()

    with zipfile.ZipFile(in_fpath, 'r', zipfile.ZIP_DEFLATED) as zip_file:
        target_ibd_files = fnmatch.filter(
            zip_file.namelist(),
            f'{tables_pattern}.ibd',
        )
        target_sql_files = fnmatch.filter(
            zip_file.namelist(),
            f'{tables_pattern}.sql',
        )

        for sql_file in target_sql_files:
            table = sql_file.rsplit('.')[0]
            print(f"executing sql: {table}")

            with suppress(Exception):
                sql_create = zip_file.read(sql_file)
                db.query(sql_create)

        for ibd_file in target_ibd_files:
            table = ibd_file.rsplit('.')[0]
            print(f"importing tablespace: {table}")

            try:
                db.query(f'alter table `{table}` discard tablespace')
                print(f'. alter table `{table}` discard tablespace')

                zip_file.extract(f'{table}.ibd', db_path)
                (db_path / f'{table}.ibd').chmod(0o666)
                print(f'.. extract {table}.ibd')
                with suppress(Exception):
                    zip_file.extract(f'{table}.cfg', db_path)
                    print(f'.. extract {table}.cfg')

                db.query(f'alter table `{table}` import tablespace')
                print(f'... alter table `{table}` import tablespace')

            except Exception as e:
                (db_path / f'{table}.ibd').unlink(missing_ok=True)
                (db_path / f'{table}.cfg').unlink(missing_ok=True)

                # db.query(f'drop table if exists `{table}`;')

                raise Exception('failed when importing tablespace: ' + str(e))
