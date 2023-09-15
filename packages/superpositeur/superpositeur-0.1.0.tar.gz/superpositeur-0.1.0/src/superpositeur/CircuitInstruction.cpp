#include "superpositeur/CircuitInstruction.hpp"

namespace superpositeur {
    
Matrix applyQubitOperandPermutation(Matrix input, std::vector<std::uint64_t> const& operands) {
    assert(std::ranges::all_of(operands, [&](auto const& index) {
        return index < operands.size();
    }));

    assert(std::set(operands.begin(), operands.end()).size() == operands.size());

    assert(input.isSquare());
    assert(std::has_single_bit(input.getNumberOfRows()));
    assert(static_cast<std::size_t>(std::countr_zero(input.getNumberOfRows())) == operands.size());

    std::vector<std::uint64_t> masks;
    std::uint64_t current = 0;
    masks.push_back(~current);
    for (auto it = operands.rbegin(); it != operands.rend(); ++it) {
        current |= 1UL << *it;
        masks.push_back(~current);
    }

    Matrix swappedRows(input.getNumberOfRows(), input.getNumberOfCols());
    std::uint64_t inputRowOrColumn = 0;
    for (std::uint64_t i = 0; i < (1UL << operands.size()); ++i) { // FIXME: refactor this.
        std::copy(input.data.begin() + inputRowOrColumn * input.getNumberOfRows(),
                  input.data.begin() + (inputRowOrColumn + 1) * input.getNumberOfRows(),
                  swappedRows.data.begin() + i * swappedRows.getNumberOfRows());
        
        std::uint64_t rightOnes = std::countr_one(i);

        assert(rightOnes < masks.size());
        assert(static_cast<std::uint64_t>(std::popcount(inputRowOrColumn & (~masks[rightOnes]))) == rightOnes);
        assert((i == ((1UL << operands.size()) - 1)) || (inputRowOrColumn & (1UL << operands[operands.size() - rightOnes - 1])) == 0);

        if (i < (1UL << operands.size()) - 1) { // FIXME: ugly
            inputRowOrColumn &= masks[rightOnes];
            assert(rightOnes < operands.size());
            inputRowOrColumn |= 1UL << operands[operands.size() - rightOnes - 1];
        }
    }

    inputRowOrColumn = 0;
    for (std::uint64_t i = 0; i < (1UL << operands.size()); ++i) {
        for (std::uint64_t rowIndex = 0; rowIndex < swappedRows.getNumberOfRows(); ++rowIndex) {
            input.set(rowIndex, i, swappedRows.get(rowIndex, inputRowOrColumn));
        }

        std::uint64_t rightOnes = std::countr_one(i);

        assert(rightOnes < masks.size());
        assert(static_cast<std::uint64_t>(std::popcount(inputRowOrColumn & (~masks[rightOnes]))) == rightOnes);
        assert((i == ((1UL << operands.size()) - 1)) || (inputRowOrColumn & (1UL << operands[operands.size() - rightOnes - 1])) == 0);

        if (i < (1UL << operands.size()) - 1) {
            inputRowOrColumn &= masks[rightOnes];
            inputRowOrColumn |= 1UL << operands[operands.size() - rightOnes - 1];
        }
    }

    return input;
}

}