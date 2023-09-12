import subprocess

def clean_and_format_code(path):
    # Remove unused imports
    autoflake_command = [
        "autoflake",
        "--remove-all-unused-imports",
        "--recursive",
        "--remove-unused-variables",
        "--in-place",
        path,
    ]
    subprocess.run(autoflake_command)

    # Sort imports
    isort_command = ["isort", path]
    subprocess.run(isort_command)
    
    # Reformat files
    black_command = ["black", path]
    subprocess.run(black_command)