import pandas as pd
import random
import string

def generate_csv(index, n) -> string:
    data = []
    for _ in range(n):
        ct = random.choice('ABCD')
        v = random.uniform(0,9999)
        data.append({"Категория": ct, "Значение": v})
    df = pd.DataFrame(data)
    
    fn = f"f_{index}.csv"
    df.to_csv(fn,index=False)
    
    return fn