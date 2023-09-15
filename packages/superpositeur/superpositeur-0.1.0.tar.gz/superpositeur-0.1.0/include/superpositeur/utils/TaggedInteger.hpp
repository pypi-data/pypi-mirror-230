#pragma once

namespace superpositeur {
namespace utils {

template <typename T> struct TaggedInteger {
    explicit TaggedInteger(std::uint64_t x) : value(x) {}

    constexpr auto operator<=>(TaggedInteger const &other) const = default;
    
    constexpr void operator++() { ++value; }

    template <typename S>
    friend TaggedInteger<S> operator*(TaggedInteger<S> left,
                                      TaggedInteger<S> right);

    template <typename S>
    friend TaggedInteger<S> operator+(TaggedInteger<S> left,
                                      TaggedInteger<S> right);

    std::uint64_t value = 0;
};

template <typename T>
TaggedInteger<T> operator*(TaggedInteger<T> left,
                           TaggedInteger<T> right) {
    return {left.value * right.value};
}

template <typename T>
TaggedInteger<T> operator+(TaggedInteger<T> left,
                           TaggedInteger<T> right) {
    return {left.value + right.value};
}

} // namespace utils
} // namespace  superpositeur