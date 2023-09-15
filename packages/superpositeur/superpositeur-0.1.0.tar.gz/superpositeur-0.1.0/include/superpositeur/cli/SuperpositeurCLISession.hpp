#include "superpositeur/API.hpp"

#include <iostream>
#include <optional>
#include <vector>
#include <climits>
#include <cassert>
#include <charconv>
#include <unordered_map>
#include <stack>
#include <functional>
#include <algorithm>
#include <variant>

#include "superpositeur/MixedState.hpp"
#include "superpositeur/StrongTypes.hpp"
#include "superpositeur/DefaultOperations.hpp"

#ifdef SUPERPOSITEUR_WASM
#include <emscripten/bind.h>
#endif

namespace superpositeur {
namespace cli {

class SuperpositeurCLISession {
public:
    SuperpositeurCLISession() = default;

    std::string operator()(std::string const& input) {
        auto words = getWords(input);

        if (words.size() <= 0) {
            return "";
        }

        auto const& command = words[0];

        if (command == "p" || command == "print") {
            std::vector<QubitIndex> operands;
            
            for (std::uint64_t i = 1; i < words.size(); ++i) {
                auto qubitIndex = getQubit(words[i]);
                
                if (!qubitIndex) {
                    return "Error: should be 'print #0 #1 #2'";
                }

                operands.push_back({*qubitIndex});
            }

            return print(std::move(operands));
        } else if (command == "reset") {
            return reset();
        } else if (command == "help") {
            return help();
        } else if (command == "l" || command == "list") {
            return list();
        } else {
            auto const& gateName = command;

            auto it = operationsMap.find(std::string(gateName));
            if (it == operationsMap.end()) {
                return std::string("Unknown operation '") + std::string(gateName) + "'";
            }
            
            auto operation = it->second(words);

            if (std::holds_alternative<std::string>(operation)) {
                return std::get<std::string>(operation);
            }
            state(std::get<CircuitInstruction>(operation));
            return "";
        }
    }

private:
    using Words = std::vector<std::string_view>;
    using MatrixGen = std::function<std::variant<CircuitInstruction, std::string>(std::vector<std::string_view> const&)>;
    using OperationsMap = std::unordered_map<std::string, MatrixGen>;

    template <typename T>
    static std::string getSyntaxString() {
        if constexpr (std::is_same_v<std::int64_t, T>) {
            return "42 ";
        }

        if constexpr (std::is_same_v<double, T>) {
            return "0.12345 ";
        }
        
        throw std::runtime_error("No syntax for this type");
    }

    template <typename Callable>
    static void addGate(OperationsMap &map, std::string &&name, std::uint64_t numQubits, Callable callable) {
        addGate(map, std::move(name), numQubits, std::function{callable});
    }

    template <typename T, typename ...Args>
    static void addGate(OperationsMap &map, std::string &&name, std::uint64_t numQubits, std::function<T(Args...)> f) {
        static_assert(std::is_same_v<T, Matrix> || std::is_same_v<T, KrausOperators>);

        std::stringstream syntax;
        syntax << "Syntax: " << name << " ";
        for (std::uint64_t i = 0; i < numQubits; ++i) {
            syntax << "#" << i << " ";
        }
        (void) (syntax << ... << getSyntaxString<Args>());
        
        MatrixGen doThisGate = [numQubits, syntax = syntax.str(), f](Words const& args) -> std::variant<CircuitInstruction, std::string> {
            if (args.size() != numQubits + sizeof...(Args) + 1) {
                return syntax;
            }

            try {
                std::uint64_t i = 0;
                CircuitInstruction::QubitIndexVector qubitOperands;
                for (std::uint64_t i = 1; i <= numQubits; ++i) {
                    qubitOperands.push_back(QubitIndex{getQubit(args[i]).value()});
                }

                auto result = [&] {
                    if constexpr (sizeof...(Args) > 0) {
                        return f((get<Args>(args[args.size() - (i++) - 1]).value(), ...));
                    } else {
                        return f();
                    }
                 }();

                if constexpr (std::is_same_v<T, Matrix>) {
                    assert(numQubits == static_cast<std::uint64_t>(std::countr_zero(result.getNumberOfRows())));
                    return CircuitInstruction(KrausOperators{result}, qubitOperands);
                } else {
                    assert(numQubits == static_cast<std::uint64_t>(std::countr_zero(result[0].getNumberOfRows())));
                    return CircuitInstruction(result, qubitOperands);
                }
            } catch (std::bad_optional_access const&) {
                return syntax;
            }
        };

        map[name] = doThisGate;
    }
    
    static void addGate(OperationsMap &map, std::string &&name, KrausOperators const& ks) {
        assert(ks.size() > 0);
        assert(std::has_single_bit(ks[0].getNumberOfRows()));

        addGate(map, std::move(name), std::countr_zero(ks[0].getNumberOfRows()), [ks]() { return ks; });
    }

    static void addGate(OperationsMap &map, std::string &&name, Matrix m) {
        addGate(map, std::move(name), KrausOperators{m});
    }

    static OperationsMap createOperationsMap() {
        namespace ops = default_operations;

        OperationsMap result;

        addGate(result, "x", ops::X);
        addGate(result, "id", ops::IDENTITY);
        addGate(result, "x", ops::X);
        addGate(result, "x90", ops::X90);
        addGate(result, "mx90", ops::MX90);
        addGate(result, "y", ops::Y);
        addGate(result, "y90", ops::Y90);
        addGate(result, "my90", ops::MY90);
        addGate(result, "z", ops::Z);
        addGate(result, "z90", ops::Z90);
        addGate(result, "mz90", ops::MZ90);
        addGate(result, "s", ops::S);
        addGate(result, "sdag", ops::SDAG);
        addGate(result, "t", ops::T);
        addGate(result, "tdag", ops::TDAG);
        addGate(result, "h", ops::H);
        addGate(result, "measure", ops::MEAS_Z);
        addGate(result, "depolarizing_channel", 1, &ops::DEPOLARIZING_CHANNEL);
        addGate(result, "phase_damping", 1, &ops::PHASE_DAMPING);
        addGate(result, "amplitude_damping", 1, &ops::AMPLITUDE_DAMPING);
        addGate(result, "rx", 1, ops::RX);
        addGate(result, "ry", 1, ops::RY);
        addGate(result, "rz", 1, ops::RZ);
        addGate(result, "cnot", ops::CNOT);
        addGate(result, "swap", ops::SWAP);
        addGate(result, "cz", ops::CZ);
        addGate(result, "crk", 2, ops::CRk);

        return result;
    }

    Words getWords(std::string_view input) {
        Words result;

        std::uint64_t pos = 0;
        while (true) {
            while (pos < input.size() && input[pos] == ' ') { ++pos; }
            if (pos >= input.size()) {
                break;
            }

            auto newPos = input.find(' ', pos);
            assert(newPos > pos);

            result.push_back(input.substr(pos, newPos - pos));

            pos = newPos;
        }

        return result;
    }

    template <typename T>
    static std::optional<T> get(std::string_view s) {
        if constexpr (std::is_same_v<T, double>) { // std::from_chars doesn't work with double and emscripten.
            try {
                double value = std::stod(std::string(s));
                return value;
            } catch (std::exception const& e) {
                return std::nullopt;
            }
        } else {
            T arg;
            auto parseResult = std::from_chars(s.data(), s.data() + s.size(), arg);
            if (parseResult.ptr != s.data() + s.size() || parseResult.ec == std::errc::invalid_argument || parseResult.ec == std::errc::result_out_of_range) {
                return std::nullopt;
            }
            return arg;
        }
    }

    static std::optional<QubitIndex> getQubit(std::string_view s) {
        if (s[0] != '#') {
            return std::nullopt;
        }

        auto qubitIndex = get<std::uint64_t>(s.substr(1, std::string_view::npos));

        if (!qubitIndex) {
            return std::nullopt;
        }

        return QubitIndex{*qubitIndex};
    }

    std::string print(std::vector<QubitIndex> &&operands) {
        if (operands.empty()) {
            return "No qubit";
        }

        std::vector<bool> mask;
        for (auto op: operands) {
            if (op.value > 128) {
                return "Wrong qubit index";
            }

            mask.resize(std::max(static_cast<std::uint64_t>(mask.size()), op.value + 1), false);
            mask[op.value] = true;
        }
        
        std::stringstream s;

        s << "Reduced density matrix for qubits ";
        for (auto op: operands) {
            s << op.value << " ";
        }

        s << state.getReducedDensityMatrix(mask);

        return s.str();
    }

    std::string list() const {
        std::stringstream s;
        s << "Available quantum operations (call gate without arguments for further help):" << std::endl;
        bool first = true;
        for (auto const& kv: operationsMap) {
            if (!first) {
                s << ", ";
            } else {
                first = false;
            }
            auto const& gateName = kv.first;
            s << gateName;
        }
        return s.str();
    }

    std::string help() const {
        std::stringstream s;
        s << "help                    show this help" << std::endl;
        s << "p[rint] #1 #2 #3        print state for qubits #1, #2 and #3" << std::endl;
        s << "reset                   reset the quantum state" << std::endl;
        s << "h #0                    apply Hadamard quantum gate on qubit #0" << std::endl;
        s << "l[ist]                  list available quantum gates";
        return s.str();
    };

    std::string reset() {
        state.reset();
        return "State is back to |00...0>";
    }

    MixedState state;
    OperationsMap const operationsMap = createOperationsMap();
    std::stack<CircuitInstruction> executedInstructions;
};

}
}

#ifdef SUPERPOSITEUR_WASM
EMSCRIPTEN_BINDINGS(superpositeur_cli_session) {
  emscripten::class_<superpositeur::cli::SuperpositeurCLISession>("SuperpositeurCLISession")
    .constructor<>()
    .function("input", &superpositeur::cli::SuperpositeurCLISession::operator())
    ;
}
#endif
