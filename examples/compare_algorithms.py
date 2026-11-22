"""Compare all algorithms on disrupted scenarios. Run: python examples/compare_algorithms.py"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from agentreassign import (ALGORITHMS, Agent, Disruption, Task, compare,
                           generate_scenario, markdown_table)


def main() -> None:
    agents, tasks = generate_scenario(n_agents=6, n_tasks=10, seed=5)
    disruptions = [
        Disruption(kind="agent_offline", agent_id="agent-1"),
        Disruption(kind="urgent_task",
                   task=Task(id="urgent-1", skill="medic", priority=3, deadline=3)),
        Disruption(kind="agent_offline", agent_id="agent-3"),
    ]
    rows = compare(ALGORITHMS, agents, tasks, disruptions)
    print("Scenario: 6 agents, 10 tasks, 2 dropouts + 1 urgent task\n")
    print(markdown_table(rows))

    # Scenario B: scarce skills. Skill-aware assignment preserves the only
    # medic-capable agent for medic tasks instead of filling it with security work.
    agents_b = {
        "a1": Agent.make("a1", ["security"], capacity=1),
        "a2": Agent.make("a2", ["security", "medic"], capacity=1),
        "a3": Agent.make("a3", ["medic"], capacity=2),
    }
    tasks_b = [
        Task("t1", "security", priority=3),
        Task("t2", "security", priority=1),
        Task("t3", "medic", priority=2),
    ]
    rows_b = compare(ALGORITHMS, agents_b, tasks_b, [])
    print("\nScenario B: scarce skills (2 security + 1 medic tasks, tight capacities)\n")
    print(markdown_table(rows_b))


if __name__ == "__main__":
    main()
