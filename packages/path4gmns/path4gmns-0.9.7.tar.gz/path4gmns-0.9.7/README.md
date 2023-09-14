# Path4GMNS
[![platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-red)](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-red)
[![Downloads](https://static.pepy.tech/badge/path4gmns)](https://pepy.tech/project/path4gmns) [![GitHub release](https://img.shields.io/badge/release-v0.9.7-brightgreen)](https://img.shields.io/badge/release-v0.8.2-brightgreen) ![Read the Docs](https://img.shields.io/readthedocs/path4gmns)

Path4GMNS is an open-source, cross-platform, lightweight, and fast Python path engine for networks encoded in [GMNS](https://github.com/zephyr-data-specs/GMNS). Besides finding static shortest paths for simple analyses, its main functionality is to provide an efficient and flexible framework for column-based (path-based) modeling and applications in transportation (e.g., activity-based demand modeling). Path4GMNS supports, in short,

1. finding (static) shortest path between two nodes,
2. performing path-based User-Equilibrium (UE) traffic assignment,
3. conducting dynamic traffic assignment (DTA) after UE.
4. evaluating multimodal accessibility and equity,
5. synthesizing zones and Origin-Destination (OD) demand for a given network.

Path4GMNS also serves as an API to the C++-based [DTALite](https://github.com/jdlph/DTALite) to conduct various multimodal traffic assignments including,
   * Link-based UE,
   * Path-based UE,
   * UE + DTA,
   * OD Matrix Estimation (ODME).

![Architecture](/docs/source/imgs/architecture.png)

## Installation
Path4GMNS has been published on [PyPI](https://pypi.org/project/path4gmns/0.9.7/), and can be installed using
```
$ pip install path4gmns
```

v0.9.7 serves as a hotfix over v0.9.5 and v0.9.6 on emitting DTALite log and synthesizing zone and demand. Please **update to or install the latest version** and **discard all old versions**.

> [!WARNING]
> Any versions prior to v0.9.4 will generate INCORRECT simulation results.
> Calling DTALite and [synthesizing zones and OD demand are not functioning for v0.9.5 and v0.9.6](https://github.com/jdlph/Path4GMNS/issues/41).

### Dependency
The Python modules are written in **Python 3.x**, which is the minimum requirement to explore the most of Path4GMNS. Some of its functions require further run-time support, which we will go through along with the corresponding **[Use Cases](https://path4gmns.readthedocs.io/en/latest/)**.

## Quick Start

 We highly recommend that you go through this **[Tutorial](https://github.com/jdlph/Path4GMNS/tree/dev/tests/tutorial.ipynb)** written in Jupyter notebook with step-by-step demonstration using the latest version, no matter you are one of the existing users or new to Path4GMNS. Its documentation is available on **[readthedocs](https://path4gmns.readthedocs.io/en/latest/)**.

## Please Contribute

Any contributions are welcomed including advise new applications of Path4GMNS, enhance documentation and [docstrings](https://docs.python-guide.org/writing/documentation/#writing-docstrings) in the source code, refactor and/or optimize the source code, report and/or resolve potential issues/bugs, suggest and/or add new functionalities, etc.

Path4GMNS has a very simple workflow setup, i.e., **master for release (on both GitHub and PyPI)** and **dev for development**. If you would like to work directly on the source code (and probably the documentation), please make sure that **the destination branch of your pull request is dev**, i.e., all potential changes/updates shall go to the dev branch before merging into master for release.

You are encouraged to join our [Discord Channel](https://discord.gg/JGFMta7kxZ) for the latest update and more discussions.

## Implementation Notes

The column generation scheme in Path4GMNS is an equivalent **single-processing implementation** as its [DTALite](https://github.com/jdlph/DTALite/tree/main/src_cpp) multiprocessing counterpart. **Note that** the results (i.e., column pool and trajectory for each agent) from Path4GMNS and DTALite are comparable but likely not identical as the shortest paths are usually not unique and subjected to implementations. This difference shall be subtle and the link performances shall be consistent if the iterations of column generation and column update are both large enough. You can always compare the results (i.e., link_performance.csv) from Path4GMNS and DTALite given the same network and demand.

The whole package is implemented towards **high performance**. The core shortest-path engine is implemented in C++ (deque implementation of the modified label correcting algorithm) along with the equivalent Python implementations for demonstration. To achieve the maximum efficiency, we use a fixed-length array as the deque (rather than the STL deque) and combine the scan eligible list (represented as deque) with the node presence status. Along with the minimum and fast argument interfacing between the underlying C++ path engine and the upper Python modules, its running time is comparable to the pure C++-based DTALite for small- and medium-size networks (e.g., the Chicago Sketch Network) without multiprocessing. If you have an extremely large network and/or have requirement on CPU time, we recommend using DTALite to fully utilize its parallel computing feature.

An easy and smooth installation process by **low dependency** is one of our major design goals. The core Python modules in Path4GMNS only require a handful of components from the Python standard library (e.g., csv, ctypes, and so on) with no any third-party libraries/packages. On the C++ side, the precompiled path engines as shared libraries are embedded to make this package portable across three major desktop environments (i.e., Windows, macOS, and Linux) and its source is implemented in C++11 with no dependency. Users can easily build the path engine from the source code towards their target system if it is not listed above as one of the three.

### More on the Column-Generation Module
**The column generation module first identifies new columns (i.e., paths) between each OD pair at each iteration and adds them into the column pool before optimizing (i.e., shifting flows among columns to achieve the equilibrium state)**. The original implementations in both DTALite and Path4GMNS (prior to v0.8.0) rely on node sum as the unique key (or hash index) to differentiate columns, which is simply the summation of node sequence numbers along a column. However, it cannot guarantee that a non-existing column will always be added to the column pool as different columns may share the same node sum (and we presume a one-to-one mapping from node sum to column rather than an array of slots for different columns with the same node sum). An example would be 0->1->4->5 and 0->2->3->5, where 0 to 5 are node sequence numbers. One of the columns will be precluded from the column pool.

In order to resolve this issue, we have deprecated node sum and introduced a side-by-side column comparison in Path4GMNS only. As columns between an OD pair are largely different in number of nodes, this comparison can be very efficiently. Slight improvements are actually observed in both running time and convergence gap over the original implementation.

DTALite uses arrays rather than STL containers to store columns. These arrays are fixed in size (1,000), which prevents a fast filtering using the number of nodes as described above. For two (long) columns only different in the last few nodes, this side-by-side comparison has to be continued until the very end and ruins the performance. Thus, we decide **NOT TO ADOPT** this updated implementation to DTALite and leave it to **[TransOMS](https://github.com/jdlph/TransOMS)**.

### Major Updates
1. Read and output node and link geometries (v0.6.0)
2. Set up individual agents from aggregated OD demand only when it is needed (v0.6.0)
3. Provide a setting file in yaml to let users control key parameters (v0.6.0)
4. Support for multi-demand-period and multi-agent-type (v0.6.0)
5. Load columns/paths from existing runs and continue path-base UE (v0.7.0a1)
6. Download the predefined GMNS test data sets to users' local machines when needed (v0.7.0a1)
7. Add allowed use in terms of agent type (i.e., transportation mode) for links (v0.7.0a1)
8. Calculate and show up multimodal accessibility (v0.7.0a1)
9. Apply lightweight and faster implementation on accessibility evaluation using virtual centroids and connectors (v0.7.0)
10. Get accessible nodes and links given mode and time budget (v0.7.0)
11. Retrieve shortest paths under multimodal allowed uses (v0.7.2)
12. Time-dependent accessibility evaluation (v0.7.3)
13. Fix crucial bug in accessibility evaluation (v0.7.5)
14. Deprecate node_sum as hash index in column generation (v0.8.0)
15. Optimize class ColumnVec, setup_agents() in class Network, and column generation module (i.e., colgen.py) (v0.8.1)
16. Deep code optimization in column generation module with significant performance improvement (v0.8.2)
17. Let users choose which speed to use in accessibility evaluation (either the free speed of an agent specified in settings.yml or the link free flow speed defined in link.csv) (v0.8.3)
18. Transportation equity evaluation (v0.8.3)
19. Introduce special events with affected links and capacity reductions (v0.8.4)
20. Synthesize zones and demands (v0.8.5)
21. Add support for Apple Silicon (v0.8.5)
22. More robust parsing functions (v0.8.6)
23. Fix crucial bug in column generation module which will lead to wrong results if a zone has multiple nodes (v0.8.6)
24. Fix crucial bug in setting up the capacity of each VDFPeriod instance if the input is missing from link.csv (v0.8.6)
25. Add backwards compatibility on deprecated default agent type of p or passenger (v0.8.7a1)
26. Fix potential issue in setup_spnetwork() which requires zone id's are in ascending order (v0.8.7a1)
27. Fix potential issue that bin_index might not start from zero along with potential zero division issue when all zones have the same number of nodes in _synthesize_bin_index() (v0.8.7a1)
28. Enhance the tutorial with elaboration on the legacy way of loading demand and zone information and some caveats. (v0.8.7a1)
29. Calculate and print out relative gap of UE as convergency measure (v0.8.7)
30. Support the most common length and speed units. See [tutorial](https://github.com/jdlph/Path4GMNS/tree/dev/tests/tutorial.ipynb) for details (v0.8.7)
31. Introduce the simulation module along with a simple traffic simulator using the point queue model and shortest paths (v0.9.0)
32. Fully optimize the C++ routing engine (v0.9.1)
33. Use the UE result as routing decisions for simulation (v0.9.1)
34. Optimize the column generation module with faster and better UE convergency (v0.9.2)
35. Fix the bug on updating the total system travel time (v0.9.2)
36. Resolve the potential issue on traversing the last through node in path engine (v0.9.2)
37. Fix the bug on loading columns where link path and node paths are not in the proper order (v0.9.2)
38. Fix the bug on handling link capacity reduction in traffic assignment (v0.9.3)
39. Remove dependency on demand.csv for loading columns (v0.9.3)
40. Deprecate find_path_for_agents() (v0.9.3)
41. Remove beg_iteration and end_iteration from setting up a special event (v0.9.4)
42. Enhance DemandPeriod setup on time_period (v0.9.4)
43. Fix multiple bugs related to simulation including calculation of agent arrival time and agent waiting time, link traverse time, and link outflow cap (v0.9.4)
44. Remove memory_blocks and its implementations (which were intended for multiprocessing) (v0.9.4)
45. Bring back the postprocessing after UE in case users do not do column updating (i.e., column_update_num = 0) (v0.9.4)
46. Drop the requirement that node id must be integer (v0.9.5)
47. Drop the requirement that zone id must be integer (v0.9.5)
48. Eliminate ultra-low-volume columns from assignment (v0.9.6)
49. Calculate and print out the final UE convergency after the postprocessing (v0.9.6)
50. Embed and support the latest [DTALite](https://github.com/asu-trans-ai-lab/DTALite) in addition to the existing [classic version](https://github.com/jdlph/DTALite) (v0.9.6)
51. Complete update 47 introduced in v0.9.5 (v0.9.7)

Detailed update information can be found in [Releases](https://github.com/jdlph/Path4GMNS/releases).

## How to Cite

Li, P. and Zhou, X. (2023, September 13). *Path4GMNS*. Retrieved from https://github.com/jdlph/Path4GMNS

## References
Lu, C. C., Mahmassani, H. S., Zhou, X. (2009). [Equivalent gap function-based reformulation and solution algorithm for the dynamic user equilibrium problem](https://www.sciencedirect.com/science/article/abs/pii/S0191261508000829). Transportation Research Part B: Methodological, 43, 345-364.

Jayakrishnan, R., Tsai, W. K., Prashker, J. N., Rajadyaksha, S. (1994). [A Faster Path-Based Algorithm for Traffic Assignment](https://escholarship.org/uc/item/2hf4541x) (Working Paper UCTC No. 191). The University of California Transportation Center.

Bertsekas, D., Gafni, E. (1983). [Projected Newton methods and optimization of multicommodity flows](https://web.mit.edu/dimitrib/www/Gafni_Newton.pdf). IEEE Transactions on Automatic Control, 28(12), 1090–1096.