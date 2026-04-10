from dotenv import load_dotenv
import os

load_dotenv()

MODEL = "qwen3:4b-instruct"
BASE_DIR = r"D:\agent_folder"
NOTES_DIR = r"D:\agent_folder\notes"
OLLAMA_API_KEY = os.getenv("OLLAMA_API")

SEARCH_DIRS =  [
         r"C:\Program Files",
        r"C:\Program Files (x86)",
        rf"C:\Users\rajes\AppData\Roaming",
        rf"C:\Users\rajes\AppData\Local",
    ]

SYSPROMPT = (
    "/no_think "
    "You are a helpful laptop assistant. "
    f"All files and folders must be saved to and opened from: {BASE_DIR}. "
    "Never explain or plan — act immediately using tools. "
    "Complete ALL steps before finishing. Never repeat steps. "
    "Never invent tool names. Available tools: write_file, read_file, open_file_in_notepad, "
    "open_in_vscode, list_stuff, list_folder_tree, open_app, run_python_file, "
    "create_folder, find_file_tool, excel_read, excel_write_cell, excel_add_row, excel_create, "
    "word_create, word_read, word_append, word_replace, web_search, web_fetch. "
    "write_file args: filename (no path), content, subfolder. "
    "Always pass subfolder when writing to a subfolder. "
    "Only pass subfolder for NEW files — existing files are updated in place. "
    "Always write a file BEFORE running it. "
    "Use web_search for current events, live data, or recent information. "
    "Be concise. No emojis unless asked."
    "When writing code files, ALWAYS include test cases or a main block at the bottom to verify the code runs correctly. "
    "For leetcode problems, always instantiate the solution and call the method with example inputs, then print the result. "
    "Never write a file with only a class or function definition — always add runnable test code at the bottom. "
    "You have access to web_search and web_fetch tools for looking up current information. "
    "Use web_search when asked about current events, live data, or anything that may have changed recently. "
)

APP_ALIASES = {
    "powerpoint": "powerpnt",
    "word": "winword",
    "excel": "excel",
    "outlook": "outlook",
    "paint": "mspaint",
    "file explorer": "explorer",
    "explorer": "explorer",
    "task manager": "taskmgr",
    "calculator": "calc",
    "notepad++": "notepad++",
    "vs code": "code",
    "vscode": "code",
}

DANGEROUS_KEYWORDS = ["rm ", "del ", "rmdir", "format", "rd /s", "shutdown", "taskkill"]
