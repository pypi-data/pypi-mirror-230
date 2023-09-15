#include <atomic>
#include <thread>
#include <vector>

namespace superpositeur {
namespace utils {

// Single producer, multiple consumers.

template <typename T>
class RingBuffer {
public:
    RingBuffer(std::size_t capacity) : data(capacity, 0) {}

    void push(T val) { // Blocks if full.
        auto currentWriteIndex = writeIndex.load(std::memory_order_relaxed);
        auto nextWriteIndex = currentWriteIndex + 1;
        assert(nextWriteIndex <= data.size());

        if (nextWriteIndex == data.size()) {
            nextWriteIndex = 0;
        }
        
        if (nextWriteIndex == readIndexCache) {
            readIndex.wait(readIndexCache);
            readIndexCache = readIndex.load(std::memory_order_acquire);
            assert(nextWriteIndex != readIndexCache);
        }

        data[currentWriteIndex] = val;
        writeIndex.store(nextWriteIndex, std::memory_order_release);
    }

    bool pop(T &val) {
        std::lock_guard<std::mutex> guard(lock);

        auto const currentReadIndex = readIndex.load(std::memory_order_relaxed);
        if (currentReadIndex == writeIndexCache) {
            writeIndexCache = writeIndex.load(std::memory_order_acquire);
            if (currentReadIndex == writeIndexCache) {
                return false;
            }
        }

        val = data[currentReadIndex];
        auto nextReadIdx = currentReadIndex + 1;
        if (nextReadIdx == data.size()) {
            nextReadIdx = 0;
        }
        readIndex.store(nextReadIdx, std::memory_order_release);
        return true;
    }

private:
    std::vector<T> data;

    alignas(64) std::atomic<std::size_t> readIndex = 0;
    alignas(64) std::atomic<std::size_t> writeIndex = 0;
    alignas(64) std::size_t readIndexCache = 0;
    alignas(64) std::size_t writeIndexCache = 0;

    std::mutex lock;
};

}
}