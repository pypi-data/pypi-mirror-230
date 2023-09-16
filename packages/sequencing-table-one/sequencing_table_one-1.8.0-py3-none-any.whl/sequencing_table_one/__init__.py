import os

import streamlit as st  
import pandas as pd

import streamlit.components.v1 as components

# Create a _RELEASE constant. We'll set this to False while we're developing
# the component, and True when we're ready to package and distribute it.
_RELEASE = True

if not _RELEASE:
    _sequencing_table_one = components.declare_component(
        "sequencing_table_one",
        url="http://localhost:3002",
    )
else:
    parent_dir = os.path.dirname(os.path.abspath(__file__))
    build_dir = os.path.join(parent_dir, "frontend/build")
    _sequencing_table_one = components.declare_component("sequencing_table_one", path=build_dir)


def sequencing_table_one(data, key=None,editable_cell=None,shape=None,colorable_cells=None,colorable_text=None,firstColumnWide=None,issequencingPage=None,timeframe=None):
    data = data.to_dict(orient='list') 
    return _sequencing_table_one(data=data, key=key, editable_cells=editable_cell,  colorable_cells=colorable_cells, shape=shape, colorable_text=colorable_text,firstColumnWide=firstColumnWide,issequencingPage=issequencingPage,timeframe=timeframe)



# Test code to play with the component while it's in development.
# During development, we can run this just as we would any other Streamlit
# app: `$ streamlit run custom_dataframe/__init__.py`
if not _RELEASE:
    # data = {
    #     "Category": ["CCF Regional Accrual", "CTM Local Accrual", "Flex", "Other", "DNNSI"],
    #     "Current": [0, 0, 0, 0, 0],
    #     "New Pricing": [0, 0, 0, 0, 0],
    #     "Change $": [0, 0, 0, 0, 0],
    #     "Change%": [0, 0, 0, 0, 0]
    # }
    data={'week': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52], 
          'holiday': ['', '', '', '', '', 'superbowl', '', '', '', '', '', '', 'easter', '', '', '', '', '', '', '', 'memorial_day', '', '', '', '', 'independence_day', '', '', '', '', '', '', '', '', 'labor_day', '', '', '', '', '', '', '', '', '', '', '', 'thanksgiving', '', '', '', 'christmas', ''],
          'swire_week': ['2024-01-05', '2024-01-12', '2024-01-19', '2024-01-26', '2024-02-02', '2024-02-09', '2024-02-16', '2024-02-23', '2024-03-01', '2024-03-08', '2024-03-15', '2024-03-22', '2024-03-29', '2024-04-05', '2024-04-12', '2024-04-19', '2024-04-26', '2024-05-03', '2024-05-10', '2024-05-17', '2024-05-24', '2024-05-31', '2024-06-07', '2024-06-14', '2024-06-21', '2024-06-28', '2024-07-05', '2024-07-12', '2024-07-19', '2024-07-26', '2024-08-02', '2024-08-09', '2024-08-16', '2024-08-23', '2024-08-30', '2024-09-06', '2024-09-13', '2024-09-20', '2024-09-27', '2024-10-04', '2024-10-11', '2024-10-18', '2024-10-25', '2024-11-01', '2024-11-08', '2024-11-15', '2024-11-22', '2024-11-29', '2024-12-06', '2024-12-13', '2024-12-20', '2024-12-31'], 
          'add_break': ['', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', ''], 
          'month': ['Jan', 'Jan', 'Jan', 'Jan', 'Feb', 'Feb', 'Feb', 'Feb', 'Mar', 'Mar', 'Mar', 'Mar', 'Mar', 'Apr', 'Apr', 'Apr', 'Apr', 'May', 'May', 'May', 'May', 'Jun', 'Jun', 'Jun', 'Jun', 'Jun', 'Jul', 'Jul', 'Jul', 'Jul', 'Aug', 'Aug', 'Aug', 'Aug', 'Sep', 'Sep', 'Sep', 'Sep', 'Sep', 'Oct', 'Oct', 'Oct', 'Oct', 'Nov', 'Nov', 'Nov', 'Nov', 'Dec', 'Dec', 'Dec', 'Dec', 'Dec'], 
          'retailer': ['bashas', 'bashas', 'bashas', 'bashas', 'bashas', 'bashas', 'bashas', 'bashas', 'bashas', 'bashas', 'bashas', 'bashas', 'bashas', 'bashas', 'bashas', 'bashas', 'bashas', 'bashas', 'bashas', 'bashas', 'bashas', 'bashas', 'bashas', 'bashas', 'bashas', 'bashas', 'bashas', 'bashas', 'bashas', 'bashas', 'bashas', 'bashas', 'bashas', 'bashas', 'bashas', 'bashas', 'bashas', 'bashas', 'bashas', 'bashas', 'bashas', 'bashas', 'bashas', 'bashas', 'bashas', 'bashas', 'bashas', 'bashas', 'bashas', 'bashas', 'bashas', 'bashas']
        }
    editable_cell = {
        "New Pricing":[0,1,2,3],
        }
    shape = {
        "no_rows": 5,
        "no_cols": 5,
        "width": "100%",
        "height": "200px",
        "landscape":"true"
    }
    colorable_cells  = {
    "Category": ["", "", "", "", ""],
    "Current": ["", "", "", "", ""],
    "New Pricing": ["rgb(255,229,180)", "rgb(255,229,180)", "rgb(255,229,180)", "rgb(255,229,180)", ""],
    "Change $": ["", "", "", "", ""],
    "Change%": ["", "", "", "", ""]
    }
    firstColumnWide={"isTrue":True,"width":"200px"}
    issequencingPage=True
    timeframe="Full Year"
    df2 = pd.DataFrame(data)
    df = sequencing_table_one(df2,key=2,editable_cell=editable_cell,shape= shape,colorable_cells=colorable_cells, colorable_text={},firstColumnWide=firstColumnWide,issequencingPage=issequencingPage,timeframe=timeframe)
    st.dataframe(df)