import streamlit as st
from migration.connector.destination.clickzetta.destination import ClickZettaDestination
from migration.connector.destination.doris.destination import DorisDestination
from migration.connector.source.clickzetta.source import ClickzettaSource
from migration.connector.source.doris.source import DorisSource


def destination_connection_test(config: dict):
    try:
        if config['db_type'] == 'doris':
            st.session_state['destination_connection'] = DorisDestination(config)
        elif config['db_type'] == 'clickzetta':
            st.session_state['destination_connection'] = ClickZettaDestination(config)
        else:
            st.error('Not supported yet')
            return
        st.session_state['destination_connection'].connect()
        st.success(f"{st.session_state['destination_connection'].name} Connection Success")
    except Exception as e:
        st.error('Connection Failed')
        st.error(e)


def source_connection_test(config: dict):
    try:
        if config['db_type'] == 'doris':
            st.session_state['src_connection'] = DorisSource(config)
        elif config['db_type'] == 'clickzetta':
            st.session_state['src_connection'] = ClickzettaSource(config)
        else:
            st.error('Not supported yet')
            return
        st.session_state['src_connection'].connect()
        st.success(f"{st.session_state['src_connection'].name} Connection Success")
    except Exception as e:
        st.error(e)
        st.error('Connection Failed')
