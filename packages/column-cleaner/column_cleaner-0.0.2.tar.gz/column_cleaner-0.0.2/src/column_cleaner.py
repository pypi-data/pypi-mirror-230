import pandas as pd
import re

def column_cleaner(data):
    data=data.dropna(how="all")
    def column_name(column):
        column =re.sub('[^a-zA-Z _]+', '', column)
        if column[0]==" " or column[0]=="_":
            column=column[1:]
        if column[-1]==" " or column[1]=="_":
            column=column[:-1]
        return(column)
    data.columns=list(pd.Series(data.columns).apply(lambda x: column_name(x)))
    data.columns=data.columns.str.replace(" ","_")
    return(data)
