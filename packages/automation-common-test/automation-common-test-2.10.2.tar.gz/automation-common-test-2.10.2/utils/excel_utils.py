import pandas as pd
from helpers.web_operations import logger

def get_excel_data_from_column(file_path, sheet_name, target_column):
    xl = pd.ExcelFile(file_path)
    if sheet_name in xl.sheet_names:
        df = xl.parse(sheet_name)
    else:
        (f'Sheet {sheet_name} does not exist in the Excel file')
        return None
    if target_column in df.columns:
        return df[target_column].values.tolist()
    else:
        logger.info(f'Column {target_column} does not exist in the Excel file')
        return None


def get_excel_data_object(file_path, sheet_name):
    xl = pd.ExcelFile(file_path)
    if sheet_name in xl.sheet_names:
        df = xl.parse(sheet_name)
    else:
        logger.info(f'Sheet {sheet_name} does not exist in the Excel file')
        return None
    data_dict = df.to_dict('list')
    return data_dict


def extract_excel_data_from_row(filename, sheet_name, search_value):
    df = pd.read_excel(filename, sheet_name=sheet_name, skiprows=1)
    logger.info(f"Searching for: {search_value}")
    extracted_data = {}
    for i, row in df.iterrows():
        for j, value in enumerate(row):
            if value == search_value:
                logger.info(
                    f"Found {search_value} at row {i + 2}, column {j + 1}") 
                data_to_right = row.iloc[j + 1:].tolist()
                extracted_data[search_value] = data_to_right
    if extracted_data:
        return extracted_data
    else:
        logger.info(f"{search_value} not found in the Excel sheet.")
        return None


