class DevelomentConfig():
    DEBUG=True
    MYSQL_HOST = 'localhost'
    MYSQL_USER = 'root'
    MYSQL_PASSWORD = ''
    MYSQL_DB = 'pruebabackend'
    MYSQL_PORT = 3306    

config={
    'development': DevelomentConfig
}