# Welcome to the Semantic World Package
Introducing Semantic World: A unified interface for scene data and asserted meaning.

The Semantic World Python package streamlines the integration and management of scene graphs with explicit semantic assertions.
Agents and autonomous systems require more than just coordinates, they need contextual understanding. 
Semantic World bridges geometry, kinematics, and meaning, allowing systems for planning, 
learning, and reasoning to process the environment through actionable, high-level concepts.

This enables the construction of environments that can be readily understood,
queried, transformed, and shared across projects.
Whether for research prototypes or robust data pipelines,
Semantic World translates raw environment data into structured knowledge.

## Assimilated Technologies

<image alt="Assimilation Icon" src="doc/_static/images/assimilation_dark_mode.png#gh-dark-mode-only" style="width: 300px; height: auto; object-fit: contain;"></image>
<image alt="Assimilation Icon" src="doc/_static/images/assimilation.png#gh-light-mode-only" style="width: 300px; height: auto; object-fit: contain;"></image>


🌍 **Model full kinematic worlds, not just meshes**. Define bodies, regions, connections, and degrees of freedom as primary, first-class entities within a clean, composable Python API.

🤔 **Enhance meaning with Views.** Transform raw geometry into actionable concepts like drawers, handles, containers, and task-relevant regions. Express relationships and intent beyond simple shapes.

💡 **Intelligent Querying.** Use a high-level entity query language to precisely locate relevant elements—e.g., "the handle attached to the drawer that is currently accessible"—to enable targeted interaction.


🛢️️ **Reproducible Persistence and Replay.** 
Serialize annotated worlds into a SQL format, allowing for faithful reconstruction as consistent, interactive objects. 
This facilitates reproducible experiments and robust machine learning data pipelines.

🛠️ **Effortless Composition.** 
Leverage factories and dataclasses for simple authoring of complex scenes and extending semantics. 
Share domain knowledge efficiently without reliance on fragile glue code.

📈 **Scale and Consistency.** 
The integrated kinematic tree, DoF registry, 
and robust world validation ensure model consistency and integrity from initial prototype to large-scale production deployment.

🔮 **Flexible Visualization.** 
View worlds in lightweight RViz2, explore within notebooks, or integrate with richer simulation environments. 
Quickly understand both the structural and semantic layers of your models.

🔌 **Pluggable Integration.** 
Use a multitude of adapters for seamless import, no matter if its URDF, USD, MJCF, etc. 

🦾 **Reliable Kinematics.** 
Compute forward transforms and inverse (backward) kinematics cleanly across the tree, 
providing a straightforward and robust foundation for pose queries, control, and reasoning.

👯‍ **Real-Time World Synchronization.** 
Maintain a consistent state across multiple processes and robotic agents using lightweight, 
real-time world synchronization. 
Structures can be created, merged, and updated at once, 
ensuring they are accurately reflected across all connected instances.

🚀 Get started with the [user-guide](https://cram2.github.io/semantic_world/user_guide.html#user-guide)!

📖 Read the full [documentation](https://cram2.github.io/semantic_world/intro.html)!

🤝 Contribute with the [developer-guide](https://cram2.github.io/semantic_world/developer_guide.html#developer-guide)!


# User Installation


You can install the package directly from PyPI:

```bash
pip install -U semantic_world
```

# Contributing

If you are interested in contributing, you can check out the source code from GitHub:

```bash
git clone https://github.com/cram2/semantic_world.git
```

### Development Dependencies

```bash
sudo apt install -y graphviz graphviz-dev
pip install -r requirements.txt
```


# Tests
The tests can be run with `pytest` directly in PyCharm or from the terminal after installing Semantic World as a python package.

```bash
pip install -e .
pytest test/
```
