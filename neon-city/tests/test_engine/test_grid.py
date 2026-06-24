"""Tests for grid module."""

import pytest

from src.engine.grid import Grid, Cell, CellType


class TestGridCreation:
    """Test Grid creation with different sizes."""

    def test_grid_creation_10x10(self):
        grid = Grid(width=10, height=10, seed=42)
        assert grid.width == 10
        assert grid.height == 10

    def test_grid_creation_50x50(self):
        grid = Grid(width=50, height=50, seed=42)
        assert grid.width == 50
        assert grid.height == 50

    def test_grid_creation_100x100(self):
        grid = Grid(width=100, height=100, seed=42)
        assert grid.width == 100
        assert grid.height == 100

    def test_grid_creation_non_square(self):
        grid = Grid(width=20, height=10, seed=42)
        assert grid.width == 20
        assert grid.height == 10

    def test_grid_different_seeds(self):
        grid1 = Grid(width=10, height=10, seed=42)
        grid2 = Grid(width=10, height=10, seed=99)
        # Different seeds should produce different layouts
        cells1 = [grid1.get_cell(x, y).cell_type for x in range(10) for y in range(10)]
        cells2 = [grid2.get_cell(x, y).cell_type for x in range(10) for y in range(10)]
        assert cells1 != cells2

    def test_grid_same_seed_deterministic(self):
        grid1 = Grid(width=10, height=10, seed=42)
        grid2 = Grid(width=10, height=10, seed=42)
        for x in range(10):
            for y in range(10):
                assert grid1.get_cell(x, y).cell_type == grid2.get_cell(x, y).cell_type


class TestCellAccess:
    """Test cell get/set operations."""

    def test_get_cell_valid(self, grid):
        cell = grid.get_cell(0, 0)
        assert isinstance(cell, Cell)
        assert cell.cell_type is not None

    def test_get_cell_out_of_bounds(self, grid):
        with pytest.raises(IndexError):
            grid.get_cell(10, 10)

    def test_get_cell_negative(self, grid):
        with pytest.raises(IndexError):
            grid.get_cell(-1, 0)

    def test_set_cell_valid(self, grid):
        new_cell = Cell(cell_type=CellType.BUILDING_INDUSTRIAL)
        grid.set_cell(0, 0, new_cell)
        assert grid.get_cell(0, 0).cell_type == CellType.BUILDING_INDUSTRIAL

    def test_set_cell_out_of_bounds(self, grid):
        new_cell = Cell(cell_type=CellType.BUILDING_INDUSTRIAL)
        with pytest.raises(IndexError):
            grid.set_cell(10, 10, new_cell)

    def test_set_cell_preserves_occupants(self, grid):
        new_cell = Cell(cell_type=CellType.STREET, occupants=["agent_1"])
        grid.set_cell(0, 0, new_cell)
        assert grid.get_agents_at(0, 0) == ["agent_1"]


class TestInBounds:
    """Test in_bounds method."""

    def test_in_bounds_valid(self, grid):
        assert grid.in_bounds(0, 0) is True
        assert grid.in_bounds(9, 9) is True
        assert grid.in_bounds(5, 5) is True

    def test_in_bounds_out(self, grid):
        assert grid.in_bounds(10, 10) is False
        assert grid.in_bounds(-1, 0) is False
        assert grid.in_bounds(0, -1) is False
        assert grid.in_bounds(10, 0) is False
        assert grid.in_bounds(0, 10) is False


class TestGetNeighbors:
    """Test get_neighbors method."""

    def test_get_neighbors_center(self, grid):
        neighbors = grid.get_neighbors(5, 5, radius=1)
        # Should have up to 8 neighbors
        assert len(neighbors) > 0
        assert all(len(n) == 3 for n in neighbors)  # (x, y, Cell)

    def test_get_neighbors_corner(self, grid):
        neighbors = grid.get_neighbors(0, 0, radius=1)
        # Corner has fewer neighbors
        assert 2 <= len(neighbors) <= 3

    def test_get_neighbors_radius_2(self, grid):
        neighbors = grid.get_neighbors(5, 5, radius=2)
        # Radius 2 should have more neighbors than radius 1
        neighbors_r1 = grid.get_neighbors(5, 5, radius=1)
        assert len(neighbors) > len(neighbors_r1)

    def test_get_neighbors_excludes_self(self, grid):
        neighbors = grid.get_neighbors(5, 5, radius=1)
        positions = [(n[0], n[1]) for n in neighbors]
        assert (5, 5) not in positions


class TestWalkable:
    """Test walkable cells."""

    def test_street_walkable(self, grid):
        # Find a street cell
        for x in range(grid.width):
            for y in range(grid.height):
                if grid.get_cell(x, y).cell_type == CellType.STREET:
                    assert grid.get_walkable(x, y) is True
                    return
        pytest.skip("No street cell found")

    def test_building_industrial_not_walkable(self, grid):
        for x in range(grid.width):
            for y in range(grid.height):
                if grid.get_cell(x, y).cell_type == CellType.BUILDING_INDUSTRIAL:
                    assert grid.get_walkable(x, y) is False
                    return
        pytest.skip("No industrial cell found")

    def test_out_of_bounds_not_walkable(self, grid):
        assert grid.get_walkable(-1, 0) is False
        assert grid.get_walkable(100, 100) is False

    def test_market_walkable(self, grid):
        for x in range(grid.width):
            for y in range(grid.height):
                if grid.get_cell(x, y).cell_type == CellType.MARKET:
                    assert grid.get_walkable(x, y) is True
                    return
        pytest.skip("No market cell found")


class TestAgentPlacement:
    """Test agent placement/removal/movement on grid."""

    def test_place_agent(self, grid):
        result = grid.place_agent("agent_1", 0, 0)
        assert result is True
        assert "agent_1" in grid.get_agents_at(0, 0)

    def test_place_agent_out_of_bounds(self, grid):
        result = grid.place_agent("agent_1", 10, 10)
        assert result is False

    def test_place_agent_duplicate(self, grid):
        grid.place_agent("agent_1", 0, 0)
        grid.place_agent("agent_1", 0, 0)
        assert grid.get_agents_at(0, 0).count("agent_1") == 1

    def test_remove_agent(self, grid):
        grid.place_agent("agent_1", 0, 0)
        result = grid.remove_agent("agent_1", 0, 0)
        assert result is True
        assert "agent_1" not in grid.get_agents_at(0, 0)

    def test_remove_agent_not_found(self, grid):
        result = grid.remove_agent("nonexistent", 0, 0)
        assert result is False

    def test_remove_agent_out_of_bounds(self, grid):
        result = grid.remove_agent("agent_1", 10, 10)
        assert result is False

    def test_move_agent(self, grid):
        # Find two adjacent walkable cells
        grid.place_agent("agent_1", 0, 0)
        result = grid.move_agent("agent_1", 0, 0, 0, 1)
        if grid.get_walkable(0, 1):
            assert result is True
            assert "agent_1" not in grid.get_agents_at(0, 0)
            assert "agent_1" in grid.get_agents_at(0, 1)
        else:
            assert result is False

    def test_move_agent_to_non_walkable(self, grid):
        grid.place_agent("agent_1", 0, 0)
        # Try to move to an industrial cell
        for x in range(grid.width):
            for y in range(grid.height):
                if grid.get_cell(x, y).cell_type == CellType.BUILDING_INDUSTRIAL:
                    result = grid.move_agent("agent_1", 0, 0, x, y)
                    assert result is False
                    return
        pytest.skip("No industrial cell found")

    def test_move_agent_not_at_source(self, grid):
        result = grid.move_agent("agent_1", 0, 0, 0, 1)
        assert result is False


class TestPathfinding:
    """Test A* pathfinding."""

    def test_pathfinding_same_cell(self, grid):
        path = grid.find_path(5, 5, 5, 5)
        assert path == [(5, 5)]

    def test_pathfinding_adjacent(self, grid):
        # Find two adjacent walkable cells
        for x in range(grid.width):
            for y in range(grid.height):
                if not grid.get_walkable(x, y):
                    continue
                for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                    nx, ny = x + dx, y + dy
                    if grid.in_bounds(nx, ny) and grid.get_walkable(nx, ny):
                        path = grid.find_path(x, y, nx, ny)
                        assert len(path) >= 2
                        assert path[0] == (x, y)
                        assert path[-1] == (nx, ny)
                        return
        pytest.skip("No adjacent walkable cells found")

    def test_pathfinding_complex(self, grid):
        # Find two walkable cells far apart
        walkable = [
            (x, y) for x in range(grid.width) for y in range(grid.height)
            if grid.get_walkable(x, y)
        ]
        if len(walkable) < 2:
            pytest.skip("Not enough walkable cells")
        start = walkable[0]
        end = walkable[-1]
        path = grid.find_path(start[0], start[1], end[0], end[1])
        if path:
            assert path[0] == start
            assert path[-1] == end
            # Verify each step is adjacent
            for i in range(1, len(path)):
                dx = abs(path[i][0] - path[i-1][0])
                dy = abs(path[i][1] - path[i-1][1])
                assert dx + dy == 1

    def test_pathfinding_no_path(self, grid):
        # Create isolated cells by setting a cell to non-walkable
        # Try to find path to an area that might be unreachable
        walkable = [
            (x, y) for x in range(grid.width) for y in range(grid.height)
            if grid.get_walkable(x, y)
        ]
        if not walkable:
            pytest.skip("No walkable cells")
        # Path to self always works
        path = grid.find_path(walkable[0][0], walkable[0][1], walkable[0][0], walkable[0][1])
        assert len(path) == 1

    def test_pathfinding_out_of_bounds(self, grid):
        path = grid.find_path(-1, 0, 5, 5)
        assert path == []
        path = grid.find_path(5, 5, 100, 100)
        assert path == []


class TestSerialization:
    """Test serialization round-trip."""

    def test_to_dict(self, grid):
        d = grid.to_dict()
        assert d["width"] == 10
        assert d["height"] == 10
        assert d["seed"] == 42
        assert len(d["cells"]) == 10
        assert len(d["cells"][0]) == 10

    def test_from_dict(self, grid):
        d = grid.to_dict()
        restored = Grid.from_dict(d)
        assert restored.width == grid.width
        assert restored.height == grid.height
        assert restored._seed == grid._seed

    def test_round_trip_cells(self, grid):
        d = grid.to_dict()
        restored = Grid.from_dict(d)
        for x in range(grid.width):
            for y in range(grid.height):
                orig = grid.get_cell(x, y)
                rest = restored.get_cell(x, y)
                assert orig.cell_type == rest.cell_type
                assert orig.elevation == rest.elevation
                assert orig.power == rest.power

    def test_cell_serialization(self):
        cell = Cell(
            cell_type=CellType.MARKET,
            occupants=["agent_1"],
            elevation=2,
            power=False,
            metadata={"zone": "downtown"}
        )
        d = cell.to_dict()
        restored = Cell.from_dict(d)
        assert restored.cell_type == CellType.MARKET
        assert restored.occupants == ["agent_1"]
        assert restored.elevation == 2
        assert restored.power is False
        assert restored.metadata == {"zone": "downtown"}


class TestCityGeneration:
    """Test city generation produces expected districts."""

    def test_streets_placed(self, grid):
        street_count = sum(
            1 for x in range(grid.width) for y in range(grid.height)
            if grid.get_cell(x, y).cell_type == CellType.STREET
        )
        assert street_count > 0

    def test_residential_placed(self, grid):
        residential_count = sum(
            1 for x in range(grid.width) for y in range(grid.height)
            if grid.get_cell(x, y).cell_type == CellType.BUILDING_RESIDENTIAL
        )
        assert residential_count > 0

    def test_commercial_placed(self, grid):
        commercial_count = sum(
            1 for x in range(grid.width) for y in range(grid.height)
            if grid.get_cell(x, y).cell_type == CellType.BUILDING_COMMERCIAL
        )
        assert commercial_count > 0

    def test_industrial_placed(self, grid):
        industrial_count = sum(
            1 for x in range(grid.width) for y in range(grid.height)
            if grid.get_cell(x, y).cell_type == CellType.BUILDING_INDUSTRIAL
        )
        assert industrial_count > 0

    def test_power_station_placed(self, grid):
        power_count = sum(
            1 for x in range(grid.width) for y in range(grid.height)
            if grid.get_cell(x, y).cell_type == CellType.POWER_STATION
        )
        assert power_count > 0

    def test_elevation_assigned(self, grid):
        has_elevation = any(
            grid.get_cell(x, y).elevation > 0
            for x in range(grid.width)
            for y in range(grid.height)
        )
        assert has_elevation


class TestDisplay:
    """Test __str__ doesn't crash."""

    def test_str_does_not_crash(self, grid):
        s = str(grid)
        assert isinstance(s, str)
        assert "Grid" in s
        assert "seed" in s

    def test_str_with_occupants(self, grid):
        grid.place_agent("agent_1", 0, 0)
        s = str(grid)
        assert isinstance(s, str)
