import os
import json
import logging

import openai
import pandas as pd
from dotenv import load_dotenv


load_dotenv()


# Using Code Llama2 on Anyscale Endpoints
openai.api_base = os.getenv("OPENAI_API_BASE")
openai.api_key = os.getenv("OPENAI_API_KEY")
MODEL_NAME="codellama/CodeLlama-34b-Instruct-hf"


logger = logging.getLogger(__name__)


def generate_readable_variable_name(*, variable_name: str) -> str:

    system_prompt = """You are an expert in data management and administration in a large enterprise setting. You have a very deep understanding of data and the common naming schemes of the data and what they means. If you are not confident of generating a good name, give an empty string instead. Please respond the query in a JSON format with the fields "variable_name" from input and "readable_name" as the output."""

    user_prompt = f"Translate this database column name '{variable_name}' into readable English."

    response = openai.ChatCompletion.create(
        model="codellama/CodeLlama-34b-Instruct-hf",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}],
        temperature=0.01,
        stream=False
    )
    message = response["choices"][0]['message']['content']
    message_json = json.loads(message)

    return message_json['readable_name']


def generate_variable_definition(*, variable_name: str) -> str:

    system_prompt = """You are an expert in data management and administration in a large enterprise setting. You have a very deep understanding of data and the common naming schemes of the data and what they means. If you are not confident of generating a good response, give an empty string instead.
    
    Please respond the query in a JSON format with the fields "variable_name" from input and "definition" as the output."""

    user_prompt = f"Translate this database column name '{variable_name}' into a definition in Genus-Differentia form: A is a B that C."

    response = openai.ChatCompletion.create(
        model="codellama/CodeLlama-34b-Instruct-hf",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}],
        temperature=0.01,
        stream=False
    )
    message = response["choices"][0]['message']['content']
    message_json = json.loads(message)

    return message_json['definition']


def infer_data_type(*, unique_values: list) -> str:

    system_prompt = """You are an expert in data management and administration in a large enterprise setting. You have a very deep understanding of data and the common naming schemes of the data and what they means. Please provide answers directly without any explaination. If you are not confident of generating a good response, give an empty string instead."""

    user_prompt = f"Using these sampels of unique values of a database column, please report back the SQL data type of the column. Make your best judgement. The unique values of the column is as follows: '{unique_values}'. Please respond in JSON format with the field 'data_type' as the response. The `data_type` value should be fully capitalized if it is a SQL data type."

    response = openai.ChatCompletion.create(
        model="codellama/CodeLlama-34b-Instruct-hf",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}],
        temperature=0.01,
        stream=False
    )
    message = response["choices"][0]['message']['content']
    try:
        message_json = json.loads(message)
    except Exception as e:
        print(message)
        raise e

    return message_json['data_type']


def gpt_data_dictionary(*, csv_file: str) -> pd.DataFrame:
    df = pd.read_csv(csv_file)
    df = df.where(pd.notnull(df), None)

    data_dict = {
        'Variable Names': [],
        'Readable Variable Name': [],
        'Data Types': [],
        'Allowed Values': [],
        'Definition of the Variable': []
    }

    for col in df.columns:
        logger.info(f"Generating data dictionary for column: {col}")
        variable_name = col
        data_dict['Variable Names'].append(variable_name)
        data_dict['Readable Variable Name'].append(
            generate_readable_variable_name(variable_name=variable_name)
        )
        data_dict['Definition of the Variable'].append(
            generate_variable_definition(variable_name=variable_name)
        )

        col_dtype = str(df[col].dtype)
        
        if col_dtype in ['int64', 'float64']:
            data_dict['Data Types'].append("Numeric") 
            min_val = df[col].min()
            max_val = df[col].max()
            allowed_values = f"Range: {min_val} to {max_val}"
        elif col_dtype == 'object':
            unique_values = df[col].unique()
            allowed_values = f"Unique Values: {unique_values[:10]}..." if len(unique_values) > 10 else f"Unique Values: {unique_values}"

            max_length = max((len(str(v)) for v in unique_values), default=0)
            data_type = infer_data_type(unique_values=unique_values[:10]) or "Categorical"
            data_dict['Data Types'].append(data_type+f"({max_length})")


        data_dict['Allowed Values'].append(allowed_values)
    
    data_dict_df = pd.DataFrame(data_dict)
    return data_dict_df
