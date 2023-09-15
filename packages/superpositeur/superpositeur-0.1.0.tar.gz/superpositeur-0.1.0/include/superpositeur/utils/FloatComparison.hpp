#pragma once

#include <complex>

#include "superpositeur/config/CompileTimeConfiguration.hpp"

namespace superpositeur {
namespace utils {

/*

Comparing floating point numbers is a complex topic in general:
see for instance https://stackoverflow.com/questions/17333/what-is-the-most-effective-way-for-float-and-double-comparison

However, it is worth mentioning here that ALL the doubles in this program are somehow real or imaginary parts or modulus
of complex numbers involved in quantum states, and their modulus is always <= 1.

*/

inline constexpr bool isNotNull(double d) {
    return std::abs(d) >= config::ATOL;
}

inline constexpr bool isNull(double d) {
    return std::abs(d) < config::ATOL;
}

inline constexpr bool isNotNull(std::complex<double> c) {
    return isNotNull(c.real()) || isNotNull(c.imag());
}

inline constexpr bool isNull(std::complex<double> c) {
    return isNull(c.real()) && isNull(c.imag());
}

} // namespace utils
} // namespace  superpositeur