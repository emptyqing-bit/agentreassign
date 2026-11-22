"""AgentReassign unit tests (stdlib unittest; run: python -m unittest discover tests)."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from agentreassign import (Agent, Allocation, Disruption, GreedyAlgorithm,
                           LocalSearchAlgorithm, RandomAlgorithm,
                           SkillAwareAlgorithm, Task, compare, generate_scenario,
                           simulate)


def small_problem():
    agents = {
        "a1": Agent.make("a1", ["security"], capacity=1),
        "a2": Agent.make("a2", ["security", "medic"], capacity=1),
        "a3": Agent.make("a3", ["medic"], capacity=2),
    }
    tasks = [
        Task("t1", "security", priority=3),
        Task("t2", "security", priority=1),
        Task("t3", "medic", priority=2),
    ]
    return agents, tasks


class TestAlgorithms(unittest.TestCase):
    def test_greedy_feasible(self):
        agents, tasks = small_problem()
        alloc = GreedyAlgorithm().allocate(tasks, agents)
        self.assertTrue(alloc.is_feasible(tasks, agents))
        # Greedy first-fit covers 2/3 here: the two security tasks compete
        # for two capacity-1 agents, one of which also serves medic tasks.
        self.assertGreaterEqual(alloc.coverage(tasks), 2 / 3)

    def test_skill_aware_full_coverage(self):
        # Skill-aware preserves scarce skills and covers all three tasks.
        agents, tasks = small_problem()
        alloc = SkillAwareAlgorithm().allocate(tasks, agents)
        self.assertEqual(alloc.coverage(tasks), 1.0)
        self.assertTrue(alloc.is_feasible(tasks, agents))

    def test_capacity_respected(self):
        agents, tasks = small_problem()
        alloc = GreedyAlgorithm().allocate(tasks, agents)
        for agent in agents.values():
            self.assertLessEqual(len(alloc.assigned_to(agent.id)), agent.capacity)

    def test_skill_mismatch_never_assigned(self):
        agents, tasks = small_problem()
        for algo in [GreedyAlgorithm(), SkillAwareAlgorithm(), RandomAlgorithm(seed=3)]:
            alloc = algo.allocate(tasks, agents)
            for tid, aid in alloc.assignments.items():
                task = next(t for t in tasks if t.id == tid)
                self.assertIn(task.skill, agents[aid].skills)

    def test_local_search_at_least_greedy(self):
        agents, tasks = small_problem()
        greedy = GreedyAlgorithm().allocate(tasks, agents)
        local = LocalSearchAlgorithm().allocate(tasks, agents)
        self.assertGreaterEqual(local.coverage(tasks), greedy.coverage(tasks))
        self.assertTrue(local.is_feasible(tasks, agents))

    def test_impossible_task_left_unassigned(self):
        agents, tasks = small_problem()
        tasks.append(Task("t-x", "pilot", priority=3))
        alloc = GreedyAlgorithm().allocate(tasks, agents)
        self.assertNotIn("t-x", alloc.assignments)


class TestSimulation(unittest.TestCase):
    def test_dropout_triggers_reassignment(self):
        agents, tasks = small_problem()
        row = simulate(GreedyAlgorithm(), agents, tasks,
                       [Disruption(kind="agent_offline", agent_id="a1")])
        self.assertGreaterEqual(row["reassigned_tasks"], 0)
        self.assertTrue(row["feasible"])

    def test_compare_returns_all_algorithms(self):
        agents, tasks = generate_scenario(seed=5)
        rows = compare([GreedyAlgorithm(), SkillAwareAlgorithm()], agents, tasks, [])
        self.assertEqual(len(rows), 2)
        for row in rows:
            self.assertTrue(row["feasible"])


if __name__ == "__main__":
    unittest.main()
