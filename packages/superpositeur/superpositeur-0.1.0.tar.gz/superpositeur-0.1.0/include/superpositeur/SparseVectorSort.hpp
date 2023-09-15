#include "superpositeur/Common.hpp"
#include <algorithm>
#include <execution>
#include <chrono>
#include <iostream>
#include <deque>

namespace superpositeur {

template <std::uint64_t MaxNumberOfQubits>
bool isSortedOnIndices(typename SparseVector<MaxNumberOfQubits>::iterator begin, typename SparseVector<MaxNumberOfQubits>::iterator end, BasisVector<MaxNumberOfQubits> indices) {
    return std::is_sorted(begin, end, [indices](auto const left, auto const right) {
        return (left.ket & indices) < (right.ket & indices);
    });
}

template <typename Iterator, typename Comp, typename Predicate>
Iterator inplace_merge_aslongas(Iterator begin, Iterator mid, Comp&& comp, Predicate&& pred) {
    auto end = mid;
    while (pred(end)) {
        ++end;
    }

    std::inplace_merge(begin, mid, end, comp);

    return end;
}

template <typename Iterator, typename Comp, typename Predicate>
Iterator inplace_merge_aslongas_experimental(Iterator begin, Iterator mid, Comp&& comp, Predicate&& pred) {
    std::deque<typename Iterator::value> buffer;
    auto write = begin;
    auto second = mid;
    while (pred(write)) {
        assert(static_cast<int64_t>(buffer.size()) <= std::distance(begin, mid));
        assert(write <= second);

        if (buffer.empty()) {
            if (!pred(second) || comp(*write, *second)) {
                ++write;
                continue;
            }

            if (write < mid) {
                buffer.push_back(*write);
            }

            *write = *second;
            ++write;
            ++second;
            continue;
        }

        if (write >= mid) {
            if (!pred(second)) {
                for (auto x: buffer) {
                    *write = x;
                    ++write;
                }
                buffer.clear();
                break;
            }

            if (comp(buffer.front(), *second)) {
                *write = buffer.front();
                buffer.pop_front();
                ++write;
            } else {
                *write = *second;
                ++write;
            }
        } else {
            if (!pred(second)) {
                for (auto toPush = write; write != mid; ++write) {
                    buffer.push_back(*toPush);
                }

                assert(static_cast<int64_t>(buffer.size()) == std::distance(write, second));
                while (!buffer.empty()) {
                    assert(!pred(write));
                    *write = buffer.front();
                    buffer.pop_front();
                    ++write;
                }
                break;
            }

            auto min = std::min({ *write, *second, buffer.front() }, comp);
            
            if (!comp(min, second) && !comp(second, min)) {
                buffer.push_back(*write);
                *write = *second;
                ++write;
                ++second;
            } else if (!comp(min, write) && !comp(write, min)) {
                if (write == second) {
                    ++second;
                }
                ++write;
            } else {
                buffer.push_back(*write);
                *write = buffer.front();
                buffer.pop_front();
                ++write;
            }
        }
    }

    return write;
}

template <std::uint64_t MaxNumberOfQubits>
void removeSortIndexImpl(SparseVector<MaxNumberOfQubits> &data, BasisVector<MaxNumberOfQubits> currentSortIndices, std::uint64_t indexToRemove) {
    assert(currentSortIndices.test(indexToRemove));
    
    assert(isSortedOnIndices(data.begin(), data.end(), currentSortIndices));

    auto outputSortIndices = currentSortIndices;
    outputSortIndices.set(indexToRemove, false);

    // auto mask = (indexToRemove + 1 >= MaxNumberOfQubits) ? BasisVector<MaxNumberOfQubits>() : (((~BasisVector<MaxNumberOfQubits>()) << (indexToRemove + 1)) & currentSortIndices);
    // assert(isSortedOnIndices(data.begin(), data.end(), mask));

    // auto it = data.begin();
    // while (it != data.end()) {
    //     auto currentMask = it->ket & mask;
        
    //     if (it->ket.test(indexToRemove)) {
    //         it = std::find_if(it, data.end(), [mask, currentMask, indexToRemove](auto x) { return (x.ket & mask) != currentMask && !x.ket.test(indexToRemove); });
    //         continue;
    //     }
        
    //     auto one = std::find_if(it, data.end(), [indexToRemove](auto x) { return x.ket.test(indexToRemove); });

    //     if (one == data.end() || (one->ket & mask) != currentMask) {
    //         it = one;
    //         continue;
    //     }

    //     assert(std::all_of(it, std::next(one), [mask, currentMask](auto x) { return (x.ket & mask) == currentMask; }));
    //     assert(isSortedOnIndices(it, one, outputSortIndices));

    //     it = inplace_merge_aslongas(it, one, [outputSortIndices](auto left, auto right) { return (left.ket & outputSortIndices) < (right.ket & outputSortIndices); }, [&data, mask, currentMask](auto x) { return x != data.end() && (x->ket & mask) == currentMask; });
    // }

    auto it = std::find_if(data.begin(), data.end(), [indexToRemove](auto x) { return !x.ket.test(indexToRemove); });
    while (it != data.end()) {
        assert(!it->ket.test(indexToRemove));
        auto mid = std::find_if(it, data.end(), [indexToRemove](auto x) { return x.ket.test(indexToRemove); });
        auto end = std::find_if(mid, data.end(), [indexToRemove](auto x) { return !x.ket.test(indexToRemove); });

        assert(end == data.end() || ((std::next(end, -1)->ket & outputSortIndices) < (end->ket & outputSortIndices)));

        if (mid == data.end() || mid == end) {
            it = end;
            continue;
        }

        if ((mid->ket & outputSortIndices) < (std::next(mid, -1)->ket & outputSortIndices)) {
            // FIXME: ranges can be smaller
            std::inplace_merge(it, mid, end, [outputSortIndices](auto left, auto right) { return (left.ket & outputSortIndices) < (right.ket & outputSortIndices); });
        }

        it = end;
    }

    assert(isSortedOnIndices(data.begin(), data.end(), outputSortIndices));
}


template <std::uint64_t MaxNumberOfQubits>
void removeSortIndices(SparseVector<MaxNumberOfQubits>& data, BasisVector<MaxNumberOfQubits> currentSortIndices, BasisVector<MaxNumberOfQubits> sortIndicesToRemove) {
    assert(isSortedOnIndices(data.begin(), data.end(), currentSortIndices));

    assert((sortIndicesToRemove & currentSortIndices) == sortIndicesToRemove);

    if (sortIndicesToRemove.empty()) {
        return;
    }

    auto startTime = std::chrono::steady_clock::now();

    for (std::uint64_t i = 0; i < MaxNumberOfQubits; ++i) {
        if (sortIndicesToRemove.test(i)) {
            removeSortIndexImpl(data, currentSortIndices, i);
            currentSortIndices.set(i, false);
        }
    }

    auto endTime = std::chrono::steady_clock::now();

    INSTRU << "removeSortIndices," << data.size() << "," << std::chrono::duration_cast<std::chrono::nanoseconds>(endTime - startTime).count() << "," << currentSortIndices << "," << sortIndicesToRemove << std::endl;

    assert(isSortedOnIndices(data.begin(), data.end(), currentSortIndices));
}

template <std::uint64_t MaxNumberOfQubits>
void addSortIndexImpl(SparseVector<MaxNumberOfQubits> &data, std::uint64_t index, BasisVector<MaxNumberOfQubits> desiredSortIndices) {
    auto mask = (index + 1 < MaxNumberOfQubits) ? ((~BasisVector<MaxNumberOfQubits>()) << (index + 1)) : BasisVector<MaxNumberOfQubits>();
    mask &= desiredSortIndices;

    auto it = data.begin();
    while (it != data.end()) {
        auto current = it->ket & mask;
        auto endPartition = std::find_if(it, data.end(), [current, mask](auto x) { return (x.ket & mask) != current; });
        std::stable_partition(it, endPartition, [index](auto x) { return !x.ket.test(index); });
        it = endPartition;
    }
}

template <std::uint64_t MaxNumberOfQubits>
void addSortIndices(SparseVector<MaxNumberOfQubits>& data, BasisVector<MaxNumberOfQubits> currentSortIndices, BasisVector<MaxNumberOfQubits> desiredSortIndices) {
    assert(isSortedOnIndices(data.begin(), data.end(), currentSortIndices));

    assert((currentSortIndices & desiredSortIndices) == currentSortIndices);

    auto sortIndicesToAdd = (~currentSortIndices) & desiredSortIndices;

    if (sortIndicesToAdd.empty()) {
        return;
    }

    auto startTime = std::chrono::steady_clock::now();

    for (std::uint64_t i = 1; i <= MaxNumberOfQubits; ++i) {
        std::uint64_t index = MaxNumberOfQubits - i;
        if (sortIndicesToAdd.test(index)) {
            addSortIndexImpl(data, index, desiredSortIndices);
        }
    }

    auto endTime = std::chrono::steady_clock::now();

    INSTRU << "addSortIndices," << data.size() << "," << std::chrono::duration_cast<std::chrono::nanoseconds>(endTime - startTime).count() << "," << currentSortIndices << "," << sortIndicesToAdd << std::endl;

    assert(isSortedOnIndices(data.begin(), data.end(), desiredSortIndices));
}

template <std::uint64_t MaxNumberOfQubits>
void sortSparseVector(SparseVector<MaxNumberOfQubits>& data, BasisVector<MaxNumberOfQubits> currentSortIndices, BasisVector<MaxNumberOfQubits> desiredSortIndices) {
    assert(isSortedOnIndices<MaxNumberOfQubits>(data.begin(), data.end(), currentSortIndices));

    // FIXME: if sortIndicesToRemove.countrZero() is too small, but non-zero, do regular sort instead?

    auto sortIndicesToRemove = currentSortIndices & (~desiredSortIndices);
    removeSortIndices(data, currentSortIndices, sortIndicesToRemove);

    auto commonSortIndices = currentSortIndices & desiredSortIndices;
    addSortIndices(data, commonSortIndices, desiredSortIndices);

    assert(isSortedOnIndices(data.begin(), data.end(), desiredSortIndices));
}

}