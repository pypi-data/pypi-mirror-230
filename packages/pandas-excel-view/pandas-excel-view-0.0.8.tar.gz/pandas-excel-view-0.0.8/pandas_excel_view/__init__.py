#%%

import datetime

def dispatch(app_name:str):
    try:
        from win32com import client
        app = client.gencache.EnsureDispatch(app_name)
    except AttributeError:
        # Corner case dependencies.
        import os
        import re
        import sys
        import shutil
        # Remove cache and try again.
        MODULE_LIST = [m.__name__ for m in sys.modules.values()]
        for module in MODULE_LIST:
            if re.match(r'win32com\.gen_py\..+', module):
                del sys.modules[module]
        shutil.rmtree(os.path.join(os.environ.get('LOCALAPPDATA'), 'Temp', 'gen_py'))
        from win32com import client
        app = client.gencache.EnsureDispatch(app_name)
    return app

class PandasExcelView:

    def __init__(self, workbook_name='Python'):
        self.__real_workbook_name = None
        self.workbook_name = workbook_name

    def __ensure_workbook(self):
        # Abre o excel se não estiver aberto
        excel = dispatch('Excel.Application')
        try:
            excel.Visible = True
        except:
            pass

        self.excel = excel

        # Checa se o workbook já está aberto
        if self.__real_workbook_name:
            for i in range(1, excel.Workbooks.Count + 1):
                _wb = excel.Workbooks(i)
                if _wb.Name == self.__real_workbook_name:
                    self.wb = _wb
                    return

        # Cria um novo workbook
        wb = excel.Workbooks.Add()
        self.__real_workbook_name = wb.Name
        wb.Name = self.workbook_name
        self.wb = wb

    def __get_last_sheet(self):
        return self.wb.Sheets(self.wb.Sheets.Count)

    def __validate_sheet_name(self, sheet_name):
        if isinstance(sheet_name, str):
            if len(sheet_name) > 0:
                return True

        return False

    def __sanitize_dataframe(self, df):
        df = df.copy()
        df = df.fillna('')
        date_columns = df.select_dtypes(include=['datetime64', datetime.date, datetime.datetime]).columns.tolist()
        df[date_columns] = df[date_columns].astype(str)
        return df

    def show(self, df, sheet_name=None):

        self.__ensure_workbook()
        valid_sheet_name = self.__validate_sheet_name(sheet_name)

        x = 1
        y = 1

        ws = None
        if not valid_sheet_name:
            ws = self.__get_last_sheet()
        else:
            for i in range(1, self.wb.Sheets.Count + 1):
                _ws = self.wb.Sheets(i)
                if _ws.Name == sheet_name:
                    ws = _ws

            if not ws:
                ws = self.wb.Sheets.Add()
                ws.Name = sheet_name


        df = self.__sanitize_dataframe(df)

        cols_count = len(df.columns)
        rows_count = len(df.index)

        ws.Cells.Clear()

        if cols_count:
            ws.Range(ws.Cells(y, x), ws.Cells(y, x + cols_count - 1)).Value = tuple(df.columns)

        if rows_count:
            ws.Range(ws.Cells(y + 1, x), ws.Cells(y + rows_count, x + cols_count - 1)).Value = df.values
            ws.Columns.AutoFit()


            rng = ws.Range(ws.Cells(y, x), ws.Cells(y + rows_count, x + cols_count - 1))#

            obj = ws.ListObjects.Add(SourceType=1, Source=rng)
            try:
                obj.TableStyle = "BlueTableStyleMedium16"
            except:
                pass
            if sheet_name:
                try:
                    obj.Name = sheet_name
                except:
                    pass

        ws.Activate()

        self.focus()

    def focus(self):
        try:
            import pygetwindow as gw

            w = gw.getWindowsWithTitle(f'{self.wb.Name} - Excel')
            if len(w):
                w[0].activate()
                w[0].restore()
        except:
            pass


pdv = PandasExcelView()
show = pdv.show

