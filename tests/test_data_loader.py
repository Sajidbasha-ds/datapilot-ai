"""Unit tests for src/data_loader.py."""

import io
import pytest
import pandas as pd
from src.data_loader import load_dataset, get_file_metadata, DataLoaderError


def test_load_valid_csv():
    csv_content = io.BytesIO(b"id,age,salary\n1,25,50000\n2,30,65000\n3,35,80000\n")
    df, summary = load_dataset(csv_content, "test.csv")
    assert len(df) == 3
    assert summary["rows"] == 3
    assert summary["columns"] == 3
    assert "age" in summary["numerical_cols"]


def test_unsupported_file_extension():
    fake_file = io.BytesIO(b"some binary content")
    with pytest.raises(DataLoaderError, match="Unsupported format"):
        load_dataset(fake_file, "data.pdf")


def test_empty_dataset():
    empty_csv = io.BytesIO(b"")
    with pytest.raises(DataLoaderError, match="empty"):
        load_dataset(empty_csv, "empty.csv")


def test_mixed_types_no_crash():
    mixed_csv = io.BytesIO(b"id,mixed_col\n1,100\n2,text_value\n3,200\n")
    df, summary = load_dataset(mixed_csv, "mixed.csv")
    assert len(df) == 3
    assert "mixed_col" in summary["categorical_cols"]
