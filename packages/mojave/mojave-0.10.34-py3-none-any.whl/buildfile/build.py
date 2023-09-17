import subprocess
import sys

commit_types = {
    "build:": "major",
    "feat:": "minor",
    "fix:": "patch",
}

try:
    # Get the commit message from command-line arguments
    commit_message = sys.argv[1]
    if not commit_message:
        raise ValueError("Please provide a commit message.")

    # Determine the type of change based on the commit message
    commit_type = next(
        (prefix for prefix in commit_types.keys() if commit_message.startswith(prefix)),
        None,
    )

    # Read the current version from pyproject.toml
    with open("pyproject.toml", "r") as toml_file:
        toml_content = toml_file.read()
        current_version = toml_content.split('version = "')[1].split('"')[0]

    if commit_type:
        # Increment the version based on the commit type
        parts = current_version.split(".")
        version_bump = commit_types[commit_type]
        if version_bump == "major":
            parts[0] = str(int(parts[0]) + 1)
            parts[1] = "0"
            parts[2] = "0"
        elif version_bump == "minor":
            parts[1] = str(int(parts[1]) + 1)
            parts[2] = "0"
        else:
            parts[2] = str(int(parts[2]) + 1)
        next_version = ".".join(parts)
    else:
        print("No recognized commit type found. Using patch version bump.")
        parts = current_version.split(".")
        parts[2] = str(int(parts[2]) + 1)
        next_version = ".".join(parts)

    # Update pyproject.toml with the new version
    toml_content = toml_content.replace(
        f'version = "{current_version}"', f'version = "{next_version}"'
    )
    with open("pyproject.toml", "w") as toml_file:
        toml_file.write(toml_content)

    # Commit the version update and tag the commit
    subprocess.run(["git", "add", "."], check=True)
    subprocess.run(["git", "commit", "-m", commit_message], check=True)

    # Create the appropriate tag
    tag_message = (
        f"{commit_type.capitalize()} release: {next_version}"
        if commit_type
        else f"Patch release: {next_version}"
    )
    subprocess.run(
        ["git", "tag", f"v{next_version}", "-a", "-m", tag_message], check=True
    )
    subprocess.run(["git", "push"], check=True)
    subprocess.run(["git", "push", "origin", f"v{next_version}"], check=True)

    # # Build distribution archives
    # subprocess.run(["python", "-m", "pip", "install", "--upgrade", "build"], check=True)
    # subprocess.run(["python", "-m", "build"], check=True)

    # # Upload the distribution archives to PyPI using twine
    # subprocess.run(["python", "-m", "pip", "install", "--upgrade", "twine"], check=True)
    # subprocess.run(
    #     ["python", "-m", "twine", "upload", "--repository", "testpypi", "dist/*"],
    #     check=True,
    # )
except Exception as e:
    print("An error occurred:", str(e))
