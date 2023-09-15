#pragma once

#include <complex>
#include <algorithm>
#include <vector>
#include <numeric>
#include <iomanip>
#include <set>
#include <random>
#include <cassert>
#include <span>

#include "superpositeur/utils/FloatComparison.hpp"

namespace superpositeur {

// FIXME: what about using valarray?

class Matrix final {
public:
    using Value = std::complex<double>;

    Matrix(std::uint64_t n, std::uint64_t m)
        : numberOfRows(n), numberOfCols(m),
          data(getNumberOfRows() * getNumberOfCols(), 0.) {}

    Matrix(std::uint64_t n) : Matrix(n, n) {}

    explicit Matrix(
        std::initializer_list<std::initializer_list<std::complex<double>>> init)
        : Matrix(init.size(),
                 init.begin() == init.end() ? 0 : init.begin()->size()) {
        std::uint64_t rowIndex = 0;
        for (auto const &row : init) {
            assert(row.size() == init.begin()->size() &&
                   "Initializer list is not a proper matrix");
            std::uint64_t colIndex = 0;
            for (auto x : row) {
                data[rowIndex * getNumberOfCols() + colIndex] = x;
                ++colIndex;
            }
            ++rowIndex;
        }
    }

    inline std::uint64_t getNumberOfRows() const { return numberOfRows; }

    inline std::uint64_t getNumberOfCols() const { return numberOfCols; }

    bool isSquare() const {
        return getNumberOfRows() == getNumberOfCols();
    }

    inline Value get(std::uint64_t i, std::uint64_t j) const {
        assert(areValidIndices(i, j));

        return data[i * getNumberOfCols() + j];
    }

    inline std::span<Value const> line(std::uint64_t i) const {
        return { data.begin() + i * getNumberOfCols(), data.begin() + (i + 1) * getNumberOfCols() };
    }

    inline void set(std::uint64_t i, std::uint64_t j, Value v) {
        assert(areValidIndices(i, j));

        data[i * getNumberOfCols() + j] = v;
    }

    inline void add(std::uint64_t i, std::uint64_t j, Value v) {
        assert(areValidIndices(i, j));
        
        data[i * getNumberOfCols() + j] += v;
    }

    Matrix dagger() const {
        Matrix result(getNumberOfCols(), getNumberOfRows());
        for (std::uint64_t i = 0; i < getNumberOfCols(); ++i) {
            for (std::uint64_t j = 0; j < getNumberOfRows(); ++j) {
                result.set(i, j, std::conj(get(j, i)));
            }
        }

        return result;
    }

    Matrix operator*(Matrix const &other) const {
        assert(getNumberOfCols() == other.getNumberOfRows() &&
               "Can't multiply matrices with incompatible sizes");
        
        Matrix result(getNumberOfRows(), other.getNumberOfCols());
        for (std::uint64_t i = 0; i < getNumberOfRows(); ++i) {
            for (std::uint64_t j = 0; j < other.getNumberOfCols(); ++j) {
                for (std::uint64_t k = 0; k < getNumberOfCols(); ++k) {
                    result.add(i, j, get(i, k) * other.get(k, j));
                }
            }
        }

        return result;
    }

    inline bool operator==(Matrix const &other) const {
        if (other.getNumberOfRows() != getNumberOfRows() ||
            other.getNumberOfCols() != getNumberOfCols()) {
            return false;
        }
        
        return std::equal(data.begin(), data.end(), other.data.begin(), [](Value left, Value right) {
            return utils::isNull(left - right);
        });
    }

    inline void print(std::ostream &os) const {
        os << "\n"
           << std::string(15 * getNumberOfCols(), '-') << "\n";

        for (std::uint64_t i = 0; i < getNumberOfRows(); ++i){
            for (std::uint64_t j = 0; j < getNumberOfCols(); ++j){
                os << std::fixed << std::setprecision(3) << " " << (get(i, j).real() < 0 ? "-" : "+") << std::setw(5) << std::abs(get(i, j).real())
                  << (get(i, j).imag() < 0 ? "-" : "+") << "i" << std::setw(5) << std::abs(get(i, j).imag()) <<  " ";
            }
            os << "\n";
        }

        os << std::string(15 * getNumberOfCols(), '-');
    }

    void operator*=(Matrix const &other) {
        assert(getNumberOfCols() == other.getNumberOfRows() &&
               other.getNumberOfRows() == other.getNumberOfCols());
        
        for (std::uint64_t rowIndex = 0; rowIndex < getNumberOfRows(); ++rowIndex) {
            auto rowBegin = data.begin() + rowIndex * getNumberOfCols();
            auto rowEnd = rowBegin + getNumberOfCols();
            std::vector<Value> oldRow(rowBegin, rowEnd);
            std::fill(rowBegin, rowEnd, 0.);

            for (std::uint64_t i = 0; i < other.data.size(); ++i) {
                auto otherRowIndex = i / other.getNumberOfCols();
                auto otherColIndex = i % other.getNumberOfCols();
                add(rowIndex, otherColIndex, oldRow[otherRowIndex] * other.data[i]);
            }
        }
    }

    void operator*=(double d) {
        for (auto &v: data) {
            v *= d;
        }
    }

    void multiplyLeft(Matrix const &other) {
        assert(other.getNumberOfCols() == getNumberOfRows() &&
               other.getNumberOfRows() == other.getNumberOfCols());
        
        UnderlyingT newData(data.size(), 0.);

        for (std::uint64_t i = 0; i < other.data.size(); ++i) {
            for (std::uint64_t colIndex = 0; colIndex < getNumberOfCols(); ++colIndex) {
                auto const otherRowIndex = i / other.getNumberOfCols();
                auto const otherColIndex = i % other.getNumberOfCols();
                assert(i == otherRowIndex * other.getNumberOfCols() + i % other.getNumberOfCols());

                newData[otherRowIndex * getNumberOfCols() + colIndex] += other.data[i] * get(otherColIndex, colIndex);
            }
        }

        data.swap(newData);
    }

    void operator+=(Matrix const &other) {
        assert(getNumberOfRows() == other.getNumberOfRows() &&
               getNumberOfCols() == other.getNumberOfCols() &&
               "Can't add matrices of different sizes");
        for (std::uint64_t i = 0; i < getNumberOfRows(); ++i) {
            for (std::uint64_t j = 0; j < getNumberOfCols(); ++j) {
                add(i, j, other.get(i, j));
            }
        }
    }

    double norm() const {
        return std::transform_reduce(data.cbegin(), data.cend(), 0., std::plus{}, [](Value v) { return std::norm(v); });
    };

    friend Matrix operator*(double d, Matrix m);

    friend Matrix applyQubitOperandPermutation(Matrix input, std::vector<std::uint64_t> const& operands);

private:
    using UnderlyingT = std::vector<std::complex<double>>; // inlined? based on matrix size

    inline bool areValidIndices(std::uint64_t i, std::uint64_t j) const {
        assert(data.size() == getNumberOfRows() * getNumberOfCols());

        return i < getNumberOfRows() && j < getNumberOfCols();
    }

    std::uint64_t const numberOfRows = 0;
    std::uint64_t const numberOfCols = 0;
    UnderlyingT data;
};

inline std::ostream &operator<<(std::ostream &os, Matrix const &m) {
    m.print(os);
    return os;
}

inline Matrix operator*(double d, Matrix m) {
    for (auto &v : m.data) {
        v *= d;
    }

    return m;
}

inline double computeSpectralRadius(Matrix const &matrix) {
    // Power iterations.

    assert(matrix.isSquare());
    static std::uint64_t const MAX_ITERATIONS = 1000;

    Matrix v(matrix.getNumberOfCols(), 1);

    for (std::uint64_t i = 0; i < v.getNumberOfRows(); ++i) {
        // static std::uniform_real_distribution<double> dis(0., 1.);
        // static std::mt19937_64 gen(0xDEADBEEF);
        // v.set(i, 0, std::complex<double>{dis(gen), dis(gen)});
        v.set(i, 0, std::complex<double>{.5, .5});
    }

    std::uint64_t iteration = 0;
    double previousVNorm = 0.;
    while (true) {
        v.multiplyLeft(matrix);

        double vNorm = std::sqrt(v.norm());

        assert(utils::isNotNull(vNorm));

        if (iteration >= MAX_ITERATIONS) {
            return vNorm;
        } else if (utils::isNull(previousVNorm - vNorm)) {
            return vNorm;
        } else {
            ++iteration;
            previousVNorm = vNorm;
        }

        double vNormInv = 1 / vNorm;

        v *= vNormInv;
    }
}

} // namespace  superpositeur