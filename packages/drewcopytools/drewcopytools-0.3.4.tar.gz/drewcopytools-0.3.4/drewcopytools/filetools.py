# Some utiltiy functions for helping us with file type things...
from pathlib import Path
from typing import Union

# ---------------------------------------------------------------------------------------------------------
def read_utf8_file(path:Union[Path,str]) -> str:
    """
    Reads content from a file at the given path.
    This function assumes that the data is encoded as UTF-8 and will handle any issues with byte-order-marks
    as needed.
    """
    path = _toStr(path)

    # According to: https://stackoverflow.com/questions/13590749/reading-unicode-file-data-with-bom-chars-in-python
    # utf-8-sig will handle the BOM automatically, and doesn't necessarily expect it.
    with open(path, 'r', encoding='utf-8-sig') as rHandle:
        data = rHandle.read()
        return data

# ---------------------------------------------------------------------------------------------------------
def delete_file(path:Union[Path,str]):
    """
    Deletes the file at the given path, if it exists.
    """
    usePath = _toPath(path)
    if usePath.exists():
        usePath.unlink()
        
# ---------------------------------------------------------------------------------------------------------
def get_sequential_file_path(dir:Union[Path,str], basename:str, extension:str) ->Path:
    """
    Generates a sequential file name <basename>_<0, 1,2,3, etc.> in the given directory.
    The directory will be created if it doesn't already exist.
    """
    if isinstance(dir, str):
        dir = Path(dir)
    if not isinstance(dir, Path):
        raise Exception(f"'dir' must be str or Path!")
        
    if not dir.exists():
        dir.mkdir()

    SANITY_COUNT = 1024    # We will give up attempting to create a sequential file after this many tries.

    # We will grab the oldest file with the given base name as check its number.
    # https://stackoverflow.com/questions/39909655/listing-of-all-files-in-directory
    # see answer by prasastoadi (list comprehension)
    entries = dir.glob("**/*")
    files = [x for x in entries if x.is_file() and x.name.startswith(basename) ]
    maxTime = 0

    newest: Path = None
    for f in files:
        time = f.stat().st_mtime
        if time > maxTime:
            maxTime = time
            newest = f

    fNumber = 0
    if newest != None:
        fNumberStr = newest.name.replace(basename + "_", '').replace(extension, '')
        if fNumberStr == '':
            fNumber = 0
        else:
            fNumber = int(fNumberStr)

    newName = basename + "_" + str(fNumber + 1) + extension
    res =  dir / newName
    return res


# ---------------------------------------------------------------------------------------------------------
def _toPath(path:Union[str,Path]):
    if isinstance(path, str):
        res = Path(path)
        return res
    else:
        return path

# ---------------------------------------------------------------------------------------------------------
def _toStr(path:Union[str,Path]):
    if isinstance(path, Path):
        res = str(path)
        return res
    else:
        return path
    

# ----------------------------------------------------------------------------------------------------------
def file_exists(path) -> bool:
    p  = Path(path)
    res = p.exists() and p.is_file()
    return res

# ----------------------------------------------------------------------------------------------------------
def directory_exists(path) -> bool:
    p  = Path(path)
    res = p.exists() and p.is_dir()
    return res

# ----------------------------------------------------------------------------------------------------------
def write_all_lines(path, lines, newLineChar="\n"):
  """
  This function solves the problem where the authors of python decided that 'writelines'
  shouldn't actually write lines, but instead blast the raw text to the file.
  Sadly this kind of jank is just par for the course when it comes to python.
  """
  path.writelines(line + newLineChar for line in lines)

# ----------------------------------------------------------------------------------------------------------
def read_all_lines(filename):
    """Read all lines from the given file.  Default separator is '\n'"""
    try:
        with open(filename, 'r') as file:
            # Read all lines from the file and strip any leading/trailing whitespace
            lines = [line.strip() for line in file.readlines()]
        return lines
    except FileNotFoundError:
        print(f"The file '{filename}' was not found.")
        return []
    except Exception as e:
        print(f"An error occurred: {e}")
        return []


