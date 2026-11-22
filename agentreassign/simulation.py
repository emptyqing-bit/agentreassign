"""Disruption-driven simulation: agent dropout, urgent tasks, escalation."""
from __future__ import annotations

import random
from dataclasses import dataclass

from .model import Agent, Allocation, Task

SKILLS = ["security", "medic", "technician", "teacher"]


@dataclass
class Disruption:
    kind: str  # "agent_offline" | "urgent_task"
    agent_id: str = ""
    task: Task | None = None


def generate_scenario(n_agents: int = 6, n_tasks: int = 10, seed: int = 5) -> tuple[dict[str, Agent], list[Task]]:
    rng = random.Random(seed)
    agents: dict[str, Agent] = {}
    for i in range(n_agents):
        skills = rng.sample(SKILLS, k=rng.choice([1, 1, 2]))
        agents[f"agent-{i}"] = Agent.make(f"agent-{i}", skills, capacity=rng.choice([2, 3]))
    tasks = [
        Task(id=f"task-{j}", skill=rng.choice(SKILLS),
             priority=rng.choice([1, 2, 3]), deadline=rng.choice([5, 10, 20]))
        for j in range(n_tasks)
    ]
    return agents, tasks


def simulate(algorithm, agents: dict[str, Agent], tasks: list[Task],
             disruptions: list[Disruption]) -> dict:
    """Allocate, apply disruptions in order, and re-allocate pending tasks."""
    alloc: Allocation = algorithm.allocate(tasks, agents)
    reassignments = 0
    pending = list(tasks)
    available = dict(agents)

    for event in disruptions:
        if event.kind == "agent_offline" and event.agent_id in available:
            offline = available.pop(event.agent_id)
            affected = [t for t in pending if alloc.assignments.get(t.id) == offline.id]
            for t in affected:
                alloc.unassign(t.id)
            reassignments += len(affected)
        elif event.kind == "urgent_task" and event.task is not None:
            pending.append(event.task)
        # Re-allocate every unassigned pending task with the remaining agents,
        # discounting each agent's capacity by its current load.
        remaining = [t for t in pending if t.id not in alloc.assignments]
        if remaining:
            adjusted = {
                aid: Agent.make(a.id, list(a.skills),
                                capacity=max(0, a.capacity - len(alloc.assigned_to(aid))))
                for aid, a in available.items()
            }
            fresh = algorithm.allocate(remaining, adjusted)
            for tid, aid in fresh.assignments.items():
                alloc.assign(tid, aid)

    return {
        "algorithm": algorithm.name,
        "coverage": round(alloc.coverage(pending), 4),
        "feasible": alloc.is_feasible(pending, available),
        "violations": len(alloc.violations(pending, available)),
        "reassigned_tasks": reassignments,
    }


def compare(algorithms: list, agents: dict[str, Agent], tasks: list[Task],
            disruptions: list[Disruption]) -> list[dict]:
    return [simulate(a, agents, tasks, disruptions) for a in algorithms]


def markdown_table(rows: list[dict]) -> str:
    lines = [
        "| Algorithm | Coverage | Feasible | Violations | Reassigned |",
        "| --- | --- | --- | --- | --- |",
    ]
    for r in rows:
        lines.append(
            f"| {r['algorithm']} | {r['coverage']:.1%} | {r['feasible']} | "
            f"{r['violations']} | {r['reassigned_tasks']} |"
        )
    return "\n".join(lines)
