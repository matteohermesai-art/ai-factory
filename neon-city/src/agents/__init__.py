"""
Agent system for the Neon City Simulation Engine.

Provides the base agent class and specialized agent types:
- Citizen: Regular inhabitants that work and trade
- Hacker: Cyber criminals that attack and steal
- Corporation: Powerful entities that control markets
- Police: Law enforcement that patrols and arrests
"""

from .base import AgentStatus, AgentMemory, BaseAgent
from .citizen import Citizen
from .hacker import Hacker
from .corporation import Corporation
from .police import Police

__all__ = [
    "AgentStatus",
    "AgentMemory",
    "BaseAgent",
    "Citizen",
    "Hacker",
    "Corporation",
    "Police",
]
