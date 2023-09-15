#include "superpositeur/Matrix.hpp"
#include "superpositeur/Common.hpp"
#include "superpositeur/CircuitInstruction.hpp"

namespace superpositeur {

template <std::uint64_t MaxNumberOfQubits>
using InputSpan = std::span<KeyValue<MaxNumberOfQubits> const>;

template <std::uint64_t MaxNumberOfQubits>
class Iterators {
public:
    using Input = InputSpan<MaxNumberOfQubits>;
    using Operands = CircuitInstruction::Mask;

    Iterators(Matrix const& m, Input const& s, Operands ops) : matrix(m), begin(s.begin()), end(s.end()), operands(ops.cast<MaxNumberOfQubits>()) {
        assert(matrix.isSquare());
        assert(std::has_single_bit(matrix.getNumberOfRows()));
        assert(matrix.getNumberOfRows() >= 2);

        iterators.reserve(matrix.getNumberOfRows() * matrix.getNumberOfCols());

        for (std::uint64_t i = 0; i < matrix.getNumberOfRows(); ++i) {
            for (std::uint64_t j = 0; j < matrix.getNumberOfCols(); ++j) {
                if (utils::isNotNull(matrix.get(i, j))) {
                    auto it = begin;
                    while (it != end && it->ket.pext(operands) != j) {
                        ++it;
                    }

                    if (it != end) {
                        iterators.emplace_back(Iterator{
                            .input = BasisVector<MaxNumberOfQubits>().pdep(j, operands),
                            .output = BasisVector<MaxNumberOfQubits>().pdep(i, operands),
                            .coeff = matrix.get(i, j),
                            .resultKet = it->ket.pdep(i, operands),
                            .iterator = it}
                        );
                    }
                }
            }
        }
    }

    KeyValue<MaxNumberOfQubits> next() {
        if (iterators.empty()) [[unlikely]] {
            return { BasisVector<MaxNumberOfQubits>(), { NAN, NAN } };
        }

        auto topIt = std::ranges::min_element(iterators, {}, &Iterator::resultKet);

        KeyValue<MaxNumberOfQubits> result = { topIt->resultKet, topIt->iterator->amplitude * topIt->coeff };

        topIt->iterator = std::find_if(++topIt->iterator, end, [&](auto kv) { return (kv.ket & operands) == topIt->input; });

        if (topIt->iterator != end) [[likely]] {
            topIt->resultKet = (topIt->iterator->ket & (~operands)) | topIt->output;
        } else {
            iterators.erase(topIt);
        }

        return result;
    }

private:
    struct Iterator {
        BasisVector<MaxNumberOfQubits> input;
        BasisVector<MaxNumberOfQubits> output;
        std::complex<double> coeff;
        BasisVector<MaxNumberOfQubits> resultKet;
        typename Input::iterator iterator;
    };
    
    Matrix const& matrix;
    typename Input::iterator const begin;
    typename Input::iterator const end;
    BasisVector<MaxNumberOfQubits> operands;
    std::vector<Iterator> iterators;
};

template <std::uint64_t MaxNumberOfQubits>
inline std::uint64_t multiplyMatrix(Matrix const& matrix, InputSpan<MaxNumberOfQubits> input, CircuitInstruction::Mask const& operands, std::back_insert_iterator<SparseVector<MaxNumberOfQubits>> inserter) {
    assert(matrix.isSquare());
    assert(std::popcount(matrix.getNumberOfRows()) == 1);
    assert(matrix.getNumberOfRows() >= 2);
    assert(operands.popcount() == static_cast<std::uint64_t>(std::countr_zero(matrix.getNumberOfRows())));

    auto iterators = Iterators<MaxNumberOfQubits>(matrix, input, operands);

    std::uint64_t hashOfTheKeys = 0;
    
    KeyValue<MaxNumberOfQubits> accumulator = { BasisVector<MaxNumberOfQubits>(), 0.};

    auto kv = iterators.next();
    while (!std::isnan(kv.amplitude.real())) {
        if (kv.ket != accumulator.ket) {
            assert(kv.ket > accumulator.ket);

            if (utils::isNotNull(accumulator.amplitude)) [[likely]] {
                inserter = accumulator;
                hashOfTheKeys += accumulator.ket.hash();
            }
            accumulator = kv;
        } else {
            accumulator.amplitude += kv.amplitude;
        }

        kv = iterators.next();
    }

    if (utils::isNotNull(accumulator.amplitude)) {
        inserter = accumulator;
        hashOfTheKeys += accumulator.ket.hash();
    }

    return hashOfTheKeys;
}

}