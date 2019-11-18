# -* - coding: UTF-8 -* -
 
import os
 
import ConfigParser
 
CONFIG_FILE = "Config.cfg"
 
def main():
 
    if os.path.exists( os.path.join( os.getcwd(),CONFIG_FILE ) ):

        config = ConfigParser.ConfigParser()

        config.read(CONFIG_FILE)

        #第一个参数指定要读取的段名，第二个是要读取的选项名

        host = config.get("DB_Config", "DATABASE_HOST") 

        port = config.get("DB_Config", "DATABASE_PORT")

        name = config.get("DB_Config", "DATABASE_NAME")

        username = config.get("DB_Config", "DATABASE_USERNAME")

        password = config.get("DB_Config", "DATABASE_PASSWORD")

        print host, port, name, username, password
 
if __name__ == '__main__': 
    main()
