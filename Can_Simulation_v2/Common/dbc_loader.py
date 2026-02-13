from pathlib import Path
import cantools

def load_dbc():
    base_dir = Path(__file__).resolve().parent.parent
    dbc_path = base_dir / "Common" / "vehicle.dbc"
    return cantools.database.load_file(str(dbc_path))
