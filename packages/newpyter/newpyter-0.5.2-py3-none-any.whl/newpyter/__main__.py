usage = """
Usages:
python -m newpyter --to ipynb file1.newpy file2.newpy
python -m newpyter --to newpy file1.ipynb file2.ipynb
python -m newpyter debug   # shows used storage in cwd 

(if your env with newpyter is activated, you can skip 'python -m')
"""
# CLI for newpyter
import sys
from pathlib import Path

from newpyter.ContentsManager import NewpyterContentsManager


def to_paths(files, suffix):
    files = [Path(f).absolute() for f in files]
    for f in files:
        assert f.exists(), f'file {f} does not exist'
        assert f.suffix == suffix, (f.suffix, suffix)
    return files


manager = NewpyterContentsManager()
manager.root_dir = '/'



def main():
    if sys.argv[1:] == ['debug']:
        from newpyter.config import get_storage_for_notebook
        storage = get_storage_for_notebook(notebook_filename=Path().joinpath('nonexistent.ipynb'))
        print(storage)
        return

    if len(sys.argv) < 4:
        print(usage)
        exit(1)

    _, command, output_format, *files = sys.argv
    if command != '--to' or (output_format not in ['ipynb', 'newpy']):
        print(usage)
        exit(1)

    input_suffix = {'ipynb': '.newpy', 'newpy': '.ipynb'}[output_format]

    files = to_paths(files, input_suffix)
    for file in files:
        print('processing', file)
        manager.convert_from_newpy_to_ipynb_or_reverse(
            str(file),
            str(file.with_suffix(f'.{output_format}')),
        )


if __name__ == '__main__':
    main()
