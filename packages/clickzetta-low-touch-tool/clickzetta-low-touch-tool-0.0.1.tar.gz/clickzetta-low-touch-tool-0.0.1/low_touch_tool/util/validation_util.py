import pandas as pd
import streamlit as st
from migration.connector.destination.base import Destination
from migration.connector.source import Source
from migration.util import validation_util


def gen_basic_validation_result(source: Source, destination: Destination, source_query: str, destination_query: str):
    try:
        result_dict = validation_util.basic_validation(source, destination, source_query, destination_query)
        source_dict = {}
        destination_dict = {}
        source_keys = []
        destination_keys = []
        for key in result_dict:
            if 'source' in key:
                if '_source_' in key:
                    final_key = key.replace('_source_', '_')
                elif 'source_' in key:
                    final_key = key.replace('source_', '')
                source_dict[final_key] = [result_dict[key]]
                source_keys.append(key)
            elif 'destination' in key:
                if '_destination_' in key:
                    final_key = key.replace('_destination_', '_')
                elif 'destination_' in key:
                    final_key = key.replace('destination_', '')
                destination_dict[final_key] = [result_dict[key]]
                destination_keys.append(key)

        source_df = pd.DataFrame.from_dict(source_dict, orient='index')
        destination_df = pd.DataFrame.from_dict(destination_dict, orient='index')
        return source_df, destination_df
    except Exception as e:
        raise e


def multidimensional_validation(source: Source, destination: Destination, source_query: str, destination_query: str):
    try:
        source_result, destination_result = validation_util.multidimensional_validation(source_query, destination_query,
                                                                                        source,
                                                                                        destination)
        source_df_result = pd.DataFrame()
        destination_df_result = pd.DataFrame()
        source_df_result['column_name'] = [row[0] for row in source_result]
        source_df_result['column_type'] = [row[1] for row in source_result]
        source_df_result['row_count'] = [row[2] for row in source_result]
        source_df_result['not_null_proportion'] = [row[3] for row in source_result]
        source_df_result['distinct_proportion'] = [row[4] for row in source_result]
        source_df_result['distinct_count'] = [row[5] for row in source_result]
        source_df_result['is_unique'] = [row[6] for row in source_result]
        source_df_result['min_value'] = [row[7] for row in source_result]
        source_df_result['max_value'] = [row[8] for row in source_result]
        source_df_result['avg_value'] = [row[9] for row in source_result]
        source_df_result['stddev_pop_value'] = [row[10] for row in source_result]
        source_df_result['stddev_sample_value'] = [row[11] for row in source_result]

        destination_df_result['column_name'] = [row[0] for row in destination_result]
        destination_df_result['column_type'] = [row[1] for row in destination_result]
        destination_df_result['row_count'] = [row[2] for row in destination_result]
        destination_df_result['not_null_proportion'] = [row[3] for row in destination_result]
        destination_df_result['distinct_proportion'] = [row[4] for row in destination_result]
        destination_df_result['distinct_count'] = [row[5] for row in destination_result]
        destination_df_result['is_unique'] = [row[6] for row in destination_result]
        destination_df_result['min_value'] = [row[7] for row in destination_result]
        destination_df_result['max_value'] = [row[8] for row in destination_result]
        destination_df_result['avg_value'] = [row[9] for row in destination_result]
        destination_df_result['stddev_pop_value'] = [row[10] for row in destination_result]
        destination_df_result['stddev_sample_value'] = [row[11] for row in destination_result]

        return source_df_result, destination_df_result
    except Exception as e:
        raise e


def line_by_line_validation(source: Source, destination: Destination, source_query: str, destination_query: str):
    try:
        result = validation_util.line_by_line_validation(source_query, destination_query, source, destination)
        source_df_result = pd.DataFrame()
        destination_df_result = pd.DataFrame()
        source_result = result['source_result']
        destination_result = result['destination_result']
        columns = result['columns']
        for index, value in enumerate(columns):
            source_df_result[value] = [row[index] for row in source_result]
            destination_df_result[value] = [row[index] for row in destination_result]

        return source_df_result, destination_df_result
    except Exception as e:
        raise e


def display_validation_result(source_df_result, destination_df_result):
    try:
        source_result, destination_result = st.columns(2)
        with source_result:
            st.text(st.session_state['src_connection'].name)
            st.table(source_df_result)
        with destination_result:
            st.text(st.session_state['destination_connection'].name)
            st.table(destination_df_result)
        if source_df_result.equals(destination_df_result):
            st.success(
                f'{st.session_state["src_connection"].name} result is equal with {st.session_state["destination_connection"].name} result')
        else:
            st.error(
                f'{st.session_state["src_connection"].name} result is not equal with {st.session_state["destination_connection"].name} result')
            diff_result = source_df_result.compare(destination_df_result, keep_shape=True, keep_equal=True,
                                                   result_names=(st.session_state['src_connection'].name,
                                                                 st.session_state[
                                                                     'destination_connection'].name))
            st.text('difference overview')
            st.table(diff_result)
            st.text('difference results')
            st.table(source_df_result.compare(destination_df_result,
                                              result_names=(st.session_state['src_connection'].name,
                                                            st.session_state[
                                                                'destination_connection'].name)))
    except Exception as e:
        raise e
