import yaml
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from datetime import datetime
from query import echoss_query


class MysqlGenerate:
    def __init__(self, config_path: str, region: str):
        """
        Args:
            config_path(str) : config file path
            region(str) : region key in config file(yaml)
        """
        with open(config_path, 'r') as f:
            self.config = yaml.load(f, Loader=yaml.FullLoader)
            self.conn_info = self.config[region]

        self.mysql = echoss_query.MysqlQuery(self.conn_info)
        self.mongo = echoss_query.MongoQuery(self.conn_info)

    def project_add(self, project_name: str) -> None:
        """
        Args:
             project_name(str) :  insert project_info table project_name
        """
        try:
            project_count = self.mysql.select(f"""
            SELECT * FROM project_info WHERE project_name = '{project_name}'""")
            raise ValueError(f'{len(project_count)} project exist')

        except Exception as e:
            print(e)
            self.mysql.insert(f"""
            INSERT INTO project_info(project_name, start_timestamp) 
            VALUES('{project_name}','{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}')
            """)

    def make_tables(self, project_name: str, table_name_list=None):
        """
        Args:
            project_name(str) : project_info table project_name
            table_name_list(list) : default(['IMAGE_INFO', 'JSON_INFO', 'TXT_INFO'])
        """
        if table_name_list is None:
            table_name_list = ['image_info', 'json_info', 'txt_info']

        project_id = int(self.mysql.select(f"""
        SELECT * FROM project_info WHERE project_name = '{project_name}'  ORDER BY project_id DESC LIMIT 1
        """)['project_id'].values)

        for table_name in table_name_list:
            cat_name = table_name.split('_')[0]
            self.mysql.create(f"""
            CREATE TABLE p{project_id}_{table_name}(
            {cat_name}_id	int(10)	NOT NULL AUTO_INCREMENT,
            file_id int(10) NOT NULL COMMENT '확장자를 제외한 파일 이름 PK',
            s3_link varchar(255) NULL COMMENT 'S3 경로',
            bucket_name varchar(255) NULL COMMENT '버킷 이름',
            prefix varchar(255) NULL,
            file_name varchar(255) NULL,
            modified_time datetime NULL COMMENT '수정 시간',
            PRIMARY KEY(`{cat_name}_id`),
            FOREIGN KEY(`file_id`) REFERENCES p{project_id}_data_info(`file_id`))
            """)

    def connection_table(self, project_name: str, config: dict=None):
        """
        Args:
            project_name(str) : project_info table project_name
            config(dict) : table properties
                            ex)
                            dict = {
                                        'column1(str)' : ['type(str)', 'null(str)'],
                                        'column2(str)' : ['type(str)', 'not null(str)'],
                                        'column3(str)' : ['type(str)', 'null(str)']
                                    }

        """
        project_id = int(self.mysql.select(f"""
        SELECT * FROM project_info WHERE project_name = '{project_name}'  ORDER BY project_id DESC LIMIT 1
        """)['project_id'].values)
    
        if config == None:
            self.mysql.create(f"""
            CREATE TABLE p{project_id}_data_info(
            file_id int(10) NOT NULL COMMENT '확장자를 제외한 파일 이름 PK' AUTO_INCREMENT,
            project_id int(10) NOT NULL COMMENT '프로젝트 번호',
            file_name varchar(255) NULL,
            PRIMARY KEY(file_id),
            FOREIGN KEY(project_id) REFERENCES project_info (project_id) ON UPDATE CASCADE)
            """)
        else:
            columns = config.keys()
            types = [value[0] for value in config.values()]
            nulls = [value[1] for value in config.values()]

            table_property = ''
            for idx, [column, typ, nul] in enumerate(zip(columns, types, nulls)):
                if len(columns) != idx + 1:
                    row = f'{column} {typ} {nul},\n'
                    table_property = '\t\t'.join([table_property, row])
                else:
                    row = f'{column} {typ} {nul}'
                    table_property = '\t\t'.join([table_property, row])

            self.mysql.create(f"""
            CREATE TABLE p{project_id}_data_info(
            file_id int(10) NOT NULL COMMENT '확장자를 제외한 파일 이름 PK' AUTO_INCREMENT,
            project_id int(10) NOT NULL COMMENT '프로젝트 번호',
            {table_property.strip()+','}
            PRIMARY KEY(file_id),
            FOREIGN KEY(project_id) REFERENCES project_info (project_id) ON UPDATE CASCADE)
            """)


class MongoGenerate:
    def __init__(self, config_path: str, region: str):
        """
        Args:
            config_path(str) : config file path
            region(str) : region key in config file(yaml)
        """
        with open(config_path, 'r') as f:
            self.config = yaml.load(f, Loader=yaml.FullLoader)
            self.conn_info = self.config[region]

        self.mongo = echoss_query.MongoQuery(self.conn_info)

    def project_add(self, project_name: str) -> None:
        """
        Args:
             project_name(str) :  insert project_info table project_name
        """
        project_count = len(self.mongo.select('project_info', {'project_name': project_name}))
        if project_count == 0:
            project_id = self.mongo.new_index('project_info', 'project_id')
            start_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            self.mongo.insert('project_info',
                              {'project_id': project_id,
                               'project_name': project_name,
                               'start_timestamp': start_timestamp,
                               'end_timestamp': None})
        else:
            raise ValueError(f'{project_count} project exist')

    def make_tables(self, project_name: str, table_name_list=None):
        """
        Args:
            project_name(str) : project_info table project_name
            table_name_list(list) : default(['IMAGE_INFO', 'JSON_INFO', 'TXT_INFO'])
        """
        project_rows = self.mongo.select('project_info', {'project_name': project_name})
        project_id = int(project_rows['project_id'].values)
        if table_name_list is None:
            table_name_list = ['image_info', 'json_info', 'txt_info']

        for table_name in table_name_list:
            cat_name = table_name.split('_')[0]
            self.mongo.insert(f'p{project_id}_{table_name}',
                              {f'{cat_name}_id': '',
                               'file_id': '',
                               's3_link': '',
                               'bucket_name': '',
                               'full_path': '',
                               'modified_time': ''})

    def connection_table(self, project_name: str):
        """
        Args:
            project_name(str) : project_info table project_name
            - auto generate document
        """
        project_rows = self.mongo.select('project_info', {'project_name': project_name})
        project_id = int(project_rows['project_id'].values)
        self.mongo.insert(f'p{project_id}_data_info',
                          {f'file_id': '',
                           'project_id': '',
                           'file_name': ''})


if __name__ == '__main__':
    # gen = MongoGenerate('/home/ubuntu/jupyter_notebooks/db_connection/config/config.yaml', 'kr_local')
    # gen.connection_table(1234,'test123',\
    #                     ['TEST2','TEST3','TEST4','TEST5','TEST6'],\
    #                      ['varchar(255)','varchar(255)','varchar(255)','varchar(255)','varchar(255)','varchar(255)'],\
    #                      ['NOT NULL','NULL','NULL','NULL','NULL','NULL'])
    # gen.project_add(5,'테스트_프로젝트5')

    gen = MysqlGenerate('../config/config.yaml', 'kr_local')
    pj_name = 'receiver_test'
    # pj_name = 'test_name'
    #
    # dict_t = {
    #     'test_column1': ['varchar(255)', 'not null'],
    #     'test_column2': ['varchar(255)', 'null'],
    #     'test_column3': ['varchar(255)', 'null'],
    #     'test_column4': ['varchar(255)', 'not null'],
    #     'test_column5': ['varchar(255)', 'null'],
    #     'test_column6': ['varchar(255)', 'null'],
    # }
    
    # gen.project_add(project_name=pj_name)
    gen.connection_table(project_name=pj_name)
    gen.make_tables(project_name=pj_name)
    #
    #
    # gen.project_add(pj_name)
    # gen.make_tables(pj_name)
    # gen.connection_table(pj_name,{})
