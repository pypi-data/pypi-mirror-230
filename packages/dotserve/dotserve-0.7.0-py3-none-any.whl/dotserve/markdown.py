import os

from dotserve.logger import logger

# Default dotserve.md file created if none exists
DEFAULT_MARKDOWN_STR = """# Welcome to Dotagent! 🚀🤖

Hi there, Developer! 👋 We're excited to have you on board. dotagent is a library of modular components and an orchestration framework. Inspired by a microservices approach, it gives developers all the components they need to build robust, stable & reliable AI applications and experimental autonomous agents.


## Welcome screen

To modify the welcome screen, edit the `dotagent.md` file at the root of your project. If you do not want a welcome screen, just leave this file empty.
"""


def init_markdown(root: str):
    """Initialize the dotserve.md file if it doesn't exist."""
    dotserve_md_file = os.path.join(root, "dotserve.md")

    if not os.path.exists(dotserve_md_file):
        with open(dotserve_md_file, "w", encoding="utf-8") as f:
            f.write(DEFAULT_MARKDOWN_STR)
            logger.info(f"Created default dotserve markdown file at {dotserve_md_file}")


def get_markdown_str(root: str):
    """Get the dotserve.md file as a string."""
    dotserve_md_path = os.path.join(root, "dotserve.md")
    if os.path.exists(dotserve_md_path):
        with open(dotserve_md_path, "r", encoding="utf-8") as f:
            dotserve_md = f.read()
            return dotserve_md
    else:
        return None
