#include "superpositeur/MixedState.hpp"

namespace superpositeur {

bool MixedState::isConsistent() const {
    auto dataSize = std::visit([](auto const& data) { return data.size(); }, dataVariant);

    if (dataSize == 0) {
        return false;
    }

    if (hashes.size() != dataSize) {
        return false;
    }

    if (std::visit([](auto const& data) { return std::ranges::any_of(data, [](auto const& x) { return x.empty(); }); }, dataVariant)) {
        return false;
    }

    return std::visit([](auto const& data) {
        double accumulator = 0.;
        for (auto const& v: data) {
            accumulator = std::accumulate(v.begin(), v.end(), accumulator, [](auto acc, auto x) { return acc + std::norm(x.amplitude); });
        }
        return utils::isNull(accumulator - 1.);
    }, dataVariant);
}

} // namespace  superpositeur