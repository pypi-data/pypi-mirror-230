import importlib.resources
import importlib.metadata
from pathlib import Path

_dir_tex = Path("tex")
_dir_pdf = Path("pdf")
_dir_png = Path("png")
_dir_tmp = Path("tmp")
_dir_config = Path("config")
_dirs = [_dir_tex, _dir_pdf, _dir_png, _dir_tmp, _dir_config]

_pool = "pool.tex"
_header = "header.tex"
_footer = "footer.tex"
_snapshot = "snapshot.tex"
_config = "config.toml"

_version = importlib.metadata.version("tentamaker")
_config_path_system = importlib.resources.files("tentamaker") / _dir_config
_config_path_local = _dir_config
