import pandas as pd
from google.colab import auth

auth.authenticate_user()

import gspread
from google.auth import default

creds, _ = default()

gc = gspread.authorize(creds)


def read_google_spreadsheet(spreadsheet_filename: str):
    """Input spreadsheet name. Return as gc spreadsheet"""
    return gc.open(spreadsheet_filename)


def list_all_worksheets(spreadsheet_filename: str):
    """Input spreadsheet name. Return list of all worksheet titles"""
    sh = read_google_spreadsheet(spreadsheet_filename)
    worksheet_objs = sh.worksheets()
    return [wksheet.title for wksheet in worksheet_objs]


def read_google_worksheet(spreadsheet_filename: str, worksheet_name: str):
    """Input name of spreadsheet and worksheet name. Return google worksheet"""
    sh = read_google_spreadsheet(spreadsheet_filename)
    gc_worksheet = sh.worksheet(worksheet_name)
    return gc_worksheet


#### main functions we will probably use
def worksheet_to_dataframe(spreadsheet_filename: str, worksheet_name: str):
    """Input spreadsheet and worksheet names. Transform and return as dataframe"""
    worksheet = read_google_worksheet(spreadsheet_filename, worksheet_name)
    values_list = worksheet.get_all_values()
    df = pd.DataFrame(values_list).fillna("")
    df.columns = df.iloc[0]
    return df.drop(df.index[0])


def update_google_worksheet_from_df(worksheet: gspread.Worksheet, df: pd.DataFrame):
    """Input google worksheet and pandas dataframe. Update current worksheet with dataframe
    contents and save directly to the file"""
    return worksheet.update([df.columns.values.tolist()] + df.values.tolist())
