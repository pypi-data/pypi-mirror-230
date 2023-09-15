#pragma once

#include <cassert>
#include <complex>
#include <limits>
#include <ranges>
#include <algorithm>
#include <variant>
#include <functional>
#include <unordered_map>
#include <execution>
#include "superpositeur/CircuitInstruction.hpp"
#include "superpositeur/Common.hpp"
#include "superpositeur/GivensRotation.hpp"
#include "superpositeur/MatrixSparseVectorMultiplication.hpp"
#include "superpositeur/utils/FloatComparison.hpp"
#include "superpositeur/StrongTypes.hpp"
#include "superpositeur/SparseVectorSort.hpp"

namespace superpositeur {

class MixedState {
public:
    explicit MixedState() : currentSortIndices(~BasisVector<128>()), dataVariant(MatrixOfVectors<64>{ SparseVector<64>{{BasisVector<64>{}, 1.}} }), hashes({BasisVector<64>{}.hash()}) {}

    void reset() {
        dataVariant = MatrixOfVectors<64>{ SparseVector<64>{{BasisVector<64>{}, 1.}} };
        hashes = {BasisVector<64>{}.hash()};
    }

    std::uint64_t currentSize() const {
        return std::visit([](auto const& data) { return std::remove_reference<decltype(data)>::type::value_type::value_type::MAX_NUMBER_OF_BITS; }, dataVariant);
    }

public:
    template <std::uint64_t NumberOfQubits>
    void resize() {
        static_assert(NumberOfQubits % 64 == 0); // FIXME
        assert(currentSize() < NumberOfQubits);
        assert(NumberOfQubits == 128); // FIXME
        throw std::runtime_error("Unimplemented");
    }

    bool operator==(MixedState const &) const {
        throw std::runtime_error("Measure of distance between two mixed states not implemented");
    }

    void simplify() {
        // TODO: assert equality before/after simplification.

        std::visit([&](auto &data) {
            if (data.size() <= 1) {
                return;
            }

            simplifyImpl(data);
        }, dataVariant);
    }

private:
    template <std::uint64_t MaxNumberOfQubits>
    void insertOrApply(MatrixOfVectors<MaxNumberOfQubits>& matrixOfVectors, std::unordered_map<std::uint64_t, std::uint64_t>& hashToIndex, std::uint64_t index1) {
        if (matrixOfVectors[index1].empty()) {
            return;
        }

        auto& hash1 = hashes[index1];

        auto [it, inserted] = hashToIndex.insert(std::make_pair(hash1 ^ matrixOfVectors[index1].size(), index1));
        if (inserted) {
            return;
        }

        auto const index2 = it->second;
        auto& hash2 = hashes[index2];
        assert(hash2 == it->first);
        assert(hash1 == hash2);

        auto success = applyGivensRotation<MaxNumberOfQubits>(matrixOfVectors[index1], hash1, matrixOfVectors[index2], hash2);

        if (!success) {
            // Hash collision: leave it be.
            return;
        }

        if ((hash2 ^ matrixOfVectors[index2].size()) == it->first) [[likely]] {
            insertOrApply(matrixOfVectors, hashToIndex, index1);
            return;
        }

        hashToIndex.erase(it);
        insertOrApply(matrixOfVectors, hashToIndex, index1);
        insertOrApply(matrixOfVectors, hashToIndex, index2);
    }

public:

    template <std::uint64_t MaxNumberOfQubits>
    void simplifyImpl(MatrixOfVectors<MaxNumberOfQubits> &data) {
        std::unordered_map<std::uint64_t, std::uint64_t> hashToIndex;

        for (std::uint64_t i = 0; i < hashes.size(); ++i) {
            insertOrApply(data, hashToIndex, {i});
        }

        auto it = data.begin();
        auto hashesIt = hashes.begin();
        while (it != data.end()) {
            if (it->empty()) {
                it = data.erase(it);
                hashesIt = hashes.erase(hashesIt);
            } else {
                ++it;
                ++hashesIt;
            }
        }
    }

    void operator()(CircuitInstruction const &circuitInstruction) {
        auto bitWidth = circuitInstruction.getOperandsMask().bitWidth();
        if (bitWidth > currentSize()) {
            if (bitWidth <= 128) {
                resize<128>();
            } else {
                throw std::runtime_error("Cannot handle that many qubits!");
            }
        }

        std::visit([&](auto&& data) {
            applyCircuitInstruction(circuitInstruction, data);
        }, dataVariant);
        
        simplify();

        assert(isConsistent());
    }

private:
    template <std::uint64_t MaxNumberOfQubits>
    std::uint64_t applyMatrixToSparseVector(SparseVector<MaxNumberOfQubits>& data, Matrix const& matrix, BasisVector<MaxNumberOfQubits> const& operands) {
        assert(std::is_sorted(data.begin(), data.end(), [operands](auto const left, auto const right) {
            return (left.ket & (~operands)) < (right.ket & (~operands));
        }));

        auto startTime = std::chrono::steady_clock::now();
        auto originalDataSize = data.size();

        std::vector<std::complex<double>> inputVector;
        inputVector.resize(matrix.getNumberOfRows());

        std::uint64_t newHash = 0;

        auto it = data.begin();
        auto max = data.end();
        while (it != max) {
            auto firstKey = it->ket;
            auto rest = firstKey & (~operands);

            std::fill(inputVector.begin(), inputVector.end(), 0.);

            auto end = it;
            while (end != max && (end->ket & (~operands)) == rest) {
                inputVector[end->ket.pext(operands)] = end->amplitude;
                ++end;
            }

            for (std::uint64_t i = 0; i < matrix.getNumberOfRows(); ++i) {
                auto v = std::inner_product(inputVector.begin(), inputVector.end(), matrix.line(i).begin(), std::complex<double>(0.));
                auto key = firstKey.pdep(i, operands);

                if (utils::isNotNull(v)) {
                    if (it == end) {
                        if (data.size() < data.capacity()) [[likely]] {
                            data.push_back({key, v});
                        } else {
                            auto itDist = std::distance(data.begin(), it);
                            auto endDist = std::distance(data.begin(), end);
                            auto maxDist = std::distance(data.begin(), max);
                            data.push_back({key, v});
                            it = std::next(data.begin(), itDist);
                            end = std::next(data.begin(), endDist);
                            max = std::next(data.begin(), maxDist);
                        }
                    } else {
                        *it = { key, v };
                        ++it;
                    }

                    newHash += key.hash();
                }
            }

            std::uint64_t maxDist = static_cast<std::uint64_t>(std::distance(data.begin(), max));
            it = data.erase(it, end);
            max = std::next(data.begin(), std::min(data.size(), maxDist));
        }

        auto endTime = std::chrono::steady_clock::now();

        INSTRU << "applyGate," << originalDataSize << "," << std::chrono::duration_cast<std::chrono::nanoseconds>(endTime - startTime).count() << std::endl;

        startTime = std::chrono::steady_clock::now();

        std::inplace_merge(data.begin(), max, data.end(), [negOps = ~operands](auto const left, auto const right) { return (left.ket & negOps) < (right.ket & negOps); });

        endTime = std::chrono::steady_clock::now();

        INSTRU << "finalInplaceMerge," << originalDataSize << "," << data.size() << "," << std::chrono::duration_cast<std::chrono::nanoseconds>(endTime - startTime).count() << std::endl;

        assert(std::is_sorted(data.begin(), data.end(), [negOps = ~operands](auto const left, auto const right) {
            return (left.ket & negOps) < (right.ket & negOps);
        }));

        return newHash;
    }

public:
    template <std::uint64_t MaxNumberOfQubits>
    void applyCircuitInstruction(CircuitInstruction const &circuitInstruction, MatrixOfVectors<MaxNumberOfQubits>& data) {
        if (!circuitInstruction.getControlQubitsMask().empty()) {
            throw std::runtime_error("Unimplemented: control qubits");
        }

        auto ops = circuitInstruction.getOperandsMask().cast<std::remove_reference<decltype(data)>::type::value_type::value_type::MAX_NUMBER_OF_BITS>();

        std::for_each(data.begin(), data.end(), [&](auto& v) {
            sortSparseVector(v, currentSortIndices.cast<MaxNumberOfQubits>(), ~ops);
        });

        auto originalNumberOfVectors = data.size();
        data.reserve(circuitInstruction.getKrausOperators().size() * originalNumberOfVectors);
        for (std::uint64_t i = 1; i < circuitInstruction.getKrausOperators().size(); ++i) {
            data.insert(data.end(), data.begin(), data.begin() + originalNumberOfVectors);
        }

        hashes.resize(data.size()); // Values don't matter here.

        for (std::uint64_t krausOperatorIndex = 0; krausOperatorIndex < circuitInstruction.getKrausOperators().size(); ++krausOperatorIndex) {
            auto const& matrix = circuitInstruction.getKrausOperators()[krausOperatorIndex];
            
            for (std::uint64_t i = originalNumberOfVectors * krausOperatorIndex; i < originalNumberOfVectors * (krausOperatorIndex + 1); ++i) {
                assert(i < data.size());

                hashes[i] = applyMatrixToSparseVector(data[i], matrix, ops);
            }
        }

        currentSortIndices = ~circuitInstruction.getOperandsMask();
    }

private:
    template <std::uint64_t N>
    static BasisVector<N> getMask(std::vector<bool> v) {
        BasisVector<N> mask;
        for (std::uint64_t i = 0; i < v.size(); ++i) {
            mask.set(i, v[i]);
        }
        return mask;
    }

    struct ReducedDensityMatrixIterator {
        using Value = std::tuple<std::uint64_t, std::uint64_t, std::complex<double>>; // i, j, M[i, j]

        template <std::uint64_t N>
        ReducedDensityMatrixIterator(MatrixOfVectors<N>& data, std::vector<bool>& mask) :
            internalsVariant(Internals<N>{.data = data, .reductionQubits = getMask<N>(mask), .vectorIterator = data.begin(), .it1 = data[0].begin(), .it2 = data[0].begin()}) {
            
            assert(std::all_of(data.begin(), data.end(), [sortIndices = ~getMask<N>(mask)](auto const& v) {
                return std::is_sorted(v.begin(), v.end(), [sortIndices](auto const left, auto const right) {
                    return (left.ket & sortIndices) < (right.ket & sortIndices);
                });
            }));
            // Let op! There can be only one density matrix iterator operating at once! And any gate application will invalidate it!
        }

        // Should this own shared ownership of data?

        std::optional<Value> next() {
            return std::visit([&](auto& internals) { return nextImpl(internals); }, internalsVariant);
        }

    private:
        template <typename Internals>
        std::optional<Value> nextImpl(Internals& internals) {
            if (internals.vectorIterator == internals.data.end()) {
                return std::nullopt;
            }

            assert(internals.it1 != internals.vectorIterator->end());
            assert(internals.it2 != internals.vectorIterator->end());
            assert(internals.it1 <= internals.it2);
            assert((internals.it1->ket & (~internals.reductionQubits)) == (internals.it2->ket & (~internals.reductionQubits)));

            Value result = Value(internals.it1->ket.pext(internals.reductionQubits), internals.it2->ket.pext(internals.reductionQubits), internals.it1->amplitude * std::conj(internals.it2->amplitude));

            if (std::next(internals.it2) == internals.vectorIterator->end()) {
                if (std::next(internals.it1) == internals.vectorIterator->end()) {
                    ++internals.vectorIterator;
                    internals.it1 = internals.vectorIterator->begin();
                    internals.it2 = internals.vectorIterator->begin();
                } else {
                    ++internals.it1;
                    internals.it2 = internals.it1;
                }
            } else {
                if ((std::next(internals.it2)->ket & (~internals.reductionQubits)) == (internals.it1->ket & (~internals.reductionQubits))) {
                    ++internals.it2;
                } else {
                    ++internals.it1;
                    internals.it2 = internals.it1;
                }
            }

            return result;
        }

        template <std::uint64_t N>
        struct Internals {
            MatrixOfVectors<N> const& data;
            BasisVector<N> reductionQubits;
            typename MatrixOfVectors<N>::iterator vectorIterator;
            typename SparseVector<N>::iterator it1;
            typename SparseVector<N>::iterator it2;
        };

        std::variant<Internals<64UL>, Internals<128UL>> internalsVariant;
    };

    struct ReducedDensityMatrixDiagonalIterator {
        using Value = std::pair<std::uint64_t, double>; // i, M[i, i]

        template <std::uint64_t N>
        ReducedDensityMatrixDiagonalIterator(MatrixOfVectors<N> const& data, std::vector<bool> const& mask) :
            internalsVariant(Internals<N>{.data = data, .reductionQubits = getMask<N>(mask), .vectorIterator = data.cbegin(), .it = data[0].cbegin()}) {}

        std::optional<Value> next() {
            return std::visit([&](auto& internals) { return nextImpl(internals); }, internalsVariant);
        }

    private:
        template <typename Internals>
        std::optional<Value> nextImpl(Internals& internals) {
            if (internals.vectorIterator == internals.data.end()) {
                return std::nullopt;
            }
            
            assert(internals.it != internals.vectorIterator->end());

            Value result = Value(internals.it->ket.pext(internals.reductionQubits), std::norm(internals.it->amplitude));

            if (std::next(internals.it) != internals.vectorIterator->end()) {
                ++internals.it;
            } else {
                ++internals.vectorIterator;
                internals.it = internals.vectorIterator->begin();
            }

            return result;
        }

        template <std::uint64_t N>
        struct Internals {
            MatrixOfVectors<N> const& data;
            BasisVector<N> reductionQubits;
            typename MatrixOfVectors<N>::const_iterator vectorIterator;
            typename SparseVector<N>::const_iterator it;
        };

        std::variant<Internals<64UL>, Internals<128UL>> internalsVariant;
    };

public:
    ReducedDensityMatrixIterator getReducedDensityMatrixIterator(std::vector<bool> qubits) {
        assert(isConsistent());
        assert(std::distance(std::ranges::find_if(qubits.rbegin(), qubits.rend(), std::identity{}), qubits.rend()) < 128); // FIXME

        return std::visit([&](auto& data) {
            auto desiredSortIndices = ~getMask<std::remove_reference<decltype(data)>::type::value_type::value_type::MAX_NUMBER_OF_BITS>(qubits);
            std::for_each(data.begin(), data.end(), [&](auto& v) {
                sortSparseVector(v, currentSortIndices.cast<std::remove_reference<decltype(data)>::type::value_type::value_type::MAX_NUMBER_OF_BITS>(), desiredSortIndices);
            });

            currentSortIndices = ~getMask<128>(qubits); // FIXME

            return ReducedDensityMatrixIterator(data, qubits);
        }, dataVariant);
    }

    ReducedDensityMatrixDiagonalIterator getReducedDensityMatrixDiagonalIterator(std::vector<bool> const& qubits) const {
        assert(isConsistent());
        assert(std::distance(std::ranges::find_if(qubits.rbegin(), qubits.rend(), std::identity{}), qubits.rend()) < 128); // FIXME

        return std::visit([&](auto const& data) {
            return ReducedDensityMatrixDiagonalIterator(data, qubits);
        }, dataVariant);
    }

    Matrix getReducedDensityMatrix(std::vector<bool> const& mask) {
        auto popcount = std::ranges::count_if(mask, std::identity{});

        assert(popcount > 0 && popcount < 64);

        auto reducedDensityMatrixIterator = getReducedDensityMatrixIterator(mask);

        Matrix m(1UL << popcount, 1UL << popcount);
        while (auto densityMatrixEntry = reducedDensityMatrixIterator.next()) {
            auto i = std::get<0>(*densityMatrixEntry);
            auto j = std::get<1>(*densityMatrixEntry);
            auto v = std::get<2>(*densityMatrixEntry);
            m.add(i, j, v);

            if (i != j) {
                m.add(j, i, std::conj(v));
            }
        }

        // TODO: assert trace == 1.

        return m;
    }

    Matrix getReducedDensityMatrixFromIndices(std::initializer_list<std::uint64_t> const& qubits) {
        std::vector<bool> mask;
        for (auto i: qubits) {
            mask.resize(std::max(mask.size(), i + 1), false);
            mask[i] = true;
        }

        return getReducedDensityMatrix(mask);
    }

    std::vector<double> getReducedDensityMatrixDiagonal(std::vector<bool> const& mask) {
        auto popcount = std::ranges::count_if(mask, [](auto x) { return x; });

        assert(popcount > 0 && popcount < 64);

        auto reducedDensityMatrixDiagonalIterator = getReducedDensityMatrixDiagonalIterator(mask);

        std::vector<double> result(1UL << popcount);
        while (auto densityMatrixDiagonalEntry = reducedDensityMatrixDiagonalIterator.next()) {
            auto i = std::get<0>(*densityMatrixDiagonalEntry);
            auto v = std::get<1>(*densityMatrixDiagonalEntry);
            result[i] += v;
        }

        assert(utils::isNull(std::reduce(result.begin(), result.end()) - 1.));

        return result;
    }

private:
    bool isConsistent() const;

    BasisVector<128> currentSortIndices;
    std::variant<MatrixOfVectors<64>, MatrixOfVectors<128>> dataVariant;
    Hashes hashes;
};

} // namespace  superpositeur