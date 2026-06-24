"""
Event generators for the Neon City Simulation Engine.

Generators create events based on simulation state, random factors,
and configurable thresholds.
"""

from __future__ import annotations

import random
import uuid
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Set

from .types import Event, EventSeverity, EventType


class EventGenerator(ABC):
    """Base class for all event generators."""

    @abstractmethod
    def generate(self, tick: int, world_state: dict) -> List[Event]:
        """
        Generate events based on current simulation state.

        Args:
            tick: Current simulation tick.
            world_state: Dictionary containing simulation state information.

        Returns:
            List of generated events.
        """
        ...


class RandomEventGenerator(EventGenerator):
    """
    Generates random events based on configurable probabilities.

    Each tick, rolls against probability thresholds to determine
    if random events occur. Uses a seeded RNG for determinism.
    """

    # Default probability thresholds
    PROB_POWER_OUTAGE = 0.05
    PROB_RIOT = 0.03
    PROB_TECH_BREAKTHROUGH = 0.02
    PROB_MARKET_CRASH = 0.01

    def __init__(
        self,
        seed: int = 42,
        prob_power_outage: float = PROB_POWER_OUTAGE,
        prob_riot: float = PROB_RIOT,
        prob_tech_breakthrough: float = PROB_TECH_BREAKTHROUGH,
        prob_market_crash: float = PROB_MARKET_CRASH,
        grid_size: tuple[int, int] = (100, 100),
    ) -> None:
        """
        Initialize the random event generator.

        Args:
            seed: Random seed for deterministic behavior.
            prob_power_outage: Probability of power outage per tick.
            prob_riot: Probability of riot per tick.
            prob_tech_breakthrough: Probability of tech breakthrough per tick.
            prob_market_crash: Probability of market crash per tick.
            grid_size: (width, height) of the simulation grid for targeting.
        """
        self._rng = random.Random(seed)
        self._prob_power_outage = prob_power_outage
        self._prob_riot = prob_riot
        self._prob_tech_breakthrough = prob_tech_breakthrough
        self._prob_market_crash = prob_market_crash
        self._grid_size = grid_size

    def _random_zone(self) -> str:
        """Generate a random zone identifier on the grid."""
        x = self._rng.randint(0, self._grid_size[0] - 1)
        y = self._rng.randint(0, self._grid_size[1] - 1)
        return f"zone_{x}_{y}"

    def generate(self, tick: int, world_state: dict) -> List[Event]:
        """
        Generate random events based on probability thresholds.

        Args:
            tick: Current simulation tick.
            world_state: Simulation state (may contain 'grid_size' override).

        Returns:
            List of randomly generated events.
        """
        events: List[Event] = []
        grid_size = world_state.get("grid_size", self._grid_size)

        # Power Outage (5% default)
        if self._rng.random() < self._prob_power_outage:
            events.append(Event(
                event_type=EventType.POWER_OUTAGE,
                severity=EventSeverity.HIGH,
                tick=tick,
                source_id="system_random",
                target_id=self._random_zone(),
                data={
                    "duration_ticks": self._rng.randint(5, 30),
                    "affected_area": grid_size,
                    "cause": self._rng.choice(["grid_failure", "cyber_attack", "overload"]),
                },
            ))

        # Riot (3% default)
        if self._rng.random() < self._prob_riot:
            events.append(Event(
                event_type=EventType.RIOT,
                severity=EventSeverity.CRITICAL,
                tick=tick,
                source_id="system_random",
                target_id=self._random_zone(),
                data={
                    "participants": self._rng.randint(10, 500),
                    "duration_ticks": self._rng.randint(3, 15),
                    "cause": self._rng.choice(["unemployment", "police_brutality", "food_shortage"]),
                },
            ))

        # Tech Breakthrough (2% default)
        if self._rng.random() < self._prob_tech_breakthrough:
            events.append(Event(
                event_type=EventType.TECH_BREAKTHROUGH,
                severity=EventSeverity.MEDIUM,
                tick=tick,
                source_id="system_random",
                data={
                    "tech_field": self._rng.choice([
                        "ai", "biotech", "quantum_computing", "energy", "robotics"
                    ]),
                    "impact_multiplier": round(self._rng.uniform(1.5, 5.0), 2),
                    "research_bonus": self._rng.randint(10, 100),
                },
            ))

        # Market Crash (1% default)
        if self._rng.random() < self._prob_market_crash:
            events.append(Event(
                event_type=EventType.MARKET_CRASH,
                severity=EventSeverity.CRITICAL,
                tick=tick,
                source_id="system_random",
                data={
                    "price_drop_pct": round(self._rng.uniform(0.1, 0.5), 2),
                    "duration_ticks": self._rng.randint(10, 50),
                    "affected_sectors": self._rng.sample(
                        ["tech", "energy", "finance", "health", "defense"],
                        k=self._rng.randint(1, 4),
                    ),
                },
            ))

        return events


class AgentEventGenerator(EventGenerator):
    """
    Generates events related to agent lifecycle and behavior.

    Handles agent spawning, death, and movement based on
    population thresholds and agent state.
    """

    def __init__(
        self,
        spawn_threshold: int = 50,
        max_population: int = 200,
        death_age_threshold: int = 500,
        move_probability: float = 0.3,
    ) -> None:
        """
        Initialize the agent event generator.

        Args:
            spawn_threshold: Population below this triggers spawn events.
            max_population: Maximum allowed population.
            death_age_threshold: Agent age at which death risk increases.
            move_probability: Probability a mobile agent moves each tick.
        """
        self._spawn_threshold = spawn_threshold
        self._max_population = max_population
        self._death_age_threshold = death_age_threshold
        self._move_probability = move_probability

    def generate(self, tick: int, world_state: dict) -> List[Event]:
        """
        Generate agent-related events based on world state.

        Expects world_state to contain:
            - 'agents': dict of agent_id -> agent_info dict with
              keys like 'age', 'health', 'position', 'mobile'
            - 'population': current total population count

        Args:
            tick: Current simulation tick.
            world_state: Simulation state with agent information.

        Returns:
            List of agent-related events.
        """
        events: List[Event] = []
        agents: Dict[str, Dict[str, Any]] = world_state.get("agents", {})
        population: int = world_state.get("population", len(agents))

        # Generate AGENT_SPAWN events if population is below threshold
        if population < self._spawn_threshold and population < self._max_population:
            # Spawn 1-3 agents
            spawn_count = min(
                self._get_spawn_count(population),
                self._max_population - population,
            )
            for _ in range(spawn_count):
                events.append(Event(
                    event_type=EventType.AGENT_SPAWN,
                    severity=EventSeverity.LOW,
                    tick=tick,
                    source_id="system_spawner",
                    target_id=f"agent_new_{uuid.uuid4().hex[:8]}",
                    data={
                        "spawn_reason": "population_below_threshold",
                        "initial_health": 100,
                        "initial_age": 0,
                    },
                ))

        # Generate AGENT_DEATH and AGENT_MOVE events for existing agents
        for agent_id, agent_info in agents.items():
            age: int = agent_info.get("age", 0)
            health: float = agent_info.get("health", 100.0)
            mobile: bool = agent_info.get("mobile", True)

            # Death check: older agents or low health are at risk
            if age > self._death_age_threshold or health <= 0:
                death_chance = 0.0
                if health <= 0:
                    death_chance = 1.0
                else:
                    # Linear increase in death probability past threshold
                    death_chance = min(1.0, (age - self._death_age_threshold) / 100.0)

                if random.random() < death_chance:
                    events.append(Event(
                        event_type=EventType.AGENT_DEATH,
                        severity=EventSeverity.MEDIUM,
                        tick=tick,
                        source_id=agent_id,
                        data={
                            "cause": "old_age" if health > 0 else "health_depleted",
                            "age": age,
                            "final_health": health,
                        },
                    ))

            # Movement check for mobile agents
            elif mobile and random.random() < self._move_probability:
                old_pos = agent_info.get("position", (0, 0))
                # Move to adjacent cell
                new_pos = (
                    max(0, old_pos[0] + random.randint(-1, 1)),
                    max(0, old_pos[1] + random.randint(-1, 1)),
                )
                events.append(Event(
                    event_type=EventType.AGENT_MOVE,
                    severity=EventSeverity.LOW,
                    tick=tick,
                    source_id=agent_id,
                    data={
                        "from_position": old_pos,
                        "to_position": new_pos,
                    },
                ))

        return events

    @staticmethod
    def _get_spawn_count(population: int) -> int:
        """Determine how many agents to spawn."""
        if population < 10:
            return 3
        elif population < 25:
            return 2
        return 1


class EconomyEventGenerator(EventGenerator):
    """
    Generates events related to economic conditions.

    Triggers market crashes, corporate takeovers, and other
    economic events based on simulation state thresholds.
    """

    def __init__(
        self,
        volatility_threshold: float = 0.15,
        corp_wealth_threshold: float = 1_000_000.0,
    ) -> None:
        """
        Initialize the economy event generator.

        Args:
            volatility_threshold: Price volatility above this triggers MARKET_CRASH.
            corp_wealth_threshold: Corporate wealth above this triggers CORP_TAKEOVER.
        """
        self._volatility_threshold = volatility_threshold
        self._corp_wealth_threshold = corp_wealth_threshold

    def generate(self, tick: int, world_state: dict) -> List[Event]:
        """
        Generate economy-related events based on world state.

        Expects world_state to contain:
            - 'price_volatility': float indicating current market volatility
            - 'corps': dict of corp_id -> corp_info with 'wealth' key

        Args:
            tick: Current simulation tick.
            world_state: Simulation state with economic information.

        Returns:
            List of economy-related events.
        """
        events: List[Event] = []

        # Check for market crash based on volatility
        price_volatility: float = world_state.get("price_volatility", 0.0)
        if price_volatility > self._volatility_threshold:
            severity = (
                EventSeverity.CRITICAL if price_volatility > self._volatility_threshold * 2
                else EventSeverity.HIGH
            )
            events.append(Event(
                event_type=EventType.MARKET_CRASH,
                severity=severity,
                tick=tick,
                source_id="system_economy",
                data={
                    "volatility": price_volatility,
                    "threshold": self._volatility_threshold,
                    "price_drop_pct": round(price_volatility * 0.5, 2),
                    "duration_ticks": int(price_volatility * 100),
                },
            ))

        # Check for corporate takeovers
        corps: Dict[str, Dict[str, Any]] = world_state.get("corps", {})
        for corp_id, corp_info in corps.items():
            wealth: float = corp_info.get("wealth", 0.0)
            if wealth > self._corp_wealth_threshold:
                # Find the wealthiest corp that could be a target
                target_id = self._find_takeover_target(corps, corp_id)
                events.append(Event(
                    event_type=EventType.CORP_TAKEOVER,
                    severity=EventSeverity.HIGH,
                    tick=tick,
                    source_id=corp_id,
                    target_id=target_id,
                    data={
                        "acquirer_wealth": wealth,
                        "threshold": self._corp_wealth_threshold,
                        "takeover_type": (
                            "hostile" if wealth > self._corp_wealth_threshold * 2
                            else "friendly"
                        ),
                    },
                ))

        return events

    def _find_takeover_target(
        self, corps: Dict[str, Dict[str, Any]], acquirer_id: str
    ) -> Optional[str]:
        """Find the most suitable takeover target (wealthiest other corp)."""
        candidates = {
            cid: info for cid, info in corps.items()
            if cid != acquirer_id
        }
        if not candidates:
            return None
        return max(candidates, key=lambda cid: candidates[cid].get("wealth", 0))


class CompositeGenerator(EventGenerator):
    """
    Combines multiple event generators into a single generator.

    Calls all child generators and deduplicates the resulting events
    by their event_id.
    """

    def __init__(self, generators: Optional[List[EventGenerator]] = None) -> None:
        """
        Initialize the composite generator.

        Args:
            generators: List of child EventGenerator instances.
        """
        self._generators: List[EventGenerator] = generators or []

    def add_generator(self, generator: EventGenerator) -> None:
        """Add a child generator."""
        self._generators.append(generator)

    def remove_generator(self, generator: EventGenerator) -> None:
        """Remove a child generator."""
        self._generators = [g for g in self._generators if g is not generator]

    def generate(self, tick: int, world_state: dict) -> List[Event]:
        """
        Generate events from all child generators, deduplicating by event_id.

        Args:
            tick: Current simulation tick.
            world_state: Simulation state passed to all child generators.

        Returns:
            Deduplicated list of events from all generators.
        """
        all_events: List[Event] = []
        seen_ids: Set[str] = set()

        for generator in self._generators:
            try:
                gen_events = generator.generate(tick, world_state)
                for event in gen_events:
                    if event.event_id not in seen_ids:
                        seen_ids.add(event.event_id)
                        all_events.append(event)
            except Exception:
                # Don't let one generator failure stop others
                continue

        return all_events
