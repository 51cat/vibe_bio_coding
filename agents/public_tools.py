import shutil
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

from langchain.tools import tool


@tool
def create_workdir(
    workdir_name: Optional[str] = None,
    parent_dir: str = ".",
    prefix: str = "workdir"
) -> Dict[str, Any]:
    """Create a working directory for analysis and output files.
    
    Args:
        workdir_name: Custom name for the working directory. If None, auto-generate with timestamp.
        parent_dir: Parent directory where the workdir will be created. Default current directory.
        prefix: Prefix for auto-generated directory name. Default "workdir".
    
    Returns:
        Dictionary with keys: success, workdir, message.
    
    Raises:
        OSError: Failed to create working directory.
    """
    parent_path = Path(parent_dir).resolve()
    
    if workdir_name:
        workdir_path = parent_path / workdir_name
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        workdir_path = parent_path / f"{prefix}_{timestamp}"
    
    try:
        workdir_path.mkdir(parents=True, exist_ok=False)
        
        return {
            "success": True,
            "workdir": str(workdir_path),
            "message": f"Successfully created working directory: {workdir_path}"
        }
    except FileExistsError:
        raise FileExistsError(f"Working directory already exists: {workdir_path}")
    except OSError as e:
        raise OSError(f"Failed to create working directory: {e}") from e


@tool
def create_output_dir(
    dir_path: str,
    exist_ok: bool = False
) -> Dict[str, Any]:
    """Create an output directory.
    
    Args:
        dir_path: Path of the directory to create.
        exist_ok: Do not raise error if directory exists. Default False.
    
    Returns:
        Dictionary with keys: success, dir_path, message.
    
    Raises:
        FileExistsError: Directory exists and exist_ok is False.
        OSError: Failed to create directory.
    """
    path = Path(dir_path).resolve()
    
    if path.exists() and not exist_ok:
        raise FileExistsError(
            f"Directory already exists: {path}. Use exist_ok=True to ignore."
        )
    
    try:
        path.mkdir(parents=True, exist_ok=exist_ok)
        
        return {
            "success": True,
            "dir_path": str(path),
            "message": f"Successfully created directory: {path}"
        }
    except OSError as e:
        raise OSError(f"Failed to create directory {path}: {e}") from e


@tool
def zip_directory(
    source_dir: str,
    output_file: str,
    force: bool = False
) -> Dict[str, Any]:
    """Compress a directory into a zip file.
    
    Args:
        source_dir: Path of the directory to compress.
        output_file: Output zip file path.
        force: Overwrite existing zip file. Default False.
    
    Returns:
        Dictionary with keys: success, source_dir, output_file, message.
    
    Raises:
        FileNotFoundError: Source directory does not exist.
        NotADirectoryError: Source path is not a directory.
        FileExistsError: Output file exists and force is False.
        OSError: Failed to create zip file.
    """
    source_path = Path(source_dir).resolve()
    output_path = Path(output_file).resolve()
    
    if not source_path.exists():
        raise FileNotFoundError(f"Source directory not found: {source_path}")
    
    if not source_path.is_dir():
        raise NotADirectoryError(f"Source path is not a directory: {source_path}")
    
    if output_path.exists() and not force:
        raise FileExistsError(
            f"Output file already exists: {output_path}. Use force=True to overwrite."
        )
    
    try:
        with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for file_path in source_path.rglob("*"):
                if file_path.is_file():
                    arcname = file_path.relative_to(source_path)
                    zf.write(file_path, arcname)
        
        return {
            "success": True,
            "source_dir": str(source_path),
            "output_file": str(output_path),
            "message": f"Successfully compressed {source_path} to {output_path}"
        }
    except OSError as e:
        raise OSError(f"Failed to create zip file: {e}") from e
