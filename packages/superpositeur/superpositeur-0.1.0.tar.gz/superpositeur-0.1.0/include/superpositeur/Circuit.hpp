#pragma once

#include "superpositeur/MixedState.hpp"

#include <optional>
#include <string>
#include <variant>
#include <vector>

namespace superpositeur {

class Circuit {
public:
    Circuit() = default;

    void addInstruction(CircuitInstruction const &circuitInstruction) {
        data.push_back(circuitInstruction);
    }

    void addLoop(std::vector<CircuitInstruction> block, std::uint64_t iterationCount) {
        data.push_back(Loop{block, iterationCount});
    }

    MixedState execute() const {
        MixedState quantumState;

        for (auto const& x: data) {
            if (auto* loop = std::get_if<Loop>(&x)) {
                for (std::uint64_t iteration = 0; iteration < loop->iterationCount; ++iteration) {
                    for (auto const& instruction: loop->block) {
                        quantumState(instruction);
                    }
                }
            } else if (auto* instruction = std::get_if<CircuitInstruction>(&x)) {
                quantumState(*instruction);
            } else {
                assert(false);
            }
        }

        return quantumState;
    }

private:
    struct Loop {
        std::vector<CircuitInstruction> block;
        std::uint64_t iterationCount = 0;
    };

    std::vector<std::variant<CircuitInstruction, Loop>> data;
};

} // namespace  superpositeur