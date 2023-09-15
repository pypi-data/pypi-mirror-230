from pymysql import connect


class MysqlConn:
    def __init__(self, db, config):
        self.config = config
        self.conn = connect(**self.config, database=db)
        self.db = db

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.close()

    def query(self, sql):
        cursor = self.conn.cursor()
        cursor.execute(sql)
        self.conn.commit()
        return cursor

    def get_tables(self):
        with self.query('show tables') as cur:
            return [rs_tup[0] for rs_tup in cur]
