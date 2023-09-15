#pragma once

#include "superpositeur/Matrix.hpp"
#include "superpositeur/Common.hpp"

namespace superpositeur {

class QuantumOperation {
public:
    static void checkValidKrausOperatorSet(KrausOperators const &krausOperators) {
        if (krausOperators.empty()) {
            throw std::runtime_error(std::string("Kraus operators set is empty"));
        }

        // All Kraus operator matrices need to have the same size.
        for (auto const &m : krausOperators) {
            if (!m.isSquare()) {
                throw std::runtime_error(std::string("Kraus operators are not all square matrices"));
            }

            if (m.getNumberOfRows() != krausOperators.begin()->getNumberOfRows()) {
                throw std::runtime_error(std::string("Kraus operators don't all have the same size"));
            }
        }

        // Size of Kraus operators need to be a power of two.
        if (!std::has_single_bit(krausOperators.begin()->getNumberOfRows())) {
            throw std::runtime_error(std::string("Kraus operators size is not a power of two"));
        }

        // Kraus operators need to satisfy the completeness relation.
        // That is: all the eigenvalues of the sum of E_k^t * E_k need to <= 1.
        Matrix accumulator(krausOperators.begin()->getNumberOfRows());
        for (auto const &m : krausOperators) {
            accumulator += m.dagger() * m;
        }

        double spectralRadius = computeSpectralRadius(accumulator);

        if (spectralRadius > 1. + config::ATOL) {
            throw std::runtime_error(std::string("Kraus operators are not non-trace-increasing"));
        }
    }

};

} // namespace  superpositeur