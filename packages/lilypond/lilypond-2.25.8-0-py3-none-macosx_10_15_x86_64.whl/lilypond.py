
from pathlib import Path

def executable(script="lilypond"):
    return Path(__file__).parent / "lilypond-binaries" / "bin" / script
