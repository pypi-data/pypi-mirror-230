# Superpositeur
Superpositeur is a project to explore efficient algorithms behind density matrix simulation of quantum circuits.

## [Try me online](https://qml-group.github.io/Superpositeur/wasm/demo.html) (work in progress)

## Context
Developed at the TU in Delft, The Netherlands, as a collaboration between the [Quantum Machine Learning group](https://www.tudelft.nl/en/eemcs/the-faculty/departments/quantum-computer-engineering/sections/quantum-circuits-architectures-and-technology/groups/quantum-machine-learning) of Sebastian Feld and [QuTech](https://qutech.nl/).

## Goals
- Has a simple C++ and Python API to provide a list of gates/quantum operations as matrices or sets of Kraus operators to be executed
- Allows access to the full and reduced density matrices of the final quantum state, in an efficient fashion
- Allows access to the diagonal of a reduced density matrix (i.e. computational basis measurement probabilities), in an efficient fashion
- When the resulting quantum state is pure, return it as a (sparse) vector
- On top of the user-friendly Python and C++ API, but also a "low-level" API which allows efficient access to the underlying state, to use in possible front-ends
- Allows usage of user-defined custom gates or set of Kraus operators with arbitrary number of qubits
- Written in C++ and portable on Linux, MacOS, Windows, for 64 bits architectures x86 and ARM
- NO usage of randomness: the output of the simulator is perfectly deterministic, whatever the input circuit
- Fast and performant on a large class of quantum circuits
- Efficient use of memory

## Future improvements
- Multithreading
- Documentation
- Research paper
- Fidelity of quantum states (and/or other metric) to compare two states
- When input circuit is obviously a tensor product of smaller circuits, simulate those separately
- Do some obvious optimization of the input circuit (e.g. collapse consecutive 1-qubit gates/Kraus operators operating on the same qubit)
- Explore how gate/operation scheduling impacts simulation complexity
- Benchmark, profiling and performance tuning
- Usage as backend of [QX-simulator](https://github.com/QuTech-Delft/qx-simulator) to simulate cQasm circuits once stable, robust and tested enough

## Current author
- Pablo Le Hénaff (p.lehenaff@tudelft.nl)
