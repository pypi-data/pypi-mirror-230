#pragma once

#include "superpositeur/utils/TaggedInteger.hpp"

namespace superpositeur {

using QubitIndex = utils::TaggedInteger<struct QubitIndexTag>;

using MeasurementRegisterIndex =
    utils::TaggedInteger<struct MeasurementRegisterIndexTag>;

} // namespace  superpositeur