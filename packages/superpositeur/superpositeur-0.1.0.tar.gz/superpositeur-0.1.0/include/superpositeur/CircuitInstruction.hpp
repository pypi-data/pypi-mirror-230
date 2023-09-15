#pragma once

#include <bit>
#include <cmath>
#include <span>

#include "superpositeur/Common.hpp"
#include "superpositeur/StrongTypes.hpp"
#include "superpositeur/config/CompileTimeConfiguration.hpp"
#include "superpositeur/QuantumOperation.hpp"

namespace superpositeur {

Matrix applyQubitOperandPermutation(Matrix input, std::vector<std::uint64_t> const& operands);

class CircuitInstruction {
public:
    using QubitIndexVector = std::vector<QubitIndex>;

    static std::uint64_t constexpr MaxNumberOfQubits = 128;
    using Mask = utils::BitSet<MaxNumberOfQubits>;

    CircuitInstruction(KrausOperators const& inputKrausOperators, QubitIndexVector operands,
                       QubitIndexVector controlQubits = {}) {
        // FIXME: check intersection of control qubits and operands.

        assert(operands.size() <= MaxNumberOfQubits);

        QuantumOperation::checkValidKrausOperatorSet(inputKrausOperators);

        for (auto op: operands) {
            assert(op.value < MaxNumberOfQubits);
            operandsMask.set(op.value);
        }

        // Find permutation to apply to the Kraus operators.
        std::vector<std::uint64_t> perm(operands.size(), 0);
        std::iota(perm.begin(), perm.end(), 0);
        std::ranges::sort(perm, [&](auto left, auto right) {
            return operands[left] < operands[right];
        });

        for (auto const& krausOperator: inputKrausOperators) {
            krausOperators.push_back(applyQubitOperandPermutation(krausOperator, perm));
        }

        for (auto q: controlQubits) {
            assert(q.value < MaxNumberOfQubits);
            controlQubitsMask.set(q.value);
        }
    }

    std::uint64_t getNumberOfKrausOperators() const {
        return krausOperators.size();
    }

    KrausOperators const& getKrausOperators() const {
        return krausOperators;
    }
    
    Mask getOperandsMask() const {
        return operandsMask;
    }

    Mask getControlQubitsMask() const {
        return controlQubitsMask;
    }

private:
    KrausOperators krausOperators;
    Mask operandsMask;
    Mask controlQubitsMask;
};

} // namespace  superpositeur