# hql_parser

A parser package which extracts fields, types and comments from a HIVE DDL. For instance, given the next `ddl.sql` file

```sql
CREATE TABLE `school.student`(
  `dni` varchar(100) COMMENT 'Identificator National Number', 
  `first_name` varchar(10) COMMENT 'First name', 
  `second_name` varchar(50) COMMENT 'Second name', 
  `age` int COMMENT 'How old is this student', 
  `nickname` varchar(30) COMMENT 'Nickname', 
  `flg_estado` smallint COMMENT 'Flag (1 - Active, 0 - No Active)')
CLUSTERED BY (dni) 
INTO 1 BUCKETS
ROW FORMAT SERDE 
  'org.apache.hadoop.hive.ql.io.orc.OrcSerde' 
STORED AS INPUTFORMAT 
  'org.apache.hadoop.hive.ql.io.orc.OrcInputFormat' 
OUTPUTFORMAT 
  'org.apache.hadoop.hive.ql.io.orc.OrcOutputFormat'
LOCATION
  'hdfs://nnha/data/environment/datalake/school/student'
TBLPROPERTIES (
  'last_modified_by'='root', 
  'last_modified_time'='1662590768', 
  'numFiles'='1600', 
  'totalSize'='1913197', 
  'transactional'='true', 
  'transient_lastDdlTime'='1666985788')

```

It can be parsed as followed:

```py
from hql_parser import DDL_Handler
ddlh = DDL_Handler()
obj = ddlh.file_parser('ddl.sql')
print(obj)
```

The result is a three-items list:

- Position 0: schema name

- Position 1: table name

- Position 2: a list of table field with following the format `{'field': '', 'ttype': '', 'comment': ''}`


This example prints the next output
```py
[
  'school', 
  'student', 
  [
    {'field': 'dni', 'ttype': 'varchar(100)', 'comment': 'Identificator National Number'}, 
    {'field': 'first_name', 'ttype': 'varchar(10)', 'comment': 'First name'}, 
    {'field': 'second_name', 'ttype': 'varchar(50)', 'comment': 'Second name'}, 
    {'field': 'age', 'ttype': 'int', 'comment': 'How old is this student'}, 
    {'field': 'nickname', 'ttype': 'varchar(30)', 'comment': 'Nickname'}, 
    {'field': 'flg_estado', 'ttype': 'smallint', 'comment': 'Flag (1 - Active, 0 - No Active)'}
  ]
]
```

On the other hand, we can parse a content variable as next:

```py
obj = ddl_parser(ddl_content_str)
```
