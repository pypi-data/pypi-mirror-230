import os
import datetime
import openpyxl


class ExcelGenerator:
    def __init__(self, data_list, header_dict):
        self.data_list = data_list
        self.header_dict = header_dict

    def generate_excel(self, filename):
        # 创建目录
        directory = os.path.dirname(filename)
        os.makedirs(directory, exist_ok=True)

        workbook = openpyxl.Workbook()
        sheet = workbook.active

        # 写入表头
        header_row = []
        for header_key in self.header_dict.keys():
            header_row.append(self.header_dict[header_key])
        sheet.append(header_row)

        # 写入数据
        for data_dict in self.data_list:
            data_row = []
            for header_key in self.header_dict.keys():
                search_key = data_dict.get(header_key)
                if search_key is not None:
                    data_row.append(search_key)
                else:
                    data_row.append("")  # 缺失数据的占位符
            sheet.append(data_row)

        # 保存工作簿
        workbook.save(filename)
        return filename


# Example usage
# data = [
#     {"Name": "Alice", "Age": 25, "Country": "USA"},
#     {"Name": "Bob", "Age": 30, "Country": "Canada"},
#     {"Name": "Charlie", "Age": 28, "Country": "UK"}
# ]
#
# header = {
#     "Name": "姓名",
#     "Age": "年龄",
#     "Country": "国家"
# }
#
# excel_generator = ExcelGenerator(data, header)
# excel_generator.generate_excel("output.xlsx")
