import subprocess
from pathlib import Path
from typing import Dict, Any, Literal

from langchain.tools import tool
import pandas as pd


@tool
def fastq2fasta(
    input_file: str,
    output_file: str,
    line_width: int = 60,
    threads: int = 4,
    compress: bool = False,
    force: bool = False,
) -> Dict[str, Any]:
    """Convert FASTQ to FASTA format using seqkit fq2fa.

    Args:
        input_file: Input FASTQ file path (supports .gz).
        output_file: Output FASTA file path.
        line_width: Bases per line in output (0 for no wrap). Default 60.
        threads: Number of CPU threads. Default 4.
        compress: Compress output with gzip. Default False.
        force: Overwrite existing output file. Default False.

    Returns:
        Dictionary with keys: success, input_file, output_file, message.

    Raises:
        FileNotFoundError: Input file does not exist.
        FileExistsError: Output file exists and force is False.
        RuntimeError: seqkit command failed.
    """
    input_path = Path(input_file).resolve()
    output_path = Path(output_file).resolve()

    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    if compress and output_path.suffix != ".gz":
        output_path = Path(str(output_path) + ".gz")

    if output_path.exists() and not force:
        raise FileExistsError(
            f"Output file already exists: {output_path}. Use force=True to overwrite."
        )

    cmd = [
        "seqkit",
        "fq2fa",
        "-o",
        str(output_path),
        "-w",
        str(line_width),
        "-j",
        str(threads),
        str(input_path),
    ]

    try:
        subprocess.run(cmd, capture_output=True, text=True, check=True)

        return {
            "success": True,
            "input_file": str(input_path),
            "output_file": str(output_path),
            "message": f"Successfully converted {input_path} to FASTA format",
        }
    except subprocess.CalledProcessError as e:
        raise RuntimeError(
            f"seqkit fq2fa failed with return code {e.returncode}.\nstderr: {e.stderr}"
        ) from e


@tool
def index_fasta(input_file: str, force: bool = False) -> Dict[str, Any]:
    """Create FAI index file for a FASTA file using seqkit faidx.

    Args:
        input_file: Input FASTA file path (must be uncompressed).
        force: Overwrite existing index file. Default False.

    Returns:
        Dictionary with keys: success, input_file, index_file, message.

    Raises:
        FileNotFoundError: Input file does not exist.
        ValueError: Input file is compressed (.gz).
        FileExistsError: Index file exists and force is False.
        RuntimeError: seqkit command failed.
    """
    input_path = Path(input_file).resolve()
    index_path = Path(f"{input_path}.fai")

    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    if input_path.suffix == ".gz":
        raise ValueError("Input file must be uncompressed FASTA, not .gz")

    if index_path.exists() and not force:
        raise FileExistsError(
            f"Index file already exists: {index_path}. Use force=True to overwrite."
        )

    cmd = ["seqkit", "faidx", str(input_path)]

    try:
        subprocess.run(cmd, capture_output=True, text=True, check=True)

        return {
            "success": True,
            "input_file": str(input_path),
            "index_file": str(index_path),
            "message": f"Successfully created index for {input_path}",
        }
    except subprocess.CalledProcessError as e:
        raise RuntimeError(
            f"seqkit faidx failed with return code {e.returncode}.\nstderr: {e.stderr}"
        ) from e


def _do_convert_table_format(
    input_file: str,
    output_file: str,
    input_format: Literal["csv", "tsv", "excel"],
    output_format: Literal["csv", "tsv", "excel"],
    sheet_name: str = "Sheet1",
    encoding: str = "utf-8",
    force: bool = False,
) -> Dict[str, Any]:
    input_path = Path(input_file).resolve()
    output_path = Path(output_file).resolve()

    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    if output_path.exists() and not force:
        raise FileExistsError(
            f"Output file already exists: {output_path}. Use force=True to overwrite."
        )

    valid_formats = {"csv", "tsv", "excel"}
    if input_format not in valid_formats:
        raise ValueError(
            f"Invalid input_format: {input_format}. Must be one of {valid_formats}"
        )
    if output_format not in valid_formats:
        raise ValueError(
            f"Invalid output_format: {output_format}. Must be one of {valid_formats}"
        )

    try:
        if input_format == "csv":
            df = pd.read_csv(input_path, encoding=encoding)
        elif input_format == "tsv":
            df = pd.read_csv(input_path, sep="\t", encoding=encoding)
        elif input_format == "excel":
            df = pd.read_excel(input_path, sheet_name=sheet_name)

        if output_format == "csv":
            df.to_csv(output_path, index=False, encoding=encoding)
        elif output_format == "tsv":
            df.to_csv(output_path, sep="\t", index=False, encoding=encoding)
        elif output_format == "excel":
            df.to_excel(output_path, sheet_name=sheet_name, index=False)

        return {
            "success": True,
            "input_file": str(input_path),
            "output_file": str(output_path),
            "rows": len(df),
            "columns": len(df.columns),
            "column_names": list(df.columns),
            "message": f"Successfully converted {input_path} ({input_format}) to {output_format} format",
        }
    except Exception as e:
        raise RuntimeError(f"Conversion failed: {str(e)}") from e


@tool
def convert_table_format(
    input_file: str,
    output_file: str,
    input_format: Literal["csv", "tsv", "excel"],
    output_format: Literal["csv", "tsv", "excel"],
    sheet_name: str = "Sheet1",
    encoding: str = "utf-8",
    force: bool = False,
) -> Dict[str, Any]:
    """Convert between CSV, TSV, and Excel formats.

    Args:
        input_file: Input file path.
        output_file: Output file path.
        input_format: Input format (csv, tsv, excel).
        output_format: Output format (csv, tsv, excel).
        sheet_name: Sheet name for Excel input/output. Default "Sheet1".
        encoding: File encoding for CSV/TSV. Default "utf-8".
        force: Overwrite existing output file. Default False.

    Returns:
        Dictionary with keys: success, input_file, output_file, rows, columns, message.

    Raises:
        FileNotFoundError: Input file does not exist.
        FileExistsError: Output file exists and force is False.
        ValueError: Unsupported format specified.
        RuntimeError: Conversion failed.
    """
    return _do_convert_table_format(
        input_file,
        output_file,
        input_format,
        output_format,
        sheet_name,
        encoding,
        force,
    )


@tool
def csv_to_tsv(
    input_file: str,
    output_file: str,
    encoding: str = "utf-8",
    force: bool = False,
) -> Dict[str, Any]:
    """Convert CSV file to TSV format.

    Args:
        input_file: Input CSV file path.
        output_file: Output TSV file path.
        encoding: File encoding. Default "utf-8".
        force: Overwrite existing output file. Default False.

    Returns:
        Dictionary with conversion result.
    """
    return _do_convert_table_format(
        input_file=input_file,
        output_file=output_file,
        input_format="csv",
        output_format="tsv",
        encoding=encoding,
        force=force,
    )


@tool
def tsv_to_csv(
    input_file: str,
    output_file: str,
    encoding: str = "utf-8",
    force: bool = False,
) -> Dict[str, Any]:
    """Convert TSV file to CSV format.

    Args:
        input_file: Input TSV file path.
        output_file: Output CSV file path.
        encoding: File encoding. Default "utf-8".
        force: Overwrite existing output file. Default False.

    Returns:
        Dictionary with conversion result.
    """
    return _do_convert_table_format(
        input_file=input_file,
        output_file=output_file,
        input_format="tsv",
        output_format="csv",
        encoding=encoding,
        force=force,
    )


@tool
def csv_to_excel(
    input_file: str,
    output_file: str,
    sheet_name: str = "Sheet1",
    encoding: str = "utf-8",
    force: bool = False,
) -> Dict[str, Any]:
    """Convert CSV file to Excel format.

    Args:
        input_file: Input CSV file path.
        output_file: Output Excel file path (.xlsx).
        sheet_name: Sheet name in Excel. Default "Sheet1".
        encoding: File encoding. Default "utf-8".
        force: Overwrite existing output file. Default False.

    Returns:
        Dictionary with conversion result.
    """
    return _do_convert_table_format(
        input_file=input_file,
        output_file=output_file,
        input_format="csv",
        output_format="excel",
        sheet_name=sheet_name,
        encoding=encoding,
        force=force,
    )


@tool
def excel_to_csv(
    input_file: str,
    output_file: str,
    sheet_name: str = "Sheet1",
    encoding: str = "utf-8",
    force: bool = False,
) -> Dict[str, Any]:
    """Convert Excel file to CSV format.

    Args:
        input_file: Input Excel file path (.xlsx).
        output_file: Output CSV file path.
        sheet_name: Sheet name to read. Default "Sheet1".
        encoding: File encoding. Default "utf-8".
        force: Overwrite existing output file. Default False.

    Returns:
        Dictionary with conversion result.
    """
    return _do_convert_table_format(
        input_file=input_file,
        output_file=output_file,
        input_format="excel",
        output_format="csv",
        sheet_name=sheet_name,
        encoding=encoding,
        force=force,
    )


@tool
def tsv_to_excel(
    input_file: str,
    output_file: str,
    sheet_name: str = "Sheet1",
    encoding: str = "utf-8",
    force: bool = False,
) -> Dict[str, Any]:
    """Convert TSV file to Excel format.

    Args:
        input_file: Input TSV file path.
        output_file: Output Excel file path (.xlsx).
        sheet_name: Sheet name in Excel. Default "Sheet1".
        encoding: File encoding. Default "utf-8".
        force: Overwrite existing output file. Default False.

    Returns:
        Dictionary with conversion result.
    """
    return _do_convert_table_format(
        input_file=input_file,
        output_file=output_file,
        input_format="tsv",
        output_format="excel",
        sheet_name=sheet_name,
        encoding=encoding,
        force=force,
    )


@tool
def excel_to_tsv(
    input_file: str,
    output_file: str,
    sheet_name: str = "Sheet1",
    encoding: str = "utf-8",
    force: bool = False,
) -> Dict[str, Any]:
    """Convert Excel file to TSV format.

    Args:
        input_file: Input Excel file path (.xlsx).
        output_file: Output TSV file path.
        sheet_name: Sheet name to read. Default "Sheet1".
        encoding: File encoding. Default "utf-8".
        force: Overwrite existing output file. Default False.

    Returns:
        Dictionary with conversion result.
    """
    return _do_convert_table_format(
        input_file=input_file,
        output_file=output_file,
        input_format="excel",
        output_format="tsv",
        sheet_name=sheet_name,
        encoding=encoding,
        force=force,
    )


@tool
def list_excel_sheets(input_file: str) -> Dict[str, Any]:
    """List all sheet names in an Excel file.

    Args:
        input_file: Input Excel file path (.xlsx).

    Returns:
        Dictionary with sheet names.

    Raises:
        FileNotFoundError: Input file does not exist.
    """
    input_path = Path(input_file).resolve()

    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    xl = pd.ExcelFile(input_path)
    sheets = xl.sheet_names

    return {
        "success": True,
        "input_file": str(input_path),
        "sheets": sheets,
        "count": len(sheets),
        "message": f"Found {len(sheets)} sheet(s): {', '.join(sheets)}",
    }
