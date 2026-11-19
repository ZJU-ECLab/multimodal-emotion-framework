"""Refresh only the five published resources from the repository's source files."""
from pathlib import Path
from shutil import copyfile

ROOT = Path(__file__).resolve().parents[1]
FILES = (
    "人人交互情绪词筛选流程.xlsx",
    "人人交互情绪词主观发生频率.xlsx",
    "人人交互情绪词各模态表达频率.xlsx",
    "情绪各模态信号整理.xlsx",
    "情绪识别模型综述.html",
)

def main():
    for name in FILES:
        if not (ROOT / name).is_file():
            raise FileNotFoundError(ROOT / name)
    destination = ROOT / "docs" / "files"
    destination.mkdir(parents=True, exist_ok=True)
    for name in FILES:
        copyfile(ROOT / name, destination / name)
    print(f"Published resources refreshed: {len(FILES)}")

if __name__ == "__main__":
    main()
