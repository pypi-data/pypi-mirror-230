import shutil
import logging
import pandas as pd
from helper import *


class ExtractCols1:
    # file_path is an os.pathLIKE path
    def __init__(self, file_path, project):
        self.file_path = os.path.abspath(file_path)
        self.excel_file = pd.ExcelFile(file_path)
        self.config_data = read_config("config.yaml")

        self.customer = os.path.basename(os.path.dirname(file_path))
        self.extract_rule = self.config_data[project]["extract_rule"][self.customer]

        self.fetch_out_path = os.path.abspath(self.config_data[project]["fetch_attachment_path"])
        self.out_path = self.config_data[project]["out_path"]
        self.out_file_name_rule = self.extract_rule["out_file_name_rule"]
        self.code = self.out_file_name_rule["code"]
        self.cname = self.out_file_name_rule["cname"]
        self.static_name = self.out_file_name_rule["static_name"]

    # transfer Excel file into dataframe
    # we can get all direct df which header is the 1st row and all data is from 2nd row
    # return: df_purchase, df_sale, df_inv (df will be set None if not matched)
    def get_df_from_excel_file(self):
        # read values will be used
        filetype = self.extract_rule["filetype"]

        purchase_sheet_index = self.extract_rule["purchase"]["sheet_index"]
        inv_sheet_index = self.extract_rule["inv"]["sheet_index"]
        sale_sheet_index = self.extract_rule["sale"]["sheet_index"]

        purchase_header = self.extract_rule["header_index"]
        inv_header = self.extract_rule["header_index"]
        sale_header = self.extract_rule["header_index"]

        purchase_keywords = self.extract_rule["purchase_keywords"]
        sale_keywords = self.extract_rule["sale_keywords"]
        inv_keywords = self.extract_rule["inv_keywords"]

        # initialize 3 df
        df_purchase = None
        df_sale = None
        df_inv = None

        # 如果类型为单文件单sheet或者单文件多sheet，就通过sheet_index来读
        flag = False
        if filetype == "single":
            for keyword in purchase_keywords:
                if keyword in self.file_path:
                    df_purchase = pd.read_excel(self.excel_file, sheet_name=purchase_sheet_index, header=purchase_header)
                    flag = True
            for keyword in sale_keywords:
                if keyword in self.file_path:
                    df_sale = pd.read_excel(self.excel_file, sheet_name=sale_sheet_index, header=sale_header)
                    flag = True
            for keyword in inv_keywords:
                if keyword in self.file_path:
                    df_inv = pd.read_excel(self.excel_file, sheet_name=inv_sheet_index, header=inv_header)
                    flag = True
            if flag:
                logging.info(f"extract failed, file name: {self.file_path}")


        elif filetype == "3in1excel":
            df_purchase = pd.read_excel(self.excel_file, sheet_name=purchase_sheet_index, header=purchase_header)
            df_inv = pd.read_excel(self.excel_file, sheet_name=inv_sheet_index, header=inv_header)
            df_sale = pd.read_excel(self.excel_file, sheet_name=sale_sheet_index, header=sale_header)
            # 类型是3in1的时候，需要筛选数据进行拆分
            df_purchase, df_sale, df_inv = self.select_data(df_purchase, df_sale, df_inv)

        elif filetype == "3in1sheet":
            sheet_names = self.excel_file.sheet_names
            for keyword in purchase_keywords:
                if keyword in sheet_names:
                    df_purchase = pd.read_excel(self.excel_file, sheet_name=purchase_sheet_index, header=purchase_header)
            for keyword in sale_keywords:
                if keyword in sheet_names:
                    df_inv = pd.read_excel(self.excel_file, sheet_name=inv_sheet_index, header=inv_header)
            for keyword in inv_keywords:
                if keyword in sheet_names:
                    df_sale = pd.read_excel(self.excel_file, sheet_name=sale_sheet_index, header=sale_header)

        return df_purchase, df_sale, df_inv

    def drop_rows(self, df):
        rows_to_dropped = self.extract_rule["drop_row_index"]
        # drop rows from rows_to_dropped, rows_to_dropped should be an index of data (under header row)
        if df is not None and rows_to_dropped is not None:
            if len(rows_to_dropped) > 0:
                df = df.drop(rows_to_dropped)

        return df

    def get_rows(self, df):
        get_data_rows_mode = self.extract_rule["get_data_rows_mode"]
        get_data_rows_param = self.extract_rule["get_data_rows_param"]
        # get rows by 4 modes
        if df is not None:
            if get_data_rows_mode == "single":
                if len(get_data_rows_param) > 0:
                    df = df.iloc[get_data_rows_param]
            if get_data_rows_mode == "single-area":
                if len(get_data_rows_param) == 2:
                    df = df.iloc[get_data_rows_param[0], get_data_rows_param[1]]
            if get_data_rows_mode == "multi-area":
                temp_df_list = []
                if len(get_data_rows_param) > 0:
                    for item in get_data_rows_param:
                        if len(item) == 2:
                            temp_df = df.iloc[get_data_rows_param[0], get_data_rows_param[1]]
                            temp_df_list.append(temp_df)
                df = pd.concat(temp_df_list, axis=0)
            # default mode all or None
            elif get_data_rows_mode == "all" or get_data_rows_mode is None:
                df = df
        return df

    def drop_noise_rows(self, df):
        drop_noise_rows = self.extract_rule["drop_noise_rows"]["index"]
        if df is not None:
            if len(drop_noise_rows) > 0:
                for item in drop_noise_rows:
                    df = df[~(df.iloc[:, item].isna())]
        else:
            df = df
        return df

    def add_columns(self, df):
        insert_cols_index = self.extract_rule["insert_cols_index"]
        insert_cols_header = self.extract_rule["insert_cols_header"]
        insert_cols_num = self.extract_rule["insert_cols_num"]
        if df is not None and insert_cols_index is not None and insert_cols_header is not None and insert_cols_num is not None:
            for i in range(insert_cols_num):
                col_name = insert_cols_header[i]
                df.insert(insert_cols_index, col_name, None)
        else:
            df = df

        return df

    def select_data(self, df_purchase, df_sale, df_inv):
        purchase_filter_index = self.extract_rule["purchase"]["data_filter"]["filter_index"]
        sale_filter_index = self.extract_rule["sale"]["data_filter"]["filter_index"]
        inv_filter_index = self.extract_rule["inv"]["data_filter"]["filter_index"]

        purchase_filter_ = self.extract_rule["purchase"]["data_filter"]["filter_content"]
        sale_filter_ = self.extract_rule["sale"]["data_filter"]["filter_content"]
        inv_filter_ = self.extract_rule["inv"]["data_filter"]["filter_content"]

        purchase_filtered_df = pd.DataFrame()
        sale_filtered_df = pd.DataFrame()
        inv_filtered_df = pd.DataFrame()

        if df_purchase is not None:
            if len(purchase_filter_index) > 0 and len(purchase_filter_index) > 0:
                for index, row in df_purchase.iterrows():
                    all_conditions_met = True
                    for col_index, filter_text in zip(purchase_filter_index, purchase_filter_):
                        col_value = str(row[df_purchase.columns[col_index]]).lower()
                        condition_met = col_value.find(filter_text.lower()) != -1
                        if not condition_met:
                            all_conditions_met = False
                            break
                    if all_conditions_met:
                        df_purchase = purchase_filtered_df._append(row, ignore_index=True)
            else:
                df_purchase = df_purchase
        if df_sale is not None:
            if len(sale_filter_index) > 0 and len(sale_filter_index) > 0:
                for index, row in df_sale.iterrows():
                    all_conditions_met = True
                    for col_index, filter_text in zip(sale_filter_index, sale_filter_):
                        col_value = str(row[df_sale.columns[col_index]]).lower()
                        condition_met = col_value.find(filter_text.lower()) != -1
                        if not condition_met:
                            all_conditions_met = False
                            break
                    if all_conditions_met:
                        df_sale = sale_filtered_df._append(row, ignore_index=True)
        else:
            df_sale = df_sale
        if df_inv is not None:
            if len(inv_filter_index) > 0 and len(inv_filter_index) > 0:
                for index, row in df_inv.iterrows():
                    all_conditions_met = True
                    for col_index, filter_text in zip(inv_filter_index, inv_filter_):
                        col_value = str(row[df_inv.columns[col_index]]).lower()
                        condition_met = col_value.find(filter_text.lower()) != -1
                        if not condition_met:
                            all_conditions_met = False
                            break
                    if all_conditions_met:
                        df_inv = inv_filtered_df._append(row, ignore_index=True)
        else:
            df_inv = df_inv

        return df_purchase, df_sale, df_inv

    def pre_process(self, purchase_df, sale_df, inv_df):
        purchase_df = self.drop_rows(purchase_df)
        purchase_df = self.get_rows(purchase_df)
        purchase_df = self.drop_noise_rows(purchase_df)
        purchase_df = self.add_columns(purchase_df)

        sale_df = self.drop_rows(sale_df)
        sale_df = self.get_rows(sale_df)
        sale_df = self.drop_noise_rows(sale_df)
        sale_df = self.add_columns(sale_df)

        inv_df = self.drop_rows(inv_df)
        inv_df = self.get_rows(inv_df)
        inv_df = self.drop_noise_rows(inv_df)
        inv_df = self.add_columns(inv_df)

        return purchase_df, sale_df, inv_df

    def extract(self, df_purchase, df_sale, df_inv):
        sale_headers = self.extract_rule["sale"]["headers"]
        inv_headers = self.extract_rule["inv"]["headers"]
        purchase_headers = self.extract_rule["purchase"]["headers"]
        sale_cols = self.extract_rule["sale"]["cols"]
        inv_cols = self.extract_rule["inv"]["cols"]
        purchase_cols = self.extract_rule["purchase"]["cols"]

        if df_sale is not None and max(sale_cols) < df_sale.shape[1]:
            df_sale = df_sale.iloc[:, sale_cols]
            df_sale.columns = sale_headers

        if df_inv is not None and max(inv_cols) < df_inv.shape[1]:
            df_inv = df_inv.iloc[:, inv_cols]
            df_inv.columns = inv_headers

        if df_purchase is not None and max(purchase_cols) < df_purchase.shape[1]:
            df_purchase = df_purchase.iloc[:, purchase_cols]
            df_purchase.columns = purchase_headers

        return df_purchase, df_sale, df_inv

    def df_to_excel(self, df, type):
        extension = self.file_path.lower().split(".")[-1]
        out_father_path = os.path.abspath(os.path.join(self.out_path, self.customer))
        os.makedirs(out_father_path, exist_ok=True)
        if df is not None and type is not None:
            name = type + "-" + str(self.code) + "-" + self.cname + "-" + self.static_name + "." + extension
            if extension == "xlsx":
                df.to_excel(os.path.join(out_father_path, name), engine='xlsxwriter', index=False)
            else:
                df.to_excel(os.path.join(out_father_path, name), engine='xlwt', index=False)

    def execute(self):
        df_purchase, df_sale, df_inv = self.get_df_from_excel_file()
        df_purchase, df_sale, df_inv = self.pre_process(df_purchase, df_sale, df_inv)
        df_purchase, df_sale, df_inv = self.select_data(df_purchase, df_sale, df_inv)
        df_purchase, df_sale, df_inv = self.extract(df_purchase, df_sale, df_inv)

        if df_purchase is not None:
            self.df_to_excel(df_purchase, "PD")
            logging.info(f"extract successful, file name: {self.file_path}")
        if df_sale is not None:
            self.df_to_excel(df_sale, "SD")
            logging.info(f"extract successful, file name: {self.file_path}")
        if df_inv is not None:
            self.df_to_excel(df_inv, "ID")
            logging.info(f"extract successful, file name: {self.file_path}")

        self.excel_file.close()
        handled_path = os.path.join(self.fetch_out_path, self.customer, "handled")
        os.makedirs(handled_path, exist_ok=True)
        try:
            shutil.move(self.file_path, handled_path)
        except Exception as e:
            print(e)









