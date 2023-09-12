import csv
import io
import pyexcel

from typing import List, Dict, Any, OrderedDict

from filum_utils.config import config


class FileService:
    @classmethod
    def get_rows(
        cls,
        file_name: str,
        file_content_bytes: bytes,
        current_index: int,
        limit: int = config.FILE_RECORD_LIMIT
    ) -> List[Dict[str, Any]]:
        rows = cls.get_file_data(file_name, file_content_bytes)
        start_row = current_index
        end_row = start_row + limit

        # prevent getting more rows than total of rows in uploaded file
        if end_row > len(rows):
            end_row = len(rows)

        if start_row == end_row:
            return []

        processed_rows = []
        for i in range(start_row, end_row):
            processed_row = dict(rows[i])
            processed_rows.append(processed_row)

        return processed_rows

    @classmethod
    def get_file_data(cls, file_name: str, file_content_bytes: bytes) -> List[Dict[str, Any]]:
        file_extension = cls._get_file_extension(file_name)
        if file_extension == "csv":
            return cls._get_csv_file_data(file_content_bytes, file_extension)

        if file_extension in ["xlsx", "xls"]:
            return cls._get_excel_file_data(file_content_bytes, file_extension)

        return []

    @classmethod
    def _get_csv_file_data(cls, file_content_bytes: bytes, file_extension: str) -> List[Dict[str, Any]]:
        file_content_bytes = file_content_bytes.decode("utf-8-sig")
        records = csv.DictReader(file_content_bytes.splitlines(), skipinitialspace=True, delimiter=",")
        rows = []

        for record in records:
            rows.append(record)

        return rows

    @classmethod
    def _get_excel_file_data(cls, file_content_bytes: bytes, file_extension: str) -> List[OrderedDict]:
        return pyexcel.get_records(
            file_content=io.BytesIO(file_content_bytes),
            file_type=file_extension,
            name_columns_by_row=0
        )

    @staticmethod
    def _get_file_extension(file_name: str):
        string_list = file_name.split(".")
        return string_list[len(string_list) - 1]
