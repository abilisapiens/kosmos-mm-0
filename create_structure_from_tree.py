import os

structure_file = "project_structure.txt"
base_path = "."

def prompt_overwrite(path, is_file=True):
    type_str = "file" if is_file else "folder"
    while True:
        response = input(f"{type_str.capitalize()} '{path}' already exists. Overwrite? [y/N]: ").strip().lower()
        if response in ("y", "yes"):
            return True
        elif response in ("n", "no", ""):
            return False

def parse_line(line):
    """Extract depth and name from a tree-like line, ignoring comments."""
    line = line.rstrip("\n")
    if not line.strip() or line.strip().startswith("#"):
        return None, None

    # Determine branch symbol
    if "├──" in line:
        prefix, name = line.rsplit("├──", 1)
    elif "└──" in line:
        prefix, name = line.rsplit("└──", 1)
    else:
        prefix, name = "", line  # top-level folder/file

    # Remove inline comment
    if "#" in name:
        name = name.split("#", 1)[0]

    name = name.strip()
    if not name:
        return None, None

    # Compute depth: count number of 4-space indentations in prefix (ignore │ symbols)
    leading_spaces = len(prefix.replace("│", " ").replace("─", " "))
    depth = leading_spaces // 4
    return depth, name

def create_structure_from_txt(file_path, base_path="."):
    stack = [(base_path, -1)]
    first_folder_skipped = False
    skip_top_level = None

    with open(file_path, "r") as f:
        for line in f:
            depth, name = parse_line(line)
            if name is None:
                continue

            # Prompt for top-level folder
            if not first_folder_skipped:
                first_folder_skipped = True
                if name.endswith("/"):
                    while skip_top_level is None:
                        response = input(f"Do you want to skip creating the top-level folder '{name}'? [y/N]: ").lower()
                        if response in ("y", "yes"):
                            skip_top_level = True
                        elif response in ("n", "no", ""):
                            skip_top_level = False
                    if skip_top_level:
                        continue

            current_path = os.path.join(stack[depth][0], name)

            if name.endswith("/"):
                if os.path.exists(current_path):
                    if not prompt_overwrite(current_path, is_file=False):
                        pass
                else:
                    os.makedirs(current_path)
                # update stack
                if len(stack) <= depth + 1:
                    stack.append((current_path, depth))
                else:
                    stack[depth + 1] = (current_path, depth)
            else:
                os.makedirs(os.path.dirname(current_path), exist_ok=True)
                if os.path.exists(current_path):
                    if prompt_overwrite(current_path, is_file=True):
                        open(current_path, "w").close()
                else:
                    open(current_path, "a").close()

if __name__ == "__main__":
    create_structure_from_txt(structure_file, base_path)
    print("Project structure created successfully.")

