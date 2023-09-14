import uuid
from datetime import datetime

from migration.connector.source.enum import Column

from migration.connector.destination.base import Destination

from migration.connector.source import Source

NUMBER_TYPE = ['BIGINT', 'DECIMAL', 'DOUBLE', 'FLOAT', 'INT', 'SMALLINT', 'TINYINT']
LEFT_BRACKET = '('


def is_number_type(self, column: Column, type_mapping: dict) -> bool:
    if LEFT_BRACKET in column.type:
        column_type = column.type.split(LEFT_BRACKET)[0]
        return type_mapping.get(column_type, column_type) in NUMBER_TYPE

    return type_mapping.get(column.type, column.type) in NUMBER_TYPE


def create_query_result_table(source: Source, destination: Destination, query: str) -> str:
    temp_db = 'validation_query_result_db'
    temp_table = f"validation_query_result_table_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
    if source.name == 'clickzetta' or destination.name == 'clickzetta':
        source.execute_sql(f"create schema if not exists {temp_db}")
    else:
        source.execute_sql(f"create database if not exists {temp_db}")
    source.execute_sql(f"drop table if exists {temp_db}.{temp_table}")
    source.execute_sql(f"create table {temp_db}.{temp_table} as {query}")
    destination.execute_sql(f"create database if not exists {temp_db}")
    destination.execute_sql(f"drop table if exists {temp_db}.{temp_table}")
    destination.execute_sql(f"create table {temp_db}.{temp_table} as {query}")
    return f"{temp_db}.{temp_table}"


def basic_validation(source: Source, destination: Destination, query: str):
    try:
        tbl_name = create_query_result_table(source, destination, query)
        count_sql = f"select count(*) from {tbl_name}"
        source_count_res = source.execute_sql(count_sql)[0]
        result = {'source_count': source_count_res[0]}
        destination_count_res = destination.execute_sql(count_sql)[0]
        result['destination_count'] = destination_count_res[0]
        type_mapping = source.type_mapping()
        table_columns = source.get_table_columns(tbl_name)
        for column in table_columns:
            if is_number_type(column, type_mapping):
                sql = f"select min({column.name}), max({column.name}), avg({column.name}) from {tbl_name}"
                source_result = source.execute_sql(sql)[0]
                result[f'{column.name}_source_min'] = source_result[0]
                result[f'{column.name}_source_max'] = source_result[1]
                result[f'{column.name}_source_avg'] = source_result[2]
                destination_result = destination.execute_sql(sql)[0]
                result[f'{column.name}_destination_min'] = destination_result[0]
                result[f'{column.name}_destination_max'] = destination_result[1]
                result[f'{column.name}_destination_avg'] = destination_result[2]
        return result
    except Exception as e:
        raise Exception(e)


def construct_profiling_sql(tbl_name: str, source: Source, type_mapping):
    table_columns = source.get_table_columns(tbl_name)
    profile_sql = f"with source_data data as (select * from {tbl_name}), \n" \
                  f"column_profiles  as ( \n"
    for index, column in enumerate(table_columns):
        profile_sql += f"select '{column.name}' as column_name, \n" \
                       f"'{column.type}' as column_type, \n" \
                       f"count(*) as row_count, \n" \
                       f"sum(case when {column.name} is null then 0 else 1 end) / count(*) as not_null_proportion,\n" \
                       f"count(distinct {column.name}) / count(*) as distinct_proportion, \n" \
                       f"count(distinct {column.name}) as distinct_count, \n" \
                       f"count(distinct {column.name}) = count(*) as is_unique, \n"
        if is_number_type(column, type_mapping):
            profile_sql += f"min({column.name}) as min_value, \n" \
                           f"max({column.name}) as max_value, \n" \
                           f"avg({column.name}) as avg_value \n" \
                           f"stddev_pop({column.name}) as stddev_pop_value \n" \
                           f"stddev_sample({column.name}) as stddev_sample_value \n"
        else:
            profile_sql += f"null as min_value, \n" \
                           f"null as max_value, \n" \
                           f"null as avg_value \n" \
                           f"null as stddev_pop_value \n" \
                           f"null as stddev_sample_value \n"
        profile_sql += f"from source_data \n"
        if index != len(table_columns) - 1:
            profile_sql += f"union all \n"
    profile_sql += f") \n" \
                   f"select * from column_profiles;"
    return profile_sql


def multidimensional_validation(source: Source, destination: Destination, query: str):
    try:
        tbl_name = create_query_result_table(source, destination, query)
        type_mapping = source.type_mapping()
        profile_sql = construct_profiling_sql(tbl_name, source, type_mapping)
        source_profile_result = source.execute_sql(profile_sql)
        destination_profile_result = destination.execute_sql(profile_sql)
        result = {'source_profile_result': source_profile_result,
                  'destination_profile_result': destination_profile_result}
        return result
    except Exception as e:
        raise Exception(e)


def line_by_line_validation(query: str, source: Source, destination: Destination):
    try:
        tbl_name = create_query_result_table(source, destination, query)
        source_result = source.execute_sql(f"select * from {tbl_name}")
        destination_result = destination.execute_sql(f"select * from {tbl_name}")
        result = {'source_result': source_result,
                  'destination_result': destination_result}
        return result
    except Exception as e:
        raise Exception(e)
