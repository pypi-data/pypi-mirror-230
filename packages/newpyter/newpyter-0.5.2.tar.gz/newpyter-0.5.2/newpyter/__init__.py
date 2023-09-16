from pathlib import Path
__version__ = '0.5.2'

def patch_jupyterlab_frontend(allow_patching_multiple=True):
    """
    Jupyter's frontend code does not recognize any other extension but ipynb as notebooks.
    No matter what jupyter backend informs and passes.

    In jlab 4.X there seems to be a way to modify this behavior with labextension,
    but I don't want to maintain full extension given we basically need to replace one line js.
    """
    try:
        from jupyterlab._version import __version__
    except ImportError:
        print('Did not locate jupyterlab')
        # no jupyter lab - no problems. Jupyter notebook seems to work properly
        return
    from jupyter_core.paths import jupyter_path

    candidate_files = [
        Path(file)
        for path in jupyter_path()
        for file in Path(path).glob('**/*.js')
    ]

    def contains_one_of(source_text, options):
        return any(option in source_text for option in options)

    original = '[".ipynb"]'
    patched = '[".ipynb", ".newpy"]'

    appropriate_files = [
        p for p in candidate_files
        if p.parent.name == 'static'
        and contains_one_of(p.open().read(), [original, patched])
    ]
    if len(appropriate_files) == 0:
        raise RuntimeError(f'Found no appropriate js to patch among {candidate_files} in {jupyter_path()}')
    if len(appropriate_files) > 1 and not allow_patching_multiple:
        raise RuntimeError(f'Found several appropriate js files to patch: {appropriate_files}')

    for file in appropriate_files:
        with file.open() as f:
            text = f.read()

        if original in text:
            print(f"Patching jupyterlab to support .newpy extension at {file}")
            with file.open('w') as f:
                f.write(text.replace(original, patched))
            print(f"Patched  jupyterlab to support .newpy extension at {file}")
        elif patched in text:
            print(f"Jupyterlab is already patched at {file}")
        else:
            raise RuntimeError('Did not find fragment to be patched in jupyterlab')
