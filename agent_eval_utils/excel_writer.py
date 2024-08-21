import openpyxl


class ExcelWriter:
    def write_excel(self, file_path, headers, data):
        workbook = openpyxl.Workbook()
        sheet = workbook.active

        sheet.append(headers)

        for row_data in data:
            row = [row_data.get(header, None) for header in headers]
            sheet.append(row)

        workbook.save(file_path)
        print(f"Excel file saved to {file_path}")

