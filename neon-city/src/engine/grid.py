"""City grid module for the Neon City Simulation Engine.

Provides CellType enum, Cell dataclass, and Grid class with deterministic
city generation, A* pathfinding, and agent placement.
"""

from __future__ import annotations

import heapq
import random
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class CellType(Enum):
    """Types of cells in the city grid."""
    EMPTY = "EMPTY"
    BUILDING_RESIDENTIAL = "BUILDING_RESIDENTIAL"
    BUILDING_COMMERCIAL = "BUILDING_COMMERCIAL"
    BUILDING_INDUSTRIAL = "BUILDING_INDUSTRIAL"
    STREET = "STREET"
    POWER_STATION = "POWER_STATION"
    DATA_CENTER = "DATA_CENTER"
    MARKET = "MARKET"
    POLICE_STATION = "POLICE_STATION"
    BLACK_MARKET = "BLACK_MARKET"


# Walkable cell types
_WALKABLE_TYPES: set[CellType] = {
    CellType.STREET,
    CellType.MARKET,
    CellType.BLACK_MARKET,
    CellType.BUILDING_RESIDENTIAL,
    CellType.BUILDING_COMMERCIAL,
    CellType.POWER_STATION,
    CellType.POLICE_STATION,
    CellType.DATA_CENTER,
}

# ASCII symbols for display
_CELL_SYMBOLS: dict[CellType, str] = {
    CellType.EMPTY: "·",
    CellType.BUILDING_RESIDENTIAL: "🏠",
    CellType.BUILDING_COMMERCIAL: "🏢",
    CellType.BUILDING_INDUSTRIAL: "🏭",
    CellType.STREET: "░",
    CellType.POWER_STATION: "⚡",
    CellType.DATA_CENTER: "🖥️",
    CellType.MARKET: "🏪",
    CellType.POLICE_STATION: "🚔",
    CellType.BLACK_MARKET: "💀",
}


@dataclass
class Cell:
    """A single cell in the city grid."""
    cell_type: CellType
    occupants: list[str] = field(default_factory=list)
    elevation: int = 0
    power: bool = True
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        """Serialize cell to dictionary."""
        return {
            "cell_type": self.cell_type.value,
            "occupants": list(self.occupants),
            "elevation": self.elevation,
            "power": self.power,
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, data: dict) -> Cell:
        """Deserialize cell from dictionary."""
        return cls(
            cell_type=CellType(data["cell_type"]),
            occupants=list(data.get("occupants", [])),
            elevation=int(data.get("elevation", 0)),
            power=bool(data.get("power", True)),
            metadata=dict(data.get("metadata", {})),
        )


class Grid:
    """2D grid representing the city with deterministic generation and A* pathfinding."""

    def __init__(self, width: int, height: int, seed: int = 42) -> None:
        self.width: int = width
        self.height: int = height
        self._seed: int = seed
        self._rng: random.Random = random.Random(seed)
        self._cells: list[list[Cell]] = []
        self._generate_city()

    # ------------------------------------------------------------------
    # City generation
    # ------------------------------------------------------------------

    def _generate_city(self) -> None:
        """Generate a deterministic city layout using the seed."""
        w, h = self.width, self.height

        # Start with all empty
        self._cells = [
            [Cell(cell_type=CellType.EMPTY) for _ in range(h)] for _ in range(w)
        ]

        # Place streets in a grid pattern every 4-5 cells
        street_spacing = max(4, min(w, h) // 8)
        for x in range(w):
            for y in range(h):
                if x % street_spacing == 0 or y % street_spacing == 0:
                    self._cells[x][y] = Cell(cell_type=CellType.STREET)

        # Place residential zones in corners
        self._fill_region(1, 1, max(2, w // 5), max(2, h // 5), CellType.BUILDING_RESIDENTIAL)
        self._fill_region(w - max(2, w // 5) - 1, 1, max(2, w // 5), max(2, h // 5), CellType.BUILDING_RESIDENTIAL)
        self._fill_region(1, h - max(2, h // 5) - 1, max(2, w // 5), max(2, h // 5), CellType.BUILDING_RESIDENTIAL)
        self._fill_region(w - max(2, w // 5) - 1, h - max(2, h // 5) - 1, max(2, w // 5), max(2, h // 5), CellType.BUILDING_RESIDENTIAL)

        # Place commercial center
        cx, cy = w // 2, h // 2
        cw, ch = max(2, w // 6), max(2, h // 6)
        self._fill_region(cx - cw // 2, cy - ch // 2, cw, ch, CellType.BUILDING_COMMERCIAL)

        # Place industrial edges (top and bottom strips)
        industrial_height = max(1, h // 8)
        for x in range(w):
            for y in range(industrial_height):
                if self._cells[x][y].cell_type == CellType.EMPTY:
                    self._cells[x][y] = Cell(cell_type=CellType.BUILDING_INDUSTRIAL)
            for y in range(h - industrial_height, h):
                if self._cells[x][y].cell_type == CellType.EMPTY:
                    self._cells[x][y] = Cell(cell_type=CellType.BUILDING_INDUSTRIAL)

        # Place power stations (near industrial)
        self._place_near_type(CellType.POWER_STATION, CellType.BUILDING_INDUSTRIAL, count=max(1, w * h // 200))

        # Place data center (near commercial)
        self._place_near_type(CellType.DATA_CENTER, CellType.BUILDING_COMMERCIAL, count=max(1, w * h // 300))

        # Place markets (scattered near commercial/residential borders)
        self._place_near_type(CellType.MARKET, CellType.BUILDING_COMMERCIAL, count=max(2, w * h // 250))

        # Place police stations (near commercial)
        self._place_near_type(CellType.POLICE_STATION, CellType.BUILDING_COMMERCIAL, count=max(1, w * h // 400))

        # Place black markets (in shadowy corners, away from police)
        self._place_black_markets(count=max(1, w * h // 500))

        # Assign elevation based on distance from center
        for x in range(w):
            for y in range(h):
                dist = abs(x - cx) + abs(y - cy)
                max_dist = cx + cy
                self._cells[x][y].elevation = min(3, int(4 * dist / max(1, max_dist)))

    def _fill_region(self, start_x: int, start_y: int, rw: int, rh: int, ct: CellType) -> None:
        """Fill a rectangular region with a cell type, preserving streets."""
        for x in range(max(0, start_x), min(self.width, start_x + rw)):
            for y in range(max(0, start_y), min(self.height, start_y + rh)):
                if self._cells[x][y].cell_type in (CellType.EMPTY, CellType.STREET):
                    self._cells[x][y] = Cell(cell_type=ct)

    def _place_near_type(self, place_type: CellType, near_type: CellType, count: int) -> None:
        """Place cells of place_type near cells of near_type."""
        near_cells = [
            (x, y)
            for x in range(self.width)
            for y in range(self.height)
            if self._cells[x][y].cell_type == near_type
        ]
        if not near_cells:
            return
        placed = 0
        attempts = 0
        while placed < count and attempts < count * 20:
            attempts += 1
            nx, ny = self._rng.choice(near_cells)
            dx = self._rng.randint(-2, 2)
            dy = self._rng.randint(-2, 2)
            px, py = nx + dx, ny + dy
            if self.in_bounds(px, py) and self._cells[px][py].cell_type in (
                CellType.EMPTY, CellType.STREET
            ):
                self._cells[px][py] = Cell(cell_type=place_type)
                placed += 1

    def _place_black_markets(self, count: int) -> None:
        """Place black markets in corners away from police stations."""
        police_cells = [
            (x, y)
            for x in range(self.width)
            for y in range(self.height)
            if self._cells[x][y].cell_type == CellType.POLICE_STATION
        ]
        corners = [
            (x, y)
            for x in range(self.width)
            for y in range(self.height)
            if self._cells[x][y].cell_type in (CellType.EMPTY, CellType.STREET)
        ]
        # Sort corners by distance from nearest police (descending)
        def min_police_dist(cx: int, cy: int) -> float:
            if not police_cells:
                return float("inf")
            return min(abs(cx - px) + abs(cy - py) for px, py in police_cells)

        corners.sort(key=lambda c: min_police_dist(c[0], c[1]), reverse=True)
        placed = 0
        for cx, cy in corners:
            if placed >= count:
                break
            self._cells[cx][cy] = Cell(cell_type=CellType.BLACK_MARKET)
            placed += 1

    # ------------------------------------------------------------------
    # Cell access
    # ------------------------------------------------------------------

    def get_cell(self, x: int, y: int) -> Cell:
        """Return the cell at (x, y). Raises IndexError if out of bounds."""
        if not self.in_bounds(x, y):
            raise IndexError(f"Cell ({x}, {y}) is out of bounds ({self.width}x{self.height})")
        return self._cells[x][y]

    def set_cell(self, x: int, y: int, cell: Cell) -> None:
        """Set the cell at (x, y). Raises IndexError if out of bounds."""
        if not self.in_bounds(x, y):
            raise IndexError(f"Cell ({x}, {y}) is out of bounds ({self.width}x{self.height})")
        self._cells[x][y] = cell

    def in_bounds(self, x: int, y: int) -> bool:
        """Check if (x, y) is within grid bounds."""
        return 0 <= x < self.width and 0 <= y < self.height

    # ------------------------------------------------------------------
    # Neighbors
    # ------------------------------------------------------------------

    def get_neighbors(
        self, x: int, y: int, radius: int = 1
    ) -> list[tuple[int, int, Cell]]:
        """Return list of (x, y, Cell) tuples for all cells within radius."""
        result: list[tuple[int, int, Cell]] = []
        for dx in range(-radius, radius + 1):
            for dy in range(-radius, radius + 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if self.in_bounds(nx, ny):
                    result.append((nx, ny, self._cells[nx][ny]))
        return result

    # ------------------------------------------------------------------
    # Walkability & pathfinding
    # ------------------------------------------------------------------

    def get_walkable(self, x: int, y: int) -> bool:
        """Check if a cell is walkable."""
        if not self.in_bounds(x, y):
            return False
        return self._cells[x][y].cell_type in _WALKABLE_TYPES

    def find_path(
        self, x1: int, y1: int, x2: int, y2: int
    ) -> list[tuple[int, int]]:
        """A* pathfinding from (x1, y1) to (x2, y2). Returns list of (x, y) waypoints."""
        if not self.in_bounds(x1, y1) or not self.in_bounds(x2, y2):
            return []
        if (x1, y1) == (x2, y2):
            return [(x1, y1)]

        # A* with Manhattan distance heuristic
        open_set: list[tuple[float, int, int]] = [(0.0, x1, y1)]
        came_from: dict[tuple[int, int], tuple[int, int]] = {}
        g_score: dict[tuple[int, int], float] = {(x1, y1): 0.0}
        closed: set[tuple[int, int]] = set()

        while open_set:
            _, cx, cy = heapq.heappop(open_set)
            if (cx, cy) == (x2, y2):
                # Reconstruct path
                path: list[tuple[int, int]] = []
                current = (cx, cy)
                while current in came_from:
                    path.append(current)
                    current = came_from[current]
                path.append((x1, y1))
                path.reverse()
                return path

            if (cx, cy) in closed:
                continue
            closed.add((cx, cy))

            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nx, ny = cx + dx, cy + dy
                if (nx, ny) in closed:
                    continue
                if not self.in_bounds(nx, ny):
                    continue
                if not self.get_walkable(nx, ny):
                    continue

                # Cost: base 1, elevation penalty
                elevation_cost = self._cells[nx][ny].elevation * 0.5
                tentative_g = g_score[(cx, cy)] + 1.0 + elevation_cost

                if tentative_g < g_score.get((nx, ny), float("inf")):
                    came_from[(nx, ny)] = (cx, cy)
                    g_score[(nx, ny)] = tentative_g
                    h = abs(nx - x2) + abs(ny - y2)
                    heapq.heappush(open_set, (tentative_g + h, nx, ny))

        return []  # No path found

    # ------------------------------------------------------------------
    # Agent management
    # ------------------------------------------------------------------

    def get_agents_at(self, x: int, y: int) -> list[str]:
        """Return list of agent IDs at position (x, y)."""
        if not self.in_bounds(x, y):
            return []
        return list(self._cells[x][y].occupants)

    def place_agent(self, agent_id: str, x: int, y: int) -> bool:
        """Place an agent at (x, y). Returns False if out of bounds."""
        if not self.in_bounds(x, y):
            return False
        if agent_id not in self._cells[x][y].occupants:
            self._cells[x][y].occupants.append(agent_id)
        return True

    def remove_agent(self, agent_id: str, x: int, y: int) -> bool:
        """Remove an agent from (x, y). Returns False if agent not found."""
        if not self.in_bounds(x, y):
            return False
        if agent_id in self._cells[x][y].occupants:
            self._cells[x][y].occupants.remove(agent_id)
            return True
        return False

    def move_agent(
        self, agent_id: str, from_x: int, from_y: int, to_x: int, to_y: int
    ) -> bool:
        """Move an agent from one cell to another. Returns False on failure."""
        if not self.in_bounds(from_x, from_y) or not self.in_bounds(to_x, to_y):
            return False
        if not self.get_walkable(to_x, to_y):
            return False
        if agent_id not in self._cells[from_x][from_y].occupants:
            return False

        self._cells[from_x][from_y].occupants.remove(agent_id)
        self._cells[to_x][to_y].occupants.append(agent_id)
        return True

    # ------------------------------------------------------------------
    # Serialization
    # ------------------------------------------------------------------

    def to_dict(self) -> dict:
        """Serialize the full grid state to a dictionary."""
        cells = []
        for x in range(self.width):
            col = []
            for y in range(self.height):
                col.append(self._cells[x][y].to_dict())
            cells.append(col)
        return {
            "width": self.width,
            "height": self.height,
            "seed": self._seed,
            "cells": cells,
        }

    @classmethod
    def from_dict(cls, data: dict) -> Grid:
        """Reconstruct a Grid from a serialized dictionary."""
        grid = cls.__new__(cls)
        grid.width = int(data["width"])
        grid.height = int(data["height"])
        grid._seed = int(data.get("seed", 42))
        grid._rng = random.Random(grid._seed)
        grid._cells = []
        for x, col_data in enumerate(data["cells"]):
            col = []
            for y, cell_data in enumerate(col_data):
                col.append(Cell.from_dict(cell_data))
            grid._cells.append(col)
        return grid

    # ------------------------------------------------------------------
    # Display
    # ------------------------------------------------------------------

    def __str__(self) -> str:
        """ASCII art representation of the grid."""
        lines: list[str] = []
        # Header
        lines.append(f"Grid {self.width}x{self.height} (seed={self._seed})")
        lines.append("+" + "-" * self.height + "+")
        for y in range(self.height):
            row = "|"
            for x in range(self.width):
                cell = self._cells[x][y]
                if cell.occupants:
                    row += str(len(cell.occupants))
                else:
                    row += _CELL_SYMBOLS.get(cell.cell_type, "?")
            row += "|"
            lines.append(row)
        lines.append("+" + "-" * self.height + "+")
        return "\n".join(lines)
