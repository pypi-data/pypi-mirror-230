import io
import json
import os
import sys
import streamlit as st
import sqlglot

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from low_touch_tool.util import connect_util,validation_util

dialects = ['bigquery', 'clickhouse', 'databricks', 'doris', 'drill', 'duckdb', 'hive', 'mysql', 'oracle',
            'postgres', 'presto', 'redshift', 'snowflake', 'spark', 'spark2', 'sqlite', 'starrocks',
            'tableau', 'teradata', 'trino', 'tsql', 'clickzetta']

TEXT_INPUT_KEY = 0

st.title('Query Validation Tool')

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

st.subheader("Query Validation", divider='rainbow')

validation_col1, validation_col2 = st.columns(2)

with validation_col1:
    st.text('source database query')
    source_query = st.text_area('query', label_visibility='collapsed', height=300)

with validation_col2:
    st.text('destination database query')
    destination_query = st.text_area('result', label_visibility='collapsed', height=300)

validate_level = ['Basic verification', 'Multidimensional verification', 'Line by line verification']
level = st.selectbox('validate level', validate_level, index=0)

exe_validation = st.button('Execute Validation', key=TEXT_INPUT_KEY + 16)

if exe_validation:
    st.subheader("Validation Result", divider='rainbow')
    if level == 'Basic verification':
        try:
            source_df_result, destination_df_result = validation_util.gen_basic_validation_result(
                st.session_state['src_connection'],
                st.session_state['destination_connection'],
                source_query, destination_query)
            validation_util.display_validation_result(source_df_result, destination_df_result)

        except Exception as e:
            st.error(e)

    elif level == 'Multidimensional verification':
        try:
            source_df_result, destination_df_result = validation_util.multidimensional_validation(
                st.session_state['src_connection'],
                st.session_state['destination_connection'],
                source_query, destination_query)
            validation_util.display_validation_result(source_df_result, destination_df_result)

        except Exception as e:
            st.error(e)
    elif level == 'Line by line verification':
        try:
            source_df_result, destination_df_result = validation_util.line_by_line_validation(
                st.session_state['src_connection'],
                st.session_state['destination_connection'],
                source_query, destination_query)
            validation_util.display_validation_result(source_df_result, destination_df_result)

        except Exception as e:
            st.error(e)
    else:
        st.error('Not supported yet')