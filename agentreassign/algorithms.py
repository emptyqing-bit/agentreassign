"""Task re-allocation algorithms: greedy, skill-aware, local search, random."""
from __future__ import annotations

import random
from typing import Protocol

from .model import Agent, Allocation, Task


class Algorithm(Protocol):
    name: str

    def allocate(self, tasks: list[Task], agents: dict[str, Agent]) -> Allocation: ...


def _ordered(tasks: list[Task]) -> list[Task]:
    return sorted(tasks, key=lambda t: (-t.priority, t.deadline, t.id))


def _feasible_agents(task: Task, agents: dict[str, Agent], alloc: Allocation) -> list[Agent]:
    return [
        a for a in agents.values()
        if task.skill in a.skills and len(alloc.assigned_to(a.id)) < a.capacity
    ]


class GreedyAlgorithm:
    """Priority-ordered first fit: least-loaded feasible agent per task."""
    name = "greedy"

    def allocate(self, tasks: list[Task], agents: dict[str, Agent]) -> Allocation:
        alloc = Allocation()
        for task in _ordered(tasks):
            candidates = _feasible_agents(task, agents, alloc)
            if candidates:
                best = min(candidates, key=lambda a: (len(alloc.assigned_to(a.id)), a.id))
                alloc.assign(task.id, best.id)
        return alloc


class SkillAwareAlgorithm:
    """Prefers agents whose skill set is narrowest (preserves scarce skills)."""
    name = "skill-aware"

    def allocate(self, tasks: list[Task], agents: dict[str, Agent]) -> Allocation:
        alloc = Allocation()
        # Most constrained tasks first: fewest feasible agents.
        for task in sorted(tasks, key=lambda t: (
                sum(1 for a in agents.values() if t.skill in a.skills), -t.priority)):
            candidates = _feasible_agents(task, agents, alloc)
            if candidates:
                best = min(candidates, key=lambda a: (
                    len(a.skills), len(alloc.assigned_to(a.id)), a.id))
                alloc.assign(task.id, best.id)
        return alloc


class LocalSearchAlgorithm:
    """Greedy seed + swap moves that increase coverage."""
    name = "local-search"

    def __init__(self, base: Algorithm | None = None, max_rounds: int = 50):
        self.base = base or GreedyAlgorithm()
        self.max_rounds = max_rounds

    def allocate(self, tasks: list[Task], agents: dict[str, Agent]) -> Allocation:
        alloc = Allocation(dict(self.base.allocate(tasks, agents).assignments))
        for _ in range(self.max_rounds):
            unassigned = [t for t in _ordered(tasks) if t.id not in alloc.assignments]
            if not unassigned:
                break
            improved = False
            for task in unassigned:
                for agent in agents.values():
                    if task.skill not in agent.skills:
                        continue
                    # Try displacing a lower-priority task to a free agent.
                    for other_id in list(alloc.assigned_to(agent.id)):
                        other = next(t for t in tasks if t.id == other_id)
                        if other.priority > task.priority:
                            continue
                        for target in agents.values():
                            if target.id == agent.id or other.skill not in target.skills:
                                continue
                            probe = Allocation(dict(alloc.assignments))
                            probe.unassign(other_id)
                            probe.assign(task.id, agent.id)
                            probe.assign(other_id, target.id)
                            if probe.is_feasible(tasks, agents):
                                alloc = probe
                                improved = True
                                break
                        if improved:
                            break
                    if improved:
                        break
                if improved:
                    break
            if not improved:
                break
        return alloc


class RandomAlgorithm:
    """Random feasible assignment (seeded), as a lower bound."""
    name = "random"

    def __init__(self, seed: int = 11):
        self.rng = random.Random(seed)

    def allocate(self, tasks: list[Task], agents: dict[str, Agent]) -> Allocation:
        alloc = Allocation()
        for task in _ordered(tasks):
            candidates = _feasible_agents(task, agents, alloc)
            if candidates:
                alloc.assign(task.id, self.rng.choice(candidates).id)
        return alloc


ALGORITHMS = [GreedyAlgorithm(), SkillAwareAlgorithm(), LocalSearchAlgorithm(), RandomAlgorithm()]
