import io
import json
import os
import sys
import streamlit as st


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from low_touch_tool.util import connect_util

TEXT_INPUT_KEY = 0
dialects = ['bigquery', 'clickhouse', 'databricks', 'doris', 'drill', 'duckdb', 'hive', 'mysql', 'oracle',
            'postgres', 'presto', 'redshift', 'snowflake', 'spark', 'spark2', 'sqlite', 'starrocks',
            'tableau', 'teradata', 'trino', 'tsql', 'clickzetta']

st.title('Connection Testing Tool')

st.subheader("Database Configuration", divider='rainbow')
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
