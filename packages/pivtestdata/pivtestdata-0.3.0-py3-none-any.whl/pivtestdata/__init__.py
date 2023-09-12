from . import pivtec, piv_challenge
from ._version import __version__
from .webzip import WebZip, user_dir


def delete_all_downloaded_files():
    """Delete all files downloaded by pivtestdata."""
    if not user_dir.exists():
        return
    import shutil
    shutil.rmtree(user_dir)


def download_all():
    """Download all files from PIV Challenge and the ILA vortex pair"""
    for p in (*piv_challenge.all_cases, pivtec.turbulent_boundary_layer, pivtec.vortex_pair):
        p.download()


__all__ = ['WebZip', 'piv_challenge', 'user_dir', 'pivtec', 'delete_all_downloaded_files', 'download_all',
           '__version__']
