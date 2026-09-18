"""Dataset loader and validator module for DataPilot AI."""

from __future__ import annotations

import io
import os
from typing import Any, BinaryIO, Dict, Tuple, Union
import numpy as np
import pandas as pd


MAX_FILE_SIZE_MB = 100
WARN_ROW_COUNT = 50000


class DataLoaderError(Exception):
    """Custom exception for data loading and validation failures."""
    pass


def get_file_metadata(file_source: Union[str, BinaryIO, io.BytesIO], filename: str) -> Dict[str, Any]:
    """Inspects raw file size and extension before loading."""
    ext = os.path.splitext(filename)[1].lower()
    valid_extensions = {".csv", ".xlsx", ".xls"}
    if ext not in valid_extensions:
        raise DataLoaderError(f"Unsupported format '{ext}'. Only CSV, XLSX, and XLS files are supported.")

    size_bytes = 0
    if isinstance(file_source, str):
        if not os.path.exists(file_source):
            raise DataLoaderError(f"File not found: {file_source}")
        size_bytes = os.path.getsize(file_source)
    elif hasattr(file_source, "seek") and hasattr(file_source, "tell"):
        file_source.seek(0, os.SEEK_END)
        size_bytes = file_source.tell()
        file_source.seek(0)
    elif hasattr(file_source, "getbuffer"):
        size_bytes = len(file_source.getbuffer())

    size_mb = size_bytes / (1024 * 1024)
    if size_bytes == 0:
        raise DataLoaderError("The uploaded file is empty (0 bytes).")
    if size_mb > MAX_FILE_SIZE_MB:
        raise DataLoaderError(f"File size ({size_mb:.1f} MB) exceeds maximum allowed limit of {MAX_FILE_SIZE_MB} MB.")

    return {
        "filename": filename,
        "extension": ext,
        "size_bytes": size_bytes,
        "size_mb": round(size_mb, 2),
    }


def load_dataset(file_source: Union[str, BinaryIO, io.BytesIO], filename: str) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """Loads a dataset from CSV or Excel with robust error handling and validation."""
    meta = get_file_metadata(file_source, filename)
    ext = meta["extension"]

    df: pd.DataFrame
    try:
        if ext == ".csv":
            # Attempt default utf-8, fallback to latin-1 / iso-8859-1 for Windows-encoded CSVs
            try:
                if hasattr(file_source, "seek"):
                    file_source.seek(0)
                df = pd.read_csv(file_source, encoding="utf-8", low_memory=False)
            except UnicodeDecodeError:
                if hasattr(file_source, "seek"):
                    file_source.seek(0)
                df = pd.read_csv(file_source, encoding="latin-1", low_memory=False)
        elif ext in {".xlsx", ".xls"}:
            if hasattr(file_source, "seek"):
                file_source.seek(0)
            df = pd.read_excel(file_source)
        else:
            raise DataLoaderError(f"Unsupported extension: {ext}")
    except DataLoaderError:
        raise
    except Exception as e:
        raise DataLoaderError(f"Unable to parse file '{filename}': {str(e)}")

    if df.empty or len(df) == 0:
        raise DataLoaderError("The dataset contains 0 rows or is completely empty.")

    if len(df.columns) == 0:
        raise DataLoaderError("The dataset contains no columns.")

    # Clean column names (strip leading/trailing whitespace, keep string representation)
    df.columns = [str(c).strip() for c in df.columns]

    # Attempt smart datetime conversion for object columns that clearly represent dates
    for col in df.columns:
        if df[col].dtype == "object":
            # Check a non-null sample to avoid expensive parsing of pure text
            sample = df[col].dropna().head(20)
            if not sample.empty and sample.astype(str).str.contains(r"^\d{4}[-/]\d{1,2}[-/]\d{1,2}", regex=True).all():
                try:
                    df[col] = pd.to_datetime(df[col], errors="ignore")
                except Exception:
                    pass

    # Categorize column types
    num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    dt_cols = df.select_dtypes(include=["datetime", "datetimetz"]).columns.tolist()
    cat_cols = [c for c in df.columns if c not in num_cols and c not in dt_cols]

    mem_bytes = df.memory_usage(deep=True).sum()
    mem_mb = round(mem_bytes / (1024 * 1024), 2)

    summary = {
        "filename": filename,
        "extension": ext,
        "rows": int(len(df)),
        "columns": int(len(df.columns)),
        "memory_usage_mb": mem_mb,
        "memory_usage_human": f"{mem_mb} MB" if mem_mb >= 1.0 else f"{round(mem_bytes / 1024, 1)} KB",
        "num_numerical": len(num_cols),
        "num_categorical": len(cat_cols),
        "num_datetime": len(dt_cols),
        "numerical_cols": num_cols,
        "categorical_cols": cat_cols,
        "datetime_cols": dt_cols,
        "is_large_dataset": len(df) > WARN_ROW_COUNT,
    }

    return df, summary
