from radis.io import fetch_exomol
import numpy as np
COdb="Li2015"
dataframe = fetch_exomol("CO",database=COdb,engine="vaex")
print(np.unique(dataframe["airbrd"]))
