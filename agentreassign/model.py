"""Problem model: agents, tasks and allocations under disruptions."""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Agent:
    id: str
    skills: frozenset[str]
    capacity: int = 2

    @classmethod
    def make(cls, id: str, skills: list[str] | set[str], capacity: int = 2) -> "Agent":
        return cls(id=id, skills=frozenset(skills), capacity=capacity)


@dataclass(frozen=True)
class Task:
    id: str
    skill: str
    priority: int = 1  # higher = more urgent
    deadline: int = 10  # simulation steps


@dataclass
class Allocation:
    """task_id -> agent_id assignment with feasibility checks."""
    assignments: dict[str, str] = field(default_factory=dict)

    def assign(self, task_id: str, agent_id: str) -> None:
        self.assignments[task_id] = agent_id

    def unassign(self, task_id: str) -> None:
        self.assignments.pop(task_id, None)

    def assigned_to(self, agent_id: str) -> list[str]:
        return [t for t, a in self.assignments.items() if a == agent_id]

    def coverage(self, tasks: list[Task]) -> float:
        if not tasks:
            return 0.0
        return sum(1 for t in tasks if t.id in self.assignments) / len(tasks)

    def violations(self, tasks: list[Task], agents: dict[str, Agent]) -> list[str]:
        """Skill mismatches and capacity overflows."""
        by_id = {t.id: t for t in tasks}
        problems: list[str] = []
        for task_id, agent_id in self.assignments.items():
            task = by_id.get(task_id)
            agent = agents.get(agent_id)
            if task is None or agent is None:
                problems.append(f"{task_id}: unknown task or agent")
                continue
            if task.skill not in agent.skills:
                problems.append(f"{task_id}: {agent_id} lacks skill {task.skill}")
            if len(self.assigned_to(agent_id)) > agent.capacity:
                problems.append(f"{agent_id}: over capacity {agent.capacity}")
        return problems

    def is_feasible(self, tasks: list[Task], agents: dict[str, Agent]) -> bool:
        return not self.violations(tasks, agents)
