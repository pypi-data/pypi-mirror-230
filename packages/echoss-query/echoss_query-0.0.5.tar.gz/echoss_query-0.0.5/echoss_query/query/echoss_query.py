import yaml
import pymysql
import pandas as pd

from pymongo import MongoClient
from opensearchpy import OpenSearch


class MysqlQuery:
    def __init__(self, conn_info: str or dict):
        """
        Args:
            conn_info : configration dictionary
            ex) conn_info = {
                                'mysql':
                                    {
                                        'user'  : str(user),
                                        'passwd': str(pw),
                                        'host'  : int(ip),
                                        'db'    : str(db_name),
                                        'charset': str(utf8)
                                    }
                            }
        """
        if str(type(conn_info)) != "<class 'dict'>":
            if str(type(conn_info)) == "<class 'str'>":
                with open(conn_info,'r')as f:
                    conn_info = yaml.load(f,Loader=yaml.FullLoader)
            else:
                raise TypeError("MysqlQuery support type 'str' and 'dict'")

        if conn_info['mysql']['user'] != None:
            self.user = conn_info['mysql']['user']
            self.passwd = conn_info['mysql']['passwd']
            self.host = conn_info['mysql']['host']
            self.db = conn_info['mysql']['db']
            self.charset = conn_info['mysql']['charset']
        else:
            print('mysql : config info not exist')

    @staticmethod
    def _parsing(query: str) -> str:
        if ';' not in query:
            result = query + ';'
        return result

    def _connect_db(self) -> None:
        try:
            self.conn = pymysql.connect(
                user=self.user,
                passwd=self.passwd,
                host=self.host,
                db=self.db,
                charset=self.charset
            )
            return self.conn
        except Exception as e:
            print(e)

    def ping(self):
        """
        Args:
            Any

        Returns:
            str : DB Status
        """
        if self._connect_db().open:
            print('database connection success')
        else:
            raise ConnectionError('database connection fail')

    def databases(self):
        """
        Args:
            Any

        Returns:
            pd.DataFrame() : database dataframe
        """
        with self._connect_db() as conn:
            with conn.cursor(pymysql.cursors.SSCursor) as cur:
                cur.execute('SHOW DATABASES;')
                result = cur.fetchall()

                if result != ():
                    return pd.DataFrame(result)
                else:
                    print("can't find database")

    def tables(self, database: str):
        """
        Args:
            database(str) : name of database

        Returns:
            pd.DataFrame() : table dataframe
        """
        if database != None:
            db = pymysql.connect(
                user=self.user,
                passwd=self.passwd,
                host=self.host,
                db=database,
                charset=self.charset
            )
            with db as conn:
                with conn.cursor(pymysql.cursors.SSCursor) as cur:
                    cur.execute('SHOW TABLES;')
                    result = cur.fetchall()

                    if result != ():
                        return pd.DataFrame(result)
                    else:
                        print("can't find tables")
        else:
            print("can't find database")

    def conn_info(self):
        """
        Args:
            Any

        Returns:
            tuple : connection information(host_info, db_info, charset_info)
        """
        return (self.conn.host_info, self.conn.db, self.conn.charset)

    #################
    # DDL Functions #
    #################

    def create(self, query_str: str) -> None:
        """
        Args:
            query_str(str) : MySQL create query string
        """
        query = self._parsing(query_str)
        keyword = 'CREATE'
        if keyword in query or keyword.lower() in query:
            try:
                with self._connect_db() as conn:
                    with conn.cursor(pymysql.cursors.DictCursor) as cur:
                        cur.execute(query)
                    conn.commit()
            except Exception as e:
                print(e)
        else:
            raise ValueError('input is not include "create"')

    def drop(self, query_str: str) -> None:
        """
        Args:
            query_str(str) : MySQL drop query string
        """
        query = self._parsing(query_str)
        keyword = 'DROP'
        if keyword in query or keyword.lower() in query:
            try:
                with self._connect_db() as conn:
                    with conn.cursor(pymysql.cursors.DictCursor) as cur:
                        cur.execute(query)
                    conn.commit()
            except Exception as e:
                print(e)
        else:
            raise ValueError('input is not include "drop"')

    def truncate(self, query_str: str) -> None:
        """
        Args:
            query_str(str) : MySQL truncate query string
        """
        query = self._parsing(query_str)
        keyword = 'TRUNCATE'
        if keyword in query or keyword.lower() in query:
            try:
                with self._connect_db() as conn:
                    with conn.cursor(pymysql.cursors.DictCursor) as cur:
                        cur.execute(query)
                    conn.commit()
            except Exception as e:
                print(e)
        else:
            raise ValueError('input is not include "truncate"')

    def alter(self, query_str: str) -> None:
        """
        Args:
            query_str(str) : MySQL alter query string
        """
        query = self._parsing(query_str)
        keyword = 'ALTER'
        if keyword in query or keyword.lower() in query:
            try:
                with self._connect_db() as conn:
                    with conn.cursor(pymysql.cursors.DictCursor) as cur:
                        cur.execute(query)
                    conn.commit()
            except Exception as e:
                print(e)
        else:
            raise ValueError('input is not include "alter"')

    #################
    # DDL Functions #
    #################
    def select_list(self, query_str: str) -> list:
        """
        Args:
            query_str(str) : MySQL select query string

        Returns:
            list() : List of query result
        """
        query = self._parsing(query_str)
        keyword = 'SELECT'

        if keyword in query or keyword.lower() in query:
            try:
                with self._connect_db() as conn:
                    with conn.cursor() as cur:
                        cur.execute(query)
                        result = cur.fetchall()

                        if result != ():
                            return [x for tuple_ in result for x in tuple_]
                        else:
                            print('data not exist')
            except Exception as e:
                print(e)
        else:
            raise ValueError('input is not include "select"')

    def select(self, query_str: str) -> pd.DataFrame:
        """
        Args:
            query_str(str) : MySQL select query string

        Returns:
            pd.DataFrame() : DataFrame of query result
        """
        query = self._parsing(query_str)
        keyword = 'SELECT'

        if keyword in query or keyword.lower() in query:
            try:
                with self._connect_db() as conn:
                    with conn.cursor(pymysql.cursors.DictCursor) as cur:
                        cur.execute(query)
                        result = cur.fetchall()

                        if result != ():
                            return pd.DataFrame(result)
                        else:
                            print('data not exist')
            except Exception as e:
                print(e)
        else:
            raise ValueError('input is not include "select"')

    def faster_select(self, query_str: str) -> pd.DataFrame:
        """
        Args:
            query_str(str) : MySQL select query string better than normal select

        Returns:
            pd.DataFrame() : DataFrame of query result
        """
        query = self._parsing(query_str)
        keyword = 'SELECT'
        if keyword in query or keyword.lower() in query:
            try:
                with self._connect_db() as conn:
                    with conn.cursor(pymysql.cursors.SSCursor) as cur:
                        cur.execute(query)
                        result = cur.fetchall()

                        if result != ():
                            return pd.DataFrame(result)
                        else:
                            print('data not exist')
            except Exception as e:
                print(e)
            self.conn.close()
        else:
            raise ValueError('input is not include "select"')

    def insert(self, query_str: str) -> None:
        """
        Args:
            query_str(str) : MySQL insert query string

        Returns:
            pd.DataFrame() : DataFrame of query result
        """
        query = self._parsing(query_str)
        keyword = 'INSERT'
        if keyword in query or keyword.lower() in query:
            try:
                with self._connect_db() as conn:
                    with conn.cursor(pymysql.cursors.DictCursor) as cur:
                        cur.execute(query)
                    conn.commit()
            except Exception as e:
                print(e)
        else:
            raise ValueError('input is not include "insert"')

    def update(self, query_str: str) -> None:
        """
        Args:
            query_str(str) : MySQL update query string

        Returns:
            pd.DataFrame() : DataFrame of query result
        """
        query = self._parsing(query_str)
        keyword = 'UPDATE'
        if keyword in query or keyword.lower() in query:
            try:
                with self._connect_db() as conn:
                    with conn.cursor(pymysql.cursors.DictCursor) as cur:
                        cur.execute(query)
                        print(f'update {cur.rowcount} rows')
                    conn.commit()
            except Exception as e:
                print(e)

        else:
            raise ValueError('input is not include "update"')

    def delete(self, query_str: str) -> None:
        """
        Args:
            query_str(str) : MySQL delete query string

        Returns:
            pd.DataFrame() : DataFrame of query result
        """
        query = self._parsing(query_str)
        keyword = 'DELETE'
        if keyword in query or keyword.lower() in query:
            try:
                with self._connect_db() as conn:
                    with conn.cursor(pymysql.cursors.DictCursor) as cur:
                        cur.execute(query)
                        print(f'delete {cur.rowcount} rows')
                    conn.commit()
            except Exception as e:
                print(e)
        else:
            raise ValueError('input is not include "delete"')

    def close(self):
        self.conn.close()


class MongoQuery:
    def __init__(self, conn_info: str or dict):
        """
        Args:
            region_env(str) : Config File Regsion
            ex) conn_info = {
                                'mongo':
                                    {
                                        'host'  : int(ip),
                                        'port'  : int(port)),
                                        'db'    : str(db_name)
                                    }
                            }
        """
        if str(type(conn_info)) != "<class 'dict'>":
            if str(type(conn_info)) == "<class 'str'>":
                with open(conn_info,'r')as f:
                    conn_info = yaml.load(f,Loader=yaml.FullLoader)
            else:
                raise TypeError("MongoQuery support type 'str' and 'dict'")

        if conn_info['mongo']['port'] != None:
            self.client = MongoClient(
                host=conn_info['mongo']['host'],
                port=conn_info['mongo']['port']
            )

            self.db_name = conn_info['mongo']['db']
            self.db = self.client[self.db_name]
        else:
            if conn_info['mongo']['uri'] != None:
                self.client = MongoClient(
                    host=conn_info['mongo']['uri']
                )
            else:
                print('mongo : config info not exist')

    @staticmethod
    def _parsing(query: str) -> str:
        if len(query) != 1:
            default, modify = query
            return default, modify
        else:
            query = query[0]
            return query

    def ping(self):
        """
        Args:
            Any

        Returns:
            str : DB Status
        """
        stat = self.client.admin.command('ping').keys()
        if 'ok' in str(stat):
            print('database connection success')
        else:
            raise ConnectionError('database connection fail')

    def databases(self):
        """
        Args:
            Any

        Returns:
            string : Database list
        """
        result = self.client.list_database_names()
        return pd.DataFrame(result, columns=['Database'])

    def collections(self, database: str) -> pd.DataFrame:
        """
        Args:
            database(str) : database name

        Returns:
            pd.DataFrame() : collection dataframe
        """
        db = self.client[database]
        result = db.list_collection_names()
        return pd.DataFrame(result, columns=['Table'])

    def select(self, collection: str, *query: str or dict) -> pd.DataFrame:
        """
        Args:
            collection(str) :
            *query(str or dict) : Mongo select query string

        Returns:
            pd.DataFrame() : DataFrame of query result
        """
        query = self._parsing(query)

        query = eval(f"self.db.{collection}.find({query})")

        return pd.DataFrame(list(query))

    def insert(self, collection: str, *query: str or dict) -> None:
        """
        Args:
            collection(str) : target collection
            *query(str or dict) : Mongo insert query string

        Returns:
            pd.DataFrame() : DataFrame of query result
        """
        query = self._parsing(query)
        eval(f"self.db.{collection}.insert_one({query})")

    def update(self, collection: str, *query: str or dict) -> None:
        """
        Args:
            collection(str) : target collection
            *query(str or dict) : Mongo update query string

        Returns:
            pd.DataFrame() : DataFrame of query result
        """
        default, modify = self._parsing(query)
        eval(f"self.db.{collection}.update_one({default}, {modify})")

    def delete(self, collection: str, *query: str or dict) -> None:
        """
        Args:
            collection(str) : target collection
            *query(str or dict) : Mongo delete query string

        Returns:
            pd.DataFrame() : DataFrame of query result
        """
        query = self._parsing(query)
        if query == {}:
            raise ValueError("can't delete all collection")
        else:
            return eval(f"self.db.{collection}.delete_one({query})")

    def new_index(self, collection: str, document: str) -> int:
        """
        Args:
            collection(str) : target collection
            document(str) : target document
        Returns:
            int() : maximum value
        """
        max_rows = list(eval(f"self.db.{collection}.find().sort([('{document}',-1)]).limit(1)"))
        if max_rows != []:
            max_value = max_rows[0][document]
            index = max_value + 1
        else:
            index = 1

        return index
    
class ElasticSearch:
    def __init__(self, conn_info: str or dict):
        """
        Args:
            conn_info : configration dictionary
            ex) conn_info = {
                                'elastic':
                                    {
                                        'user'  : str(user),
                                        'passwd': str(pw),
                                        'cloud_id'  : str(id),
                                        'index' : str(index)
                                    }
                            }
        """
        if str(type(conn_info)) != "<class 'dict'>":
            if str(type(conn_info)) == "<class 'str'>":
                with open(conn_info,'r')as f:
                    conn_info = yaml.load(f,Loader=yaml.FullLoader)
            else:
                raise TypeError("ElasticSearch support type 'str' and 'dict'")

        if conn_info['elastic']['user'] != None:
            self.user = conn_info['elastic']['user']
            self.passwd = conn_info['elastic']['passwd']
            self.host = conn_info['elastic']['host']
            self.port = conn_info['elastic']['port']
            self.index_name = conn_info['elastic']['index']

            self.hosts = [{
                'host' : self.host,
                'port' : self.port
            }]
            
            self.auth = (self.user, self.passwd)

        else:
            print('elastic : config info not exist')

    def _connect_es(self) -> None:
        """
        ElasticSearch Cloud에 접속하는 함수
        """
        self.es = OpenSearch(
            hosts=self.hosts,
            http_compress = True,
            http_auth=self.auth,
            use_ssl = True,
            verify_certs = True,
            ssl_assert_hostname = False,
            ssl_show_warn = False
        )
        return self.es
    
    def ping(self) -> bool:
        """
        Elastic Search에 Ping
        """
        with self._connect_es() as conn:
            return conn.ping()
    
    def info(self) -> dict:
        """
        Elastic Search Information
        """
        with self._connect_es() as conn:
            return conn.info()
    
    def exists(self, id:str or int=None) -> bool:
        """
        Args:
            index(str) : 확인 대상 index \n
            id(str) : 확인 대상 id \n
        Returns:
            boolean
        """
        with self._connect_es() as conn:
            return conn.exists(index=self.index_name, id=id)
        
    def search_list(self, body:dict) -> list:
        """
        Returns:
            result(list) : search result
        """
        with self._connect_es() as conn:
            result = conn.search(
                index = self.index_name,
                body=body
            )
        return result['hits']['hits']
        
    def search(self, body:dict) -> list:
        """
        Returns:
            result(list) : search result
        """
        with self._connect_es() as conn:
            result = conn.search(
                index = self.index_name,
                body=body
            )
        return result
    
    def search_field(self, field:str, value:str) -> list:
        """
        해당 index, field, value 값과 비슷한 값들을 검색해주는 함수 \n
        Args:
            field(str) : 검색 대상 field \n
            value(str) : 검색 대상 value \n
        Returns:
            result(list) : 검색 결과 리스트
        """
        with self._connect_es() as conn:
            result = conn.search(
                    index=self.index_name,
                    body={
                        'query':{
                            'match': {field: value}
                        }
                }
            )
        return result['hits']['hits']
    
    def get(self, id:str or int) -> dict:
        """
        index에서 id와 일치하는 데이터를 불러오는 함수 \n
        Args:
            id(str) : 가져올 대상 id \n
        Returns:
            result(dict) : 결과 데이터

        """
        with self._connect_es() as conn:
            return conn.get(index=self.index_name, id=id)
        
    def get_source(self, id:str or int) -> dict:
        """
        index에서 id와 일치하는 데이터의 소스만 불러오는 함수 \n
        Args:
            id(str) : 가져올 대상 id \n
        Returns:
            result(dict) : 결과 데이터

        """
        with self._connect_es() as conn:
            return conn.get_source(index=self.index_name, id=id)
        
    def create(self, id:str or int, body:dict):
        """
        index에 해당 id로 새로운 document를 생성하는 함수 \n
        (기존에 있는 index에 데이터를 추가할 때 사용) \n
        Args:
            id(str) : 생성할 id \n
        Returns:
            result(str) : 생성 결과
        """
        with self._connect_es() as conn:
            return conn.create(index=self.index_name, id=id, body=body)
        
    def index(self, index:str, body:dict, id:str or int=None) -> str:
        """
        index를 생성하고 해당 id로 새로운 document를 생성하는 함수 \n
        (index를 추가하고 그 내부 document까지 추가하는 방식) \n
        Args:
            index(str) : 생성할 index name \n
            id(str) : 생성할 id \n
            body(dict) : 입력할 json 내용
        Returns:
            result(str) : 생성 결과
        """
        with self._connect_es() as conn:
            if id == None:
                return conn.index(index=index, body=body)
            else:
                return conn.index(index=index, id=id, body=body)

    def update(self, id:str or int, body:dict) -> str:
        """
        기존 데이터를 id를 기준으로 body 값으로 수정하는 함수 \n
        Args:
            id(str) : 수정할 대상 id \n
        Returns:
            result(str) : 처리 결과
        """
        with self._connect_es() as conn:
            return conn.update(index=self.index_name, id=id, body=body)

    def delete(self, id:str or int) -> str:
        """
        삭제하고 싶은 데이터를 id 기준으로 삭제하는 함수 \n
        Args:
            id(str) : 삭제 대상 id \n
        Returns:
            result(str) : 처리 결과
        """
        with self._connect_es() as conn:
            return conn.delete(index=self.index_name, id=id)
        
    def delete_index(self, index):
        """
        인덱스를 삭제하는 명령어 신중하게 사용해야한다.\n
        Args:
            index(str) : 삭제할 index
        Returns:
            result(str) : 처리 결과
        """
        with self._connect_es() as conn:
            return conn.indices.delete(index=index)

class ElasticSearchV2:
    def __init__(self, conn_info: str or dict):
        """
        Connection Pool을 유지한 상태로 통신하는 방식
        Args:
            conn_info : configration dictionary
            ex) conn_info = {
                                'elastic':
                                    {
                                        'user'  : str(user),
                                        'passwd': str(pw),
                                        'cloud_id'  : str(id),
                                        'index' : str(index)
                                    }
                            }
        """
        if str(type(conn_info)) != "<class 'dict'>":
            if str(type(conn_info)) == "<class 'str'>":
                with open(conn_info,'r')as f:
                    conn_info = yaml.load(f,Loader=yaml.FullLoader)
            else:
                raise TypeError("ElasticSearch support type 'str' and 'dict'")

        if conn_info['elastic']['user'] != None:
            self.user = conn_info['elastic']['user']
            self.passwd = conn_info['elastic']['passwd']
            self.host = conn_info['elastic']['host']
            self.port = conn_info['elastic']['port']
            self.index_name = conn_info['elastic']['index']

            self.hosts = [{
                'host' : self.host,
                'port' : self.port
            }]
            
            self.auth = (self.user, self.passwd)
            self.conn = OpenSearch(
                hosts=self.hosts,
                http_compress = True,
                http_auth=self.auth,
                use_ssl = True,
                verify_certs = True,
                ssl_assert_hostname = False,
                ssl_show_warn = False
            )

        else:
            print('elastic : config info not exist')

    def ping(self) -> bool:
        """
        Elastic Search에 Ping
        """
        return self.conn.ping()
    
    def info(self) -> dict:
        """
        Elastic Search Information
        """
        return self.conn.info()
    
    def exists(self, id:str or int=None) -> bool:
        """
        Args:
            echoss_query_env(env_var) : Region Name
            ex export echoss_query=kr_local
    """

    # import os
    import yaml

    #### region = os.environ['echoss_query_env']
    # 환경 변수를 가져와서 인자 값으로 할당하는 방식
    #
    with open('../config/config.yaml', 'r') as file:
        yaml_info = yaml.load(file, Loader=yaml.FullLoader)

    # mysql = MysqlQuery(yaml_info['kr_local'])
    mongo = MongoQuery(yaml_info['kr_stag'])
    # print(mongo.new_index('project_info', 'project_number'))
    # # print(mysql.update("""UPDATE PROJECT_INFO SET PROJECT_NUMBER = 777 WHERE = PROJECT_NAME = 'abalone'"""))
    # # print(mysql.select_list('SELECT 영수증번호 FROM sys.`ppcd_df-001.csv` WHERE 고객번호 = 1'))
    # # print(mongo.select('ppcd_df', {'고객번호':1}))
    # # print(mysql.databases())
    # # print(mongo.databases())
    # print(mongo.create('test_collection2'))
