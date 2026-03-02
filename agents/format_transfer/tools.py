import subprocess
from pathlib import Path
from typing import Dict, Any

from langchain.tools import tool


@tool
def fastq2fasta(
    input_file: str,
    output_file: str,
    line_width: int = 60,
    threads: int = 4,
    compress: bool = False,
    force: bool = False
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
        "seqkit", "fq2fa",
        "-o", str(output_path),
        "-w", str(line_width),
        "-j", str(threads),
        str(input_path)
    ]
    
    try:
        subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        return {
            "success": True,
            "input_file": str(input_path),
            "output_file": str(output_path),
            "message": f"Successfully converted {input_path} to FASTA format"
        }
    except subprocess.CalledProcessError as e:
        raise RuntimeError(
            f"seqkit fq2fa failed with return code {e.returncode}.\n"
            f"stderr: {e.stderr}"
        ) from e


@tool
def index_fasta(
    input_file: str,
    force: bool = False
) -> Dict[str, Any]:
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
            "message": f"Successfully created index for {input_path}"
        }
    except subprocess.CalledProcessError as e:
        raise RuntimeError(
            f"seqkit faidx failed with return code {e.returncode}.\n"
            f"stderr: {e.stderr}"
        ) from e
