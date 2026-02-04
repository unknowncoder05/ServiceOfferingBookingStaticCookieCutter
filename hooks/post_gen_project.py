#!/usr/bin/env python
"""Post-generation hook for cookiecutter template."""
import os
import shutil
import subprocess


def remove_ai_integration():
    """Remove AI-related files and dependencies if not selected."""
    # Files/directories to remove when AI integration is not selected
    ai_related_paths = [
        # Add AI-specific paths here if needed in the future
    ]

    for path in ai_related_paths:
        if os.path.exists(path):
            if os.path.isdir(path):
                shutil.rmtree(path)
            else:
                os.remove(path)

    # Remove AI-related dependencies from requirements
    requirements_file = os.path.join('BackEndApi', 'requirements', 'base.txt')
    if os.path.exists(requirements_file):
        with open(requirements_file, 'r') as f:
            lines = f.readlines()

        ai_packages = ['openai', 'anthropic', 'langchain', 'tiktoken']
        filtered_lines = []
        skip_next = False

        for line in lines:
            # Check if this is an AI package
            is_ai_package = any(pkg in line.lower() for pkg in ai_packages)
            # Check if this is a comment about AI
            is_ai_comment = '# AI' in line or '# Optional AI' in line

            if is_ai_comment:
                skip_next = True
                continue

            if skip_next and is_ai_package:
                skip_next = False
                continue

            skip_next = False
            filtered_lines.append(line)

        with open(requirements_file, 'w') as f:
            f.writelines(filtered_lines)


def init_git_repo():
    """Initialize a fresh git repository."""
    try:
        subprocess.run(['git', 'init'], check=True, capture_output=True)
        subprocess.run(['git', 'add', '.'], check=True, capture_output=True)
        subprocess.run(
            ['git', 'commit', '-m', 'Initial commit from cookiecutter template'],
            check=True,
            capture_output=True
        )
        print("Git repository initialized with initial commit.")
    except subprocess.CalledProcessError as e:
        print(f"Warning: Could not initialize git repository: {e}")
    except FileNotFoundError:
        print("Warning: Git not found. Skipping repository initialization.")


def main():
    """Main post-generation hook."""
    print("Running post-generation hooks...")

    # Remove AI integration if not selected
    if '{{ cookiecutter.use_ai_integration }}' != 'y':
        print("Removing AI integration files...")
        remove_ai_integration()

    # Initialize git repository
    print("Initializing git repository...")
    init_git_repo()

    print("\n" + "=" * 60)
    print("Project '{{ cookiecutter.project_name }}' created successfully!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. cd {{ cookiecutter.project_slug }}")
    print("2. Review and update .env files in BackEndApi/.envs/")
    print("3. Run 'make setup' to initialize the development environment")
    print("4. Run 'make dev' to start the development servers")
    print("\nFor more information, see the README.md file.")


if __name__ == '__main__':
    main()
