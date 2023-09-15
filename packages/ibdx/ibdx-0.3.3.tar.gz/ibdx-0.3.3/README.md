# ibdx


## Use case

- backup/restore mysql InnoDB tables in an easy way


## Setup

#### From pypi
```
pip install ibdx
```

#### From source
```
git clone https://github.com/Grvzard/ibdx.git
cd ibdx
pip install .
```

#### Edit config
```
cp demo.env .env
vim .env
```
the .env works only when the ```ibdx``` command is running in that directory


## Usage

```ibdx --help```

**Take care:**
There seems to be an incompatibility between mysql and mariadb.
Make sure that ibdx works between the same db system.


## Example

Let's say we have following tables:
```[ logs_2023_01, logs_2023_02, logs_2023_03, logs_2023_04 ]```

```
ibdx backup --db test1 --tables logs_2023_* -f logs.2023.zip [--datadir /mysql/datadir]
```
```
ibdx restore -f logs.2023.zip --db test1 --tables logs_2023_* [--datadir /mysql/datadir]
```

When the mysql server is running in Docker, the _--datadir_ option is required.


## Script Workflow

backup:
1. mysql> ``` FLUSH TABLES test1 FOR EXPORT; ``` (tables are read locked)
2. backup the .ibd (and .cfg) files.
3. mysql> ``` UNLOCK TABLES; ```

restore:
1. (optional) mysql> ``` CREATE TABLE test1; ```
2. mysql> ``` ALTER TABLE test1 DISCARD TABLESPACE; ```
3. copy the .ibd (and .cfg) files to the mysql-server's datadir
4. mysql> ``` ALTER TABLE test1 IMPORT TABLESPACE; ```


## Reference

[MariaDB Knowledge Base > InnoDB File-Per-Table Tablespaces](https://mariadb.com/kb/en/innodb-file-per-table-tablespaces/#copying-transportable-tablespaces)
