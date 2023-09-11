from pathlib import Path

from src.utils import generate_sumake

home_dir = Path.home()
current = Path(__file__).parent.absolute()

generate_sumake(home_dir, current)
