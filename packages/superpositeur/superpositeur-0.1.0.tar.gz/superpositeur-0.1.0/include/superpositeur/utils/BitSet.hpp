#pragma once

#include <array>
#include <cassert>
#include <climits>
#include <limits>
#include <string>
#include <bit>
#include <optional>
#include <compare>
#include <algorithm>

#ifdef __BMI2__
#include <x86gprintrin.h> // pdep, pext
#endif

namespace superpositeur {
namespace utils {

inline bool getBit(std::uint64_t x, std::uint64_t index) {
    return (x >> index) & 1; // FIXME: use pext?
}

inline void setBit(std::uint64_t &x, std::uint64_t index, bool value) {
    assert(index < 64);
    x = (x & ~(1UL << index)) | (static_cast<std::uint64_t>(value) << index); // FIXME: use pdep?
}

#ifdef _BMI2INTRIN_H_INCLUDED
// __attribute__((__target__ ("bmi2")))
inline std::uint64_t pext_wrapper(std::uint64_t source, std::uint64_t mask) {
    return _pext_u64(source, mask);
}
#else
// __attribute__((__target__ ("default")))
inline std::uint64_t pext_wrapper(std::uint64_t source, std::uint64_t mask) {
    // FIXME: do this better? And test.
    std::uint64_t result = 0;
    std::uint64_t setBits = 0;
    for (std::uint64_t i = 0; i < 64; ++i) {
        std::uint64_t b = 1 << i;
        if ((mask & b) != 0) {
            assert(setBits <= i);
            result |= ((source & b) >> (i - setBits));
            ++setBits;
        }
    }
    return result;
}
#endif

#ifdef _BMI2INTRIN_H_INCLUDED
// __attribute__((__target__ ("bmi2")))
inline std::uint64_t pdep_wrapper(std::uint64_t source, std::uint64_t mask) {
    return _pdep_u64(source, mask);
}
#else
// __attribute__((__target__ ("default")))
inline std::uint64_t pdep_wrapper(std::uint64_t source, std::uint64_t mask) {
    // FIXME: do this better? And test.
    std::uint64_t result = 0;
    std::uint64_t setBits = 0;
    for (std::uint64_t i = 0; i < 64; ++i) {
        std::uint64_t b = 1 << i;
        if ((mask & b) != 0) {
            assert(setBits <= i);
            result |= ((source & (1 << setBits)) << (i - setBits));
            ++setBits;
        }
    }
    return result;
}
#endif

// std::bitset does not have an operator<. Here, only multiples of 64 bits are allowed.

template <std::uint64_t NumberOfBits> class BitSet {

private:
    static constexpr std::uint64_t BITS_PER_UNIT =
        CHAR_BIT * sizeof(std::uint64_t);
    static_assert(BITS_PER_UNIT == 64);

    static_assert(NumberOfBits % BITS_PER_UNIT == 0);

public:
    static constexpr std::uint64_t STORAGE_SIZE = NumberOfBits / BITS_PER_UNIT;

    static constexpr std::uint64_t getNumberOfBits() { return NumberOfBits; }

    BitSet() = default;

    BitSet(std::string_view s) {
        assert(s.size() <= NumberOfBits);
        std::uint64_t i = 0;
        for (auto it = s.rbegin(); it != s.rend(); ++it, ++i) {
            set(i, *it == '1' ? true : false);
        }
    }

    BitSet(std::uint64_t s) {
        data[0] = s;
    }

    inline std::uint64_t popcount() const {
        std::uint64_t result = 0;
        for (auto const& x: data) {
            result += std::popcount(x);
        }

        return result;
    }

    template <std::uint64_t MaskNumberOfBits>
    void operator&=(BitSet<MaskNumberOfBits> mask) {
        for (std::uint64_t i = 0; i < std::min(STORAGE_SIZE, BitSet<MaskNumberOfBits>::STORAGE_SIZE); ++i) {
            data[i] &= mask.data[i];
        }
    }

    inline void reset() { data = {}; }

    inline bool test(std::uint64_t index) const {
        assert(index < NumberOfBits &&
               "BitSet::test bit index out of range");
        return getBit(data[index / BITS_PER_UNIT], index % BITS_PER_UNIT);
    }

    inline void set(std::uint64_t index, bool value = true) {
        assert(index < NumberOfBits &&
               "BitSet::set bit index out of range");
        setBit(data[index / BITS_PER_UNIT], index % BITS_PER_UNIT, value);
    }

    inline auto operator<=>(BitSet<NumberOfBits> const &other) const = default;

    inline bool operator==(BitSet<NumberOfBits> const &other) const = default;

    inline void operator^=(BitSet<NumberOfBits> const &other) {
        for (std::uint64_t i = 0; i < STORAGE_SIZE; ++i) {
            data[i] ^= other.data[i];
        }
    }

    inline BitSet<NumberOfBits> operator~() const {
        BitSet<NumberOfBits> result = *this;
        for (std::uint64_t i = 0; i < result.STORAGE_SIZE; ++i) {
            result.data[i] = ~result.data[i];
        }
        return result;
    }

    inline void operator&=(BitSet<NumberOfBits> const &other) {
        for (std::uint64_t i = 0; i < STORAGE_SIZE; ++i) {
            data[i] &= other.data[i];
        }
    }

    inline BitSet<NumberOfBits> operator&(BitSet<NumberOfBits> const &other) const {
        auto result = *this;
        result &= other;
        return result;
    }

    inline void operator|=(BitSet<NumberOfBits> const &other) {
        for (std::uint64_t i = 0; i < STORAGE_SIZE; ++i) {
            data[i] |= other.data[i];
        }
    }

    inline BitSet<NumberOfBits> operator|(BitSet<NumberOfBits> const &other) const {
        auto result = *this;
        result |= other;
        return result;
    }

    inline BitSet<NumberOfBits> operator^(BitSet<NumberOfBits> const &other) const {
        auto result = *this;
        result ^= other;
        return result;
    }

    inline void operator++() {
        for (auto &d : data) {
            if (d < std::numeric_limits<std::uint64_t>::max()) {
                ++d;
                return;
            }
            d = 0;
        }
    }

    std::uint64_t toUInt64() const {
#ifndef NDEBUG
        for (std::uint64_t i = 1; i < STORAGE_SIZE; ++i) {
            assert(data[i] == 0);
        }
#endif

        return data[0];
    }

    std::string toString() const {
        std::string result(NumberOfBits, '0');
        for (std::uint64_t i = 0; i < NumberOfBits; ++i) {
            if (test(NumberOfBits - i - 1)) {
                result[i] = '1';
            }
        }
        return result;
    }

    BitSet operator<<(std::uint64_t n) {
        BitSet result;

        if (n >= NumberOfBits) {
            return result;
        }

        std::uint64_t div = n / BITS_PER_UNIT;
        std::uint64_t rem = n % BITS_PER_UNIT;

        assert(div < STORAGE_SIZE);

        std::uint64_t topMask = rem == 0UL ? 0UL : (~0UL) << (BITS_PER_UNIT - rem);

        result.data[div] = data[0] << rem;
        for (std::uint64_t i = div + 1; i < STORAGE_SIZE; ++i) {
            result.data[i] = data[i - div] << rem;
            result.data[i] |= (data[i - div - 1] & topMask) >> (BITS_PER_UNIT - rem);
            // result.data[i] |= _pext_u64(data[i - div - 1], topMask); // This is also possible but uses pext intrinsics.
        }

        return result;
    }

    std::uint64_t hash() const {
        auto singleHash = [] (std::uint64_t x) {
            x = (x ^ (x >> 30)) * 0xbf58476d1ce4e5b9UL;
            x = (x ^ (x >> 27)) * 0x94d049bb133111ebUL;
            x = x ^ (x >> 31);
            return x;
        };

        std::uint64_t result = singleHash(data[STORAGE_SIZE - 1]);
        for (std::uint64_t i = 2; i <= STORAGE_SIZE; ++i) {
            result = 3 * result + singleHash(data[STORAGE_SIZE - i]);
        }
        return result + 1;
    }

    std::uint64_t countlZero() const {
        std::uint64_t result = 0;

        for (std::uint64_t i = 1; i <= STORAGE_SIZE; ++i) {
            std::uint64_t partialCountlZero = std::countl_zero(data[STORAGE_SIZE - i]);
            result += partialCountlZero;
            if (partialCountlZero < BITS_PER_UNIT) {
                return result;
            }
        }

        return result;
    }

    std::uint64_t countrZero() const {
        std::uint64_t result = 0;

        for (std::uint64_t i = 0; i < STORAGE_SIZE; ++i) {
            std::uint64_t partialCountrZero = std::countr_zero(data[i]);
            result += partialCountrZero;
            if (partialCountrZero < BITS_PER_UNIT) {
                return result;
            }
        }

        return result;
    }
    
    inline std::uint64_t bitWidth() const {
        return NumberOfBits - countlZero();
    }

    bool empty() const {
        return std::all_of(data.begin(), data.end(), [](auto x) { return x == 0; }); // FIXME: memcmp or sth?
    }

    template <std::size_t NewNumberOfBits>
    BitSet<NewNumberOfBits> cast() const {
        BitSet<NewNumberOfBits> result;
        for (std::uint64_t i = 0; i < std::min(result.STORAGE_SIZE, STORAGE_SIZE); ++i) {
            result.data[i] = data[i];
        }
        return result;
    }
    
    template<std::uint64_t> friend class BitSet;

    template <std::uint64_t MaskNumberOfBits>
    std::uint64_t pext(BitSet<MaskNumberOfBits> mask) const {
        assert(mask.popcount() <= BITS_PER_UNIT);

        std::uint64_t result = 0;
        std::uint64_t bitsDone = 0;
        for (std::uint64_t i = 0; i < std::min(STORAGE_SIZE, BitSet<MaskNumberOfBits>::STORAGE_SIZE); ++i) {
            std::uint64_t partial = pext_wrapper(data[i], mask.data[i]);
            result |= (partial << bitsDone);
            bitsDone += std::popcount(mask.data[i]);
        }
        return result;
    }

    template <std::uint64_t MaskNumberOfBits>
    BitSet pdep(std::uint64_t source, BitSet<MaskNumberOfBits> mask) const {
        assert(mask.popcount() <= BITS_PER_UNIT);

        BitSet result;
        std::uint64_t bitsDone = 0;
        for (std::uint64_t i = 0; i < std::min(STORAGE_SIZE, BitSet<MaskNumberOfBits>::STORAGE_SIZE); ++i) {
            std::uint64_t partial = pdep_wrapper(source >> bitsDone, mask.data[i]);
            result.data[i] = (data[i] & (~mask.data[i])) | partial;
            bitsDone += std::popcount(mask.data[i]);
        }

        return result;
    }

private:
    std::array<std::uint64_t, STORAGE_SIZE> data{};
};

template <std::uint64_t NumberOfBits>
inline std::ostream &operator<<(std::ostream &os, BitSet<NumberOfBits> const &bitset) {
    os << bitset.toString();
    return os;
}

static_assert(BitSet<64>::STORAGE_SIZE == 1);
static_assert(BitSet<128>::STORAGE_SIZE == 2);

} // namespace utils
} // namespace  superpositeur
