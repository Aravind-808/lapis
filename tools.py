import glob
import os
import shutil
import subprocess
import threading
 
from config import APP_ALIASES, BASE_DIR, NOTES_DIR, SEARCH_DIRS

def write_file(filename, content, subfolder= ""):
    """Write text content to a file in the agent folder.

    Args:
        filename: Just the filename e.g. hello.py — do NOT include any path
        content: The full text content to write into the file
        subfolder: Optional subfolder inside agent folder e.g. projects — leave empty for notes

    Returns:
        A message confirming the file was written with its full path
    """
    filename = os.path.basename(filename)
    base = os.path.join(r"D:\agent_folder", subfolder) if subfolder else NOTES_DIR
    os.makedirs(base, exist_ok=True)
    full_path = os.path.join(base, filename)

    content = content.replace("\\n", "\n").replace("\\t", "\t")
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content)
    return f"File written: {full_path}"

def find_file(filename):
    """Helper — recursively find a file anywhere inside agent_folder.
    Returns full path if found, None if not."""
    for root, dirs, files in os.walk(BASE_DIR):
        if filename in files:
            return os.path.join(root, filename)
    return None

def find_file_tool(filename):
    """Search for a file anywhere inside the agent folder.

    Args:
        filename: Just the filename e.g. hello.py

    Returns:
        The full path if found, or an error message
    """
    result = find_file(filename)
    return result if result else f"Error: {filename} not found anywhere in {BASE_DIR}"

def read_file(filename , subfolder  = ""):
    """Read the content of any file inside the agent folder.

    Args:
        filename: Just the filename e.g. q1.txt — do NOT include any path
        subfolder: Optional hint for which subfolder e.g. leetcode/q1

    Returns:
        The text content of the file
    """
    if subfolder:
        full_path = os.path.join(BASE_DIR, subfolder, filename)
    else:
        full_path = find_file(filename)

    if not full_path or not os.path.exists(full_path):
        return f"Error: {filename} not found anywhere in {BASE_DIR}"

    return open(full_path, "r", encoding="utf-8").read()


def open_in_vscode(filename ) :
    """Open any file from the agent folder in VS Code.

    Args:
        filename: Just the filename e.g. attention.py — do NOT include any path

    Returns:
        A message confirming VS Code was launched
    """
    full_path = find_file(filename)
    if not full_path:
        return f"Error: {filename} not found anywhere in {BASE_DIR}"
    subprocess.Popen(["code", full_path], shell=True)
    return f"Opened {full_path} in VS Code"


def open_file_in_notepad(filename ) :
    """Open any file from the agent folder in Notepad.

    Args:
        filename: Just the filename e.g. poem.txt — do NOT include any path

    Returns:
        A message confirming Notepad was launched
    """
    full_path = find_file(filename)
    if not full_path:
        return f"Error: {filename} not found anywhere in {BASE_DIR}"
    subprocess.Popen(["notepad.exe", full_path])
    return f"Opened {full_path} in Notepad"


def run_python_file(filename, subfolder = ""):
    """Run a Python file from inside the agent folder.

    Args:
        filename: Just the filename e.g. hello.py — do NOT include any path
        subfolder: Optional hint if you know which subfolder it's in e.g. coding/LLM

    Returns:
        The output or error from running the script
    """
    # use subfolder hint if provided, otherwise search
    if subfolder:
        full_path = os.path.join(BASE_DIR, subfolder, filename)
    else:
        full_path = find_file(filename)

    if not full_path or not os.path.exists(full_path):
        return f"Error: {filename} not found anywhere in {BASE_DIR}"

    if not os.path.abspath(full_path).startswith(os.path.abspath(BASE_DIR)):
        return f"Error: cannot run files outside {BASE_DIR}"

    result = subprocess.run(
        ["python", full_path],
        capture_output=True,
        text=True,
        timeout=30
    )
    return result.stdout or result.stderr or "Script ran with no output"

def list_stuff(subfolder = ""):
    """List all files currently saved in the folder.

    Args: 
        subfolder: an optional subfolder to list. Leave empty for agent_folder
    Returns:
        A list of filenames in the folder
    """
    target = os.path.join(BASE_DIR, subfolder) if subfolder != "" else BASE_DIR
    if not os.path.exists(target):
        return f"Error, {target} doesnt exist."
    files = os.listdir(target)
    return "\n".join(files) if files else "Empty folder"

def list_folder_tree(subfolder: str = "") -> str:
    """List all files and folders recursively in a tree structure.

    Args:
        subfolder: Optional subfolder to list e.g. ecommerce — leave empty for root

    Returns:
        A tree structure of all files and folders
    """
    target = os.path.join(BASE_DIR, subfolder) if subfolder else BASE_DIR
    if not os.path.exists(target):
        return f"Error: {target} does not exist"
    lines = []
    for root, dirs, files in os.walk(target):
        level = root.replace(target, "").count(os.sep)
        indent = "  " * level
        lines.append(f"{indent}{os.path.basename(root)}/")
        for file in files:
            lines.append(f"{indent}  {file}")
    return "\n".join(lines) if lines else "Empty folder."


def open_app(app_name):
    """Open any application on Windows by searching for it.

    Args:
        app_name: The app to launch e.g. spotify, chrome, notepad, vlc

    Returns:
        A message confirming the app was launched or an error if not found
    """
    app_name = APP_ALIASES.get(app_name.lower(), app_name)

    # if the app is in PATH itself
    if shutil.which(app_name):
        threading.Thread(target=os.system, args=(app_name, ), daemon=True).start()
        # subprocess.Popen(app_name, shell=True)
        return f"Launched: {app_name}"

    # else search recursively
    search_dirs = SEARCH_DIRS

    for directory in search_dirs:
        matches = glob.glob(
            os.path.join(directory, "**", f"{app_name}.exe"),
            recursive=True
        )
        if matches:
            # subprocess.Popen(matches[0], shell=True) didnt work :(
            threading.Thread(target=os.system, args=(f'"{matches[0]}"', ), daemon=True).start()
            return f"Launched: {matches[0]}"
    try:
        subprocess.Popen(f"start {app_name}", shell=True)
        return f"Attempted to launch: {app_name}"
    except Exception as e:
        return f"Could not find or launch {app_name}: {str(e)}"

def create_folder(folder_name):
    """Create a new folder or nested folders inside the agent folder.

    Args:
        folder_name: Folder name or nested path
                     — do NOT use any path outside the agent folder

    Returns:
        A message confirming the folder was created
    """
    full_path = os.path.join(BASE_DIR, folder_name)

    # safety check
    if not os.path.abspath(full_path).startswith(os.path.abspath(BASE_DIR)):
        return f"Error: cannot create folders outside {BASE_DIR}"

    if os.path.exists(full_path):
        return f"Folder already exists: {full_path}"

    os.makedirs(full_path, exist_ok=True) 
    return f"Folder created: {full_path}"

# all avl tools
TOOLS = {
    "write_file": write_file,
    "open_file_in_notepad": open_file_in_notepad,
    "open_in_vscode": open_in_vscode,
    "read_file": read_file,
    "list_stuff": list_stuff,
    "open_app": open_app,
    "run_python_file": run_python_file,
    "create_folder": create_folder,
    "find_file_tool": find_file_tool,
    "list_folder_tree": list_folder_tree
}