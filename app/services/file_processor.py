import pandas as pd
import re
from typing import List
from fastapi import UploadFile, HTTPException


async def process_file(file: UploadFile) -> List[str]:

    if not file.filename:
        raise HTTPException(status_code=400, detail="File has no name")

    if file.filename.endswith(".csv"):
        df = pd.read_csv(file.file)
    elif file.filename.endswith((".xls", ".xlsx")):
        df = pd.read_excel(file.file)
    else:
        raise HTTPException(status_code=400, detail="Unsupported file type")

    if df.empty:
        raise HTTPException(status_code=400, detail="Uploaded file is empty")

    companies = (
        df.iloc[:, 0]
        .dropna()
        .astype(str)
        .str.lower()
        .str.strip()
        .apply(lambda x: re.sub(r"[^\w\s]", "", x))
        .drop_duplicates()
        .tolist()
    )

    return companies
