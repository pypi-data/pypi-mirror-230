import io
import json
import os
import sys
import streamlit as st
import sqlglot

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from low_touch_tool.util import connect_util

dialects = ['bigquery', 'clickhouse', 'databricks', 'doris', 'drill', 'duckdb', 'hive', 'mysql', 'oracle',
            'postgres', 'presto', 'redshift', 'snowflake', 'spark', 'spark2', 'sqlite', 'starrocks',
            'tableau', 'teradata', 'trino', 'tsql', 'clickzetta']

TEXT_INPUT_KEY = 0

st.title('SQL Translation Tool')

config_col1, config_col2 = st.columns(2)

with config_col1:
    src_db = st.selectbox('source db', dialects, index=dialects.index('doris'))
    config = None
    if src_db == "mysql" or src_db == "doris":
        config = st.file_uploader('source config file', type=['json'])
        if config:
            config = json.load(io.BytesIO(config.getvalue()))
            host = config['host']
            port = config['port']
            username = config['username']
            password = config['password']
            config = {'fe_servers': [host + ':' + port], 'user': username,
                      'password': password, 'db_type': src_db}
        src_button = st.button('Connect Testing', key=TEXT_INPUT_KEY + 12)

        if src_button:
            connect_util.source_connection_test(config)
    else:
        # url = st.text_input('URL', value='', key=TEXT_INPUT_KEY + 14)
        st.error('Not supported yet')

with config_col2:
    dest_db = st.selectbox('destination db', ['clickzetta'], index=0)

    uploader = st.file_uploader('destination config file', type=['json'])

    if uploader:
        config = json.load(io.BytesIO(uploader.getvalue()))
        service = config['service']
        workspace = config['workspace']
        instance = config['instance']
        vcluster = config['vcluster']
        username = config['username']
        password = config['password']
        schema = config['schema']
        instance_id = config['instanceId']
        if instance_id is None or len(instance_id) == 0:
            st.text("instanceId is empty, will use the first instanceId")
            instance_id = 0

    dest_button = st.button('Connect Testing', key=TEXT_INPUT_KEY + 13)

    if dest_button:
        config = {'service': service, 'workspace': workspace, 'instance': instance,
                  'vcluster': vcluster, 'username': username, 'password': password, 'schema': schema,
                  'db_type': dest_db, 'instanceId': 300}
        connect_util.destination_connection_test(config)

st.subheader('SQL Transpile', divider='rainbow')

transpile_col1, transpile_col2 = st.columns(2)

with transpile_col1:
    src_dialect = st.selectbox('from dialect', dialects, index=dialects.index('doris'))
    src_sql = st.text_area('source sql', label_visibility='collapsed', height=300)
    transpile_button = st.button('Testing Transpiled SQL', key=TEXT_INPUT_KEY + 15)

with transpile_col2:
    dest_dialect = st.selectbox('to dialect', dialects, index=dialects.index('clickzetta'))
    dest_sql = st.empty()
    dest_sql.text_area('dest sql', label_visibility='collapsed', height=300, key=TEXT_INPUT_KEY + 14)
    exe_button = st.button('Testing Run Transpiled SQL', key=TEXT_INPUT_KEY + 17)

if src_sql:
    if transpile_button:
        try:
            ret = sqlglot.transpile(src_sql, read=src_dialect, write=dest_dialect, pretty=True)
            dest_sql.code(ret, language='sql')
            st.session_state['ret'] = ret
        except Exception as e:
            st.error(f'Transpile from {src_dialect} SQL to {dest_dialect} SQL Failed!')
            st.error(e)
if exe_button:
    try:
        result = st.session_state['destination_connection'].execute_sql(st.session_state['ret'][0])
        st.table(result)
        st.success('Transpiled SQL run successfully')
    except Exception as e:
        st.error('Transpiled SQL run failed')
        st.error(e)