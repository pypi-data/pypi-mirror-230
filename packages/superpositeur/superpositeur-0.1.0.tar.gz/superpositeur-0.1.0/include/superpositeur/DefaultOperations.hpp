#pragma once

#include "superpositeur/Common.hpp"
#include "superpositeur/Matrix.hpp"

namespace superpositeur {
namespace default_operations {

using namespace std::complex_literals;

inline double PI = 3.141592653589793238462643383279502884L;
inline double SQRT_2 = 1.414213562373095048801688724209698078L;

inline Matrix IDENTITY{{1, 0},
                       {0, 1}};

inline Matrix X{{0, 1},
                       {1, 0}};

inline Matrix Y{{0, -1i},
                       {1i, 0}};

inline Matrix Z{{1, 0},
                       {0, -1}};

inline Matrix S{{1, 0},
                       {0, 1i}};

inline Matrix SDAG = S.dagger();

inline Matrix T{{1, 0},
                       {0, 1 / SQRT_2 + 1i / SQRT_2}};

inline Matrix TDAG = T.dagger();

inline Matrix RX(double theta) {
    return Matrix{{std::cos(theta / 2), -1i * std::sin(theta / 2)},
                          {-1i * std::sin(theta / 2), std::cos(theta / 2)}};
}

inline auto X90 = RX(PI / 2);
inline auto MX90 = RX(-PI / 2);

inline Matrix RY(double theta) {
    return Matrix{{std::cos(theta / 2), -std::sin(theta / 2)},
                          {std::sin(theta / 2), std::cos(theta / 2)}};
}

inline auto Y90 = RY(PI / 2);
inline auto MY90 = RY(-PI / 2);

inline Matrix RZ(double theta) {
    return Matrix{{std::cos(theta / 2) - 1i * std::sin(theta / 2), 0},
            {0, std::cos(theta / 2) + 1i * std::sin(theta / 2)}};
}

inline auto Z90 = RZ(PI / 2);
inline auto MZ90 = RZ(-PI / 2);

inline Matrix H{{1 / SQRT_2, 1 / SQRT_2},
                       {1 / SQRT_2, -1 / SQRT_2}};

inline Matrix CNOT{
    {1, 0, 0, 0},
    {0, 1, 0, 0},
    {0, 0, 0, 1},
    {0, 0, 1, 0}};

inline Matrix SWAP{
    {1, 0, 0, 0},
    {0, 0, 1, 0},
    {0, 1, 0, 0},
    {0, 0, 0, 1}};

inline Matrix CZ{
    {1, 0, 0, 0},
    {0, 1, 0, 0},
    {0, 0, 1, 0},
    {0, 0, 0, -1}};

inline Matrix CR(double theta) {
    return Matrix{{1, 0, 0, 0},
                          {0, 1, 0, 0},
                          {0, 0, 1, 0},
                          {0, 0, 0, std::cos(theta) + 1i * std::sin(theta)}};
}

inline Matrix CRk(std::int64_t k) {
    double f = std::pow(2., -k);

    return Matrix{{1, 0, 0, 0},
                   {0, 1, 0, 0},
                   {0, 0, 1, 0},
                   {0, 0, 0, std::polar(1., 2 * PI * f)}};
}

inline Matrix TOFFOLI{
    {1, 0, 0, 0, 0, 0, 0, 0},
    {0, 1, 0, 0, 0, 0, 0, 0},
    {0, 0, 1, 0, 0, 0, 0, 0},
    {0, 0, 0, 1, 0, 0, 0, 0},
    {0, 0, 0, 0, 1, 0, 0, 0},
    {0, 0, 0, 0, 0, 1, 0, 0},
    {0, 0, 0, 0, 0, 0, 0, 1},
    {0, 0, 0, 0, 0, 0, 1, 0}};

inline std::initializer_list<Matrix> MEAS_Z{
    Matrix{{1, 0},
                 {0, 0}},
    Matrix{{0, 0},
                 {0, 1}}};

inline std::initializer_list<Matrix> MEAS_Z_STORE{
    Matrix{{1, 0, 0, 0},
                 {0, 0, 0, 0},
                 {0, 0, 0, 0},
                 {0, 0, 0, 0}},
    Matrix{{0, 1, 0, 0},
                 {0, 0, 0, 0},
                 {0, 0, 0, 0},
                 {0, 0, 0, 0}},
    Matrix{{0, 0, 0, 0},
                 {0, 0, 0, 0},
                 {0, 0, 0, 0},
                 {0, 0, 1, 0}},
    Matrix{{0, 0, 0, 0},
                 {0, 0, 0, 0},
                 {0, 0, 0, 0},
                 {0, 0, 0, 1}}};

// FIXME
inline std::initializer_list<Matrix> MEAS_X{
    Matrix{{1 / 2., 1 / 2.},
                 {1 / 2., 1 / 2.}},
    Matrix{{1 / 2., -1 / 2.},
                 {-1 / 2., 1 / 2.}}};
inline std::initializer_list<Matrix> MEAS_Y{
    Matrix{{1 / 2., 1i / 2.},
                 {1i / 2., -1 / 2.}},
    Matrix{{1 / 2., -1i / 2.},
                 {-1i / 2., 1 / 2.}}};
inline std::initializer_list<Matrix> PREP_Z{Matrix{{1, 0},
                                                               {0, 0}},
                                                  Matrix{{0, 1},
                                                               {0, 0}}};
inline std::initializer_list<Matrix> PREP_Z_SWAP{
    Matrix{{1, 1},
                 {0, 0}}};
inline std::initializer_list<Matrix> PREP_Y{
    Matrix{{1 / 2., 1i / 2.},
                 {1i / 2., -1 / 2.}},
    Matrix{{1 / 2., -1i / 2.},
                 {1i / 2., -1 / 2.}}};

inline KrausOperators DEPOLARIZING_CHANNEL(double lambda) {
    lambda = std::min(1., std::max(0., lambda));

    auto k0 = std::sqrt(1. - 3 * lambda / 4) * IDENTITY;
    auto k1 = std::sqrt(lambda / 4) * X;
    auto k2 = std::sqrt(lambda / 4) * Y;
    auto k3 = std::sqrt(lambda / 4) * Z;

    return {k0, k1, k2, k3};
}

inline KrausOperators AMPLITUDE_DAMPING(double gamma) {
    gamma = std::min(1., std::max(0., gamma));

    auto e0 = Matrix{{1, 0},
                     {0, std::sqrt(1 - gamma)}};
    auto e1 = Matrix{{0, std::sqrt(gamma)},
                     {0, 0}};

    return {e0, e1};
}

inline KrausOperators PHASE_DAMPING(double lambda) {
    lambda = std::min(1., std::max(0., lambda));

    auto e0 = Matrix{{1, 0},
                     {0, std::sqrt(1 - lambda)}};
    auto e1 = Matrix{{0, 0},
                     {0, std::sqrt(lambda)}};

    return {e0, e1};
}

// inline Operations createDefaultOperations() {
//     std::unordered_map<std::string, std::any> defaultOperations;

//     defaultOperations.add("id", {Q}, IDENTITY);
//     defaultOperations.add("x", {Q}, X);
//     defaultOperations.add("x90", {Q}, X90);
//     defaultOperations.add("mx90", {Q}, MX90);
//     defaultOperations.add("y", {Q}, Y);
//     defaultOperations.add("y90", {Q}, Y90);
//     defaultOperations.add("my90", {Q}, MY90);
//     defaultOperations.add("z", {Q}, Z);
//     defaultOperations.add("z90", {Q}, Z90);
//     defaultOperations.add("mz90", {Q}, MZ90);
//     defaultOperations.add("s", {Q}, S);
//     defaultOperations.add("sdag", {Q}, SDAG);
//     defaultOperations.add("t", {Q}, T);
//     defaultOperations.add("tdag", {Q}, TDAG);
//     defaultOperations.add("h", {Q}, H);
//     defaultOperations.add("cnot", {Q, Q}, CNOT);
//     defaultOperations.add("swap", {Q, Q}, SWAP);
//     defaultOperations.add("cz", {Q, Q}, CZ);
//     defaultOperations.add("toffoli", {Q, Q, Q}, TOFFOLI);
//     defaultOperations.add("measure", {Q}, MEAS_Z);
//     defaultOperations.add("measure_z", {Q}, MEAS_Z);
//     // defaultOperations.add("measure_x", {Q, B}, MEAS_X); // FIXME
//     // defaultOperations.add("measure_y", {Q, B}, MEAS_Y);
//     defaultOperations.add("prep", {Q}, PREP_Z);
//     defaultOperations.add("prep_z", {Q}, PREP_Z);
//     defaultOperations.add("rx", {Q, D}, RX);
//     defaultOperations.add("ry", {Q, D}, RY);
//     defaultOperations.add("rz", {Q, D}, RZ);
//     defaultOperations.add("cr", {Q, Q, D}, CR);
//     defaultOperations.add("crk", {Q, Q, I}, CRk);
//     defaultOperations.add("depolarizing_channel", {Q, D}, DEPOLARIZING_CHANNEL);
//     defaultOperations.add("phase_damping", {Q, D}, PHASE_DAMPING);
//     defaultOperations.add("amplitude_damping", {Q, D}, AMPLITUDE_DAMPING);

//     return defaultOperations;
// }

// inline Operations defaultOperations = createDefaultOperations();

} // namespace default_operations
} // namespace  superpositeur