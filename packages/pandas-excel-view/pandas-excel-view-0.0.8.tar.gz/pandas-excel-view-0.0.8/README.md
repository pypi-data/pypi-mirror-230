## Install
<code>
python -m pip install git+https://github.com/wilianzilv/pandas-excel-view
</code>

## Usage
<code>
import pandas_excel_view as pdv
</code>

<br/>
<code>
pdv.show(df)
</code>


## Multiple Sheets
<code>
pdv.show(df1, "lorem")

pdv.show(df2, "ipsum")
</code>

## Multiple Workbooks
<code>
from pandas_excel_view import PandasExcelView
</code>

<br/>
<code>
pdv0 = PandasExcelView()

pdv1 = PandasExcelView()
</code>



