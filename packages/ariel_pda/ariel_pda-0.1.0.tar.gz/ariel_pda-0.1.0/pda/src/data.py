import pandas as pd
from pda import constants

df= pd.DataFrame([('a',2),('b',None),(constants.MY_VAR,10)],
                 columns=['col_a','col_B']
                 )

print(df)