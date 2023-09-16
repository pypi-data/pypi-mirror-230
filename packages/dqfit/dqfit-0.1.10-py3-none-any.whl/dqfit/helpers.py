## DRAFT

import pandas as pd


def time_horizon_matrix(min_date: str, key: str = "Recent") -> pd.DataFrame:
    df = pd.DataFrame()
    df["Date"] = pd.date_range(start=min_date, end="today", freq="D").astype(str)
    df = df.reset_index()
    df[key] = df["index"].apply(lambda x: x / df["index"].max())
    return df[["Date", key]]


def get_date(dim: pd.Series) -> str:
    # WIP: context
    TIME_PATHS = [
        "Procedure.performed[x]",
        "Condition.onset[x]",
        "Condition.abatement[x]",
        "Observation.effective[x]",
    ]

    val = dim.get("value", None)
    if dim["path"] not in TIME_PATHS:
        return None
    try:
        if isinstance(val, dict):
            if val.get("start"):
                return val["start"][0:10]
            if val.get("end"):
                return val["end"][0:10]
        else:
            return val[0:10]
    except Exception as e:
        print(e)
        print(val)
