from typing import List, Dict
from pydantic import BaseModel, Field

class CommandEntry(BaseModel):
    order: int = Field(description="Order number starting from 1")
    command: str = Field(description="The actual bash command to execute")
    needs_dir_change: int = Field(default=0, description="1 if command changes directory, 0 otherwise")
    needs_file_check: int = Field(default=0, description="1 if command needs file verification, 0 otherwise")

class CommandSequence(BaseModel):
    commands: List[CommandEntry]
    total_commands: int