"""
File: folder_structure.py

Defines folder structure management utilities for file storage system.
Able to create, verify, list, and traverse folders both locally and in external backends.
"""

import os
from typing import List, Optional

class FolderStructure:
    def __init__(self, backend):
        """
        backend: Must implement create_folder, list_folders, folder_exists.
        """
        self.backend = backend
    
    def create_folder(self, path: str) -> bool:
        """
        Creates a folder at the given path.
        Returns True on success.
        """
        return self.backend.create_folder(path)
    
    def folder_exists(self, path: str) -> bool:
        """
        Checks if folder exists.
        """
        return self.backend.folder_exists(path)
    
    def list_folders(self, parent_path: str) -> List[str]:
        """
        List all folders under parent_path.
        """
        return self.backend.list_folders(parent_path)
    
    def get_folder_tree(self, root_path: str) -> dict:
        """
        Recursively build folder tree for root_path.
        """
        tree = {}
        if not self.folder_exists(root_path):
            return tree
        children = self.list_folders(root_path)
        tree[root_path] = [self.get_folder_tree(os.path.join(root_path, child)) for child in children]
        return tree