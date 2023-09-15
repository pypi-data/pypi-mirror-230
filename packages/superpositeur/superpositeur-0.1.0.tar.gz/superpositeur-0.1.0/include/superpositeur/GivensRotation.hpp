#pragma once

#include "superpositeur/Common.hpp"
#include "superpositeur/config/CompileTimeConfiguration.hpp"
#include "superpositeur/utils/FloatComparison.hpp"
#include <span>
#include <algorithm>
#include <cmath>

namespace superpositeur {

template <std::uint64_t MaxNumberOfQubits>
void undo(SparseVector<MaxNumberOfQubits>& firstLine,
          typename SparseVector<MaxNumberOfQubits>::iterator firstIt, 
          std::uint64_t& firstHash,
          SparseVector<MaxNumberOfQubits>& secondLine,
          typename SparseVector<MaxNumberOfQubits>::iterator secondIt,
          std::uint64_t& secondHash,
          std::complex<double> c,
          std::complex<double> s) {
    (void) firstLine;
    (void) firstIt;
    (void) firstHash;
    (void) secondLine;
    (void) secondIt;
    (void) secondHash;
    (void) c;
    (void) s;

    throw std::runtime_error("Congrats, you found a hash collision, and this is not implemented yet");
}

template <std::uint64_t MaxNumberOfQubits = 64>
bool applyGivensRotation(SparseVector<MaxNumberOfQubits>& firstLine, std::uint64_t& firstHash, SparseVector<MaxNumberOfQubits>& secondLine, std::uint64_t& secondHash) {
    assert(!firstLine.empty());

    assert(firstLine.size() == secondLine.size());
    assert(std::equal(firstLine.begin(), firstLine.end(), secondLine.begin(), [](auto left, auto right) { return left.ket == right.ket; }));

    assert(std::all_of(firstLine.begin(), firstLine.end(), [](auto x) { return utils::isNotNull(x.amplitude); }));
    assert(std::all_of(secondLine.begin(), secondLine.end(), [](auto x) { return utils::isNotNull(x.amplitude); }));

    assert(std::accumulate(firstLine.begin(), firstLine.end(), 0ULL, [](auto acc, auto x) { return acc + x.ket.hash(); }) == firstHash);
    assert(std::accumulate(secondLine.begin(), secondLine.end(), 0ULL, [](auto acc, auto x) { return acc + x.ket.hash(); }) == secondHash);
    assert(firstHash == secondHash);


    auto firstIt = firstLine.begin();
    auto secondIt = secondLine.begin();

    auto firstWriteIt = firstLine.begin();
    auto secondWriteIt = secondLine.begin();

    auto const& a = firstIt->amplitude;
    auto const& b = secondIt->amplitude;
    assert(std::hypot(std::abs(a), std::abs(b)) > config::ATOL);

    double const invr = 1 / std::hypot(std::abs(a), std::abs(b));

    std::complex<double> c = b * invr;
    std::complex<double> s = a * invr;

    while (firstIt != firstLine.end()) {
        assert(secondIt != secondLine.end());

        assert(utils::isNotNull(firstIt->amplitude));
        assert(utils::isNotNull(secondIt->amplitude));

        assert(firstWriteIt <= firstIt);
        assert(secondWriteIt <= secondIt);

        if (firstIt->ket != secondIt->ket) [[unlikely]] {
            undo(firstLine, firstIt, firstHash, secondLine, secondIt, secondHash, c, s);
            return false;
        }

        auto newFirstAmplitude = c * firstIt->amplitude - s * secondIt->amplitude;
        auto newSecondAmplitude = std::conj(s) * firstIt->amplitude + std::conj(c) * secondIt->amplitude;

        if (utils::isNotNull(newFirstAmplitude)) [[likely]] {
            firstWriteIt->ket = firstIt->ket;
            firstWriteIt->amplitude = newFirstAmplitude;
            ++firstWriteIt;
        } else {
            firstHash -= firstIt->ket.hash();
        }

        if (utils::isNotNull(newSecondAmplitude)) [[likely]] {
            secondWriteIt->ket = secondIt->ket;
            secondWriteIt->amplitude = newSecondAmplitude;
            ++secondWriteIt;
        } else {
            secondHash -= secondIt->ket.hash();
        }

        ++firstIt;
        ++secondIt;
    }

    firstLine.erase(firstWriteIt, firstLine.end());
    secondLine.erase(secondWriteIt, secondLine.end());

    return true;
}

} // namespace  superpositeur