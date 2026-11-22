# AgentReassign

**Algorithms for dynamic task re-allocation under disruptions.**

A compact, dependency-free library for multi-agent task allocation when things go
wrong: agents drop out, urgent tasks arrive, priorities shift. Built for research on
adaptive emergency-response workflows and multi-agent resource scheduling.

## Algorithms

| Algorithm | Strategy |
| --- | --- |
| `GreedyAlgorithm` | Priority-ordered first fit, least-loaded feasible agent |
| `SkillAwareAlgorithm` | Preserves scarce skills: assigns narrow-skill agents first, most-constrained tasks first |
| `LocalSearchAlgorithm` | Greedy seed + swap moves that increase coverage while staying feasible |
| `RandomAlgorithm` | Seeded random feasible assignment (lower bound) |

All algorithms respect **skill requirements** and **per-agent capacities**; infeasible
tasks are left unassigned rather than forced.

## Simulation

`simulate()` applies a disruption sequence (`agent_offline`, `urgent_task`) and
re-allocates pending tasks, discounting each agent's capacity by its current load.
Metrics: coverage, feasibility, constraint violations, reassigned-task count.

## Quick start

Python 3.10+, no third-party dependencies.

```bash
python examples/compare_algorithms.py   # two scenarios, algorithm comparison table
python -m unittest discover tests      # 8 unit tests
```

Sample output (scenario B: scarce skills):

| Algorithm | Coverage | Feasible | Violations |
| --- | --- | --- | --- |
| greedy | 66.7% | True | 0 |
| skill-aware | 100.0% | True | 0 |
| local-search | 66.7% | True | 0 |
| random | 100.0% | True | 0 |

## Use in your research

```python
from agentreassign import Agent, Task, GreedyAlgorithm

agents = {"a1": Agent.make("a1", ["security"], capacity=2)}
tasks = [Task("t1", "security", priority=3, deadline=5)]
alloc = GreedyAlgorithm().allocate(tasks, agents)
print(alloc.assignments)  # {'t1': 'a1'}
```

## Repository layout

| Path | Contents |
| --- | --- |
| `agentreassign/model.py` | Agents, tasks, allocation with feasibility checks |
| `agentreassign/algorithms.py` | Four allocation algorithms |
| `agentreassign/simulation.py` | Disruption events, simulation loop, metrics, Markdown tables |
| `examples/compare_algorithms.py` | Disruption scenario + scarce-skill scenario |
| `tests/` | Feasibility, capacity, skill and simulation tests |

## License

MIT — see [LICENSE](LICENSE).
