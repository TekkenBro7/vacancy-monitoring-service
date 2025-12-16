import os

EXCLUDE_DIRS = [
    "venv/",
    "node_modules",
    "__pycache__",
    ".git",
    "migrations",
    ".mypy_cache",
    "build",
    "lib/",
    ".idea",
    ".vscode",
    ".ruff_cache",
    ".pytest_cache",
    ".ruff_cache",
    "bin",
    "include",
    "lib",
    "lib64"
]


def print_directory_structure(root_dir: str, prefix: str = "", is_root: bool = True) -> None:
    try:
        items = os.listdir(root_dir)

        directories = []
        files = []

        for item in items:
            full_path = os.path.join(root_dir, item)
            if os.path.isdir(full_path):
                directories.append(item)
            else:
                files.append(item)

        if is_root:
            print("└── " + os.path.basename(root_dir))
            new_prefix = prefix + "    "
        else:
            new_prefix = prefix

        for i, file_name in enumerate(files):
            if i == len(files) - 1 and not directories:
                print(new_prefix + "└── " + file_name)
            else:
                print(new_prefix + "├── " + file_name)

        for i, dir_name in enumerate(directories):
            full_dir_path = os.path.join(root_dir, dir_name)

            if i == len(directories) - 1:
                dir_prefix = new_prefix + "    "
                print(new_prefix + "└── " + dir_name + "/")
            else:
                dir_prefix = new_prefix + "│   "
                print(new_prefix + "├── " + dir_name + "/")

            if dir_name not in EXCLUDE_DIRS:
                print_directory_structure(full_dir_path, dir_prefix, is_root=False)

    except Exception as ex:
        print(f"{new_prefix}    [Access error: {ex}]")
        return


if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    print("Current directory:", current_dir)
    print(f"Excluded directories: {', '.join(EXCLUDE_DIRS)}")
    offset = input(
        "Enter a relative path to change the current directory, or press Enter to skip: "
    ).strip()

    final_dir = os.path.abspath(os.path.join(current_dir, offset)) if offset else current_dir
    print("Final directory:", final_dir)
    print("\nDirectory structure:")
    print_directory_structure(final_dir)
