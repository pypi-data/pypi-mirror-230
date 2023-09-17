import pathlib


def push_generation(path: pathlib.Path, minimum_length: int = 3):
    if not path.is_file():
        raise ValueError
    minimum_length = 0 if minimum_length < 0 else minimum_length

    try:
        current = int(path.suffix[-1:])
    except ValueError:
        current = 0
        current_path = path.with_name(f"{path.name}.0")
    else:
        current_path = path
    next_path = current_path.with_suffix(f".{current+1:0{minimum_length}d}")
    if next_path.exists():
        push_generation(path=next_path, minimum_length=minimum_length)
    path.rename(next_path)


if __name__ == "__main__":
    push_generation(pathlib.Path("a.txt"))
