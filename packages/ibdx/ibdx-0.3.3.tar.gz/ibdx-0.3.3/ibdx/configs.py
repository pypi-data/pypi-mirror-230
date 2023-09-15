from dotenv import dotenv_values


config = dotenv_values(".env")


DB_CONFIG = {
    'host': config['host'],
    'port': int(config['port']),
    'user': config['user'],
    'password': config['password'],
}
