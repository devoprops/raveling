"""GitHub repository storage for configuration files."""

import os
import yaml
from typing import Optional, Dict, Any
from github import Github
from github.GithubException import GithubException

# GitHub configuration from environment
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_REPO = os.getenv("GITHUB_REPO", "devoprops/raveling")  # owner/repo
GITHUB_BRANCH = os.getenv("GITHUB_BRANCH", "main")
GITHUB_BASE_PATH = os.getenv("GITHUB_BASE_PATH", "src/configs")  # Base path in repo


class GitHubStorage:
    """Handle storage of config files in GitHub repository."""
    
    def __init__(self):
        self.github = None
        self.repo = None
        
        if not GITHUB_TOKEN:
            raise ValueError(
                "GITHUB_TOKEN environment variable is required. "
                "Please set it in your environment variables."
            )
        
        try:
            self.github = Github(GITHUB_TOKEN)
            self.repo = self.github.get_repo(GITHUB_REPO)
        except Exception as e:
            raise RuntimeError(
                f"Failed to initialize GitHub storage: {e}. "
                "Please check your GITHUB_TOKEN and GITHUB_REPO settings."
            )
    
    def get_file_path(self, config_type: str, name: str) -> str:
        """Get the file path in the GitHub repository."""
        # Sanitize name for filename
        safe_name = "".join(c for c in name if c.isalnum() or c in ('-', '_')).strip()
        return f"{GITHUB_BASE_PATH}/{config_type}s/{safe_name}.yaml"
    
    def _get_file_path(self, config_type: str, name: str) -> str:
        """Private alias for backward compatibility."""
        return self.get_file_path(config_type, name)
    
    def save_config(
        self,
        config_type: str,
        name: str,
        content: Dict[str, Any],
        commit_message: Optional[str] = None
    ) -> str:
        """
        Save a config file to GitHub.
        
        Returns the commit SHA.
        Raises RuntimeError if GitHub is not configured or operation fails.
        """
        if not self.repo:
            raise RuntimeError("GitHub storage not initialized")
        
        try:
            file_path = self._get_file_path(config_type, name)
            yaml_content = yaml.dump(content, default_flow_style=False, sort_keys=False)
            
            # Try to get existing file
            try:
                existing_file = self.repo.get_contents(file_path, ref=GITHUB_BRANCH)
                # Update existing file
                commit = self.repo.update_file(
                    path=file_path,
                    message=commit_message or f"Update {config_type}: {name}",
                    content=yaml_content,
                    sha=existing_file.sha,
                    branch=GITHUB_BRANCH
                )
            except GithubException:
                # File doesn't exist, create it
                commit = self.repo.create_file(
                    path=file_path,
                    message=commit_message or f"Create {config_type}: {name}",
                    content=yaml_content,
                    branch=GITHUB_BRANCH
                )
            
            return commit["commit"].sha
            
        except Exception as e:
            raise RuntimeError(f"Failed to save config to GitHub: {e}")
    
    def save_file(
        self,
        file_path: str,
        content: bytes,
        commit_message: Optional[str] = None
    ) -> str:
        """
        Save a binary file to GitHub.
        
        Args:
            file_path: Path in repository (e.g., "thumbnails/items/sword.png")
            content: File content as bytes
            commit_message: Optional commit message
            
        Returns:
            Commit SHA
        """
        if not self.repo:
            raise RuntimeError("GitHub storage not initialized")
        
        try:
            # Try to get existing file
            try:
                existing_file = self.repo.get_contents(file_path, ref=GITHUB_BRANCH)
                # Update existing file
                commit = self.repo.update_file(
                    path=file_path,
                    message=commit_message or f"Update file: {file_path}",
                    content=content,
                    sha=existing_file.sha,
                    branch=GITHUB_BRANCH
                )
            except GithubException:
                # File doesn't exist, create it
                commit = self.repo.create_file(
                    path=file_path,
                    message=commit_message or f"Create file: {file_path}",
                    content=content,
                    branch=GITHUB_BRANCH
                )
            
            return commit["commit"].sha
            
        except Exception as e:
            raise RuntimeError(f"Failed to save file to GitHub: {e}")
    
    def load_config(self, config_type: str, name: str) -> Dict[str, Any]:
        """
        Load a config file from GitHub.
        
        Returns the config content as a dictionary.
        Raises RuntimeError if config not found or GitHub error occurs.
        """
        if not self.repo:
            raise RuntimeError("GitHub storage not initialized")
        
        try:
            file_path = self._get_file_path(config_type, name)
            file_content = self.repo.get_contents(file_path, ref=GITHUB_BRANCH)
            content = yaml.safe_load(file_content.decoded_content.decode())
            if content is None:
                return {}
            return content
        except GithubException as e:
            if e.status == 404:
                raise FileNotFoundError(f"Config '{name}' of type '{config_type}' not found in GitHub")
            raise RuntimeError(f"Failed to load config from GitHub: {e}")
        except Exception as e:
            raise RuntimeError(f"Error loading config from GitHub: {e}")
    
    def delete_config(self, config_type: str, name: str) -> None:
        """
        Delete a config file from GitHub.
        
        Raises RuntimeError if operation fails.
        """
        if not self.repo:
            raise RuntimeError("GitHub storage not initialized")
        
        try:
            file_path = self._get_file_path(config_type, name)
            existing_file = self.repo.get_contents(file_path, ref=GITHUB_BRANCH)
            self.repo.delete_file(
                path=file_path,
                message=f"Delete {config_type}: {name}",
                sha=existing_file.sha,
                branch=GITHUB_BRANCH
            )
        except GithubException as e:
            if e.status == 404:
                raise FileNotFoundError(f"Config '{name}' of type '{config_type}' not found in GitHub")
            raise RuntimeError(f"Failed to delete config from GitHub: {e}")
        except Exception as e:
            raise RuntimeError(f"Error deleting config from GitHub: {e}")
    
    def list_configs(self, config_type: str) -> list[str]:
        """
        List all config files of a given type from GitHub.
        
        Returns a list of config names (without .yaml extension).
        """
        if not self.repo:
            raise RuntimeError("GitHub storage not initialized")
        
        try:
            dir_path = f"{GITHUB_BASE_PATH}/{config_type}s"
            contents = self.repo.get_contents(dir_path, ref=GITHUB_BRANCH)
            
            if isinstance(contents, list):
                # Directory listing
                return [item.name.replace(".yaml", "").replace(".yml", "") for item in contents if item.type == "file"]
            else:
                # Single file
                return [contents.name.replace(".yaml", "").replace(".yml", "")]
        except GithubException as e:
            if e.status == 404:
                # Directory doesn't exist yet, return empty list
                return []
            raise RuntimeError(f"Failed to list configs from GitHub: {e}")
        except Exception as e:
            raise RuntimeError(f"Error listing configs from GitHub: {e}")


# Global instance
github_storage = GitHubStorage()
