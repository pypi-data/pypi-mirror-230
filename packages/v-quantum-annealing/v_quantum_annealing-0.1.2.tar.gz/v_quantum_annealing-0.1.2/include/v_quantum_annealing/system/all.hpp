//    Copyright 2023 Jij Inc.

//    Licensed under the Apache License, Version 2.0 (the "License");
//    you may not use this file except in compliance with the License.
//    You may obtain a copy of the License at

//        http://www.apache.org/licenses/LICENSE-2.0

//    Unless required by applicable law or agreed to in writing, software
//    distributed under the License is distributed on an "AS IS" BASIS,
//    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
//    See the License for the specific language governing permissions and
//    limitations under the License.

#pragma once

// disable eigen -Wdeprecated-copy warning
#include "v_quantum_annealing/utility/disable_eigen_warning.hpp"

#include "v_quantum_annealing/system/classical_ising.hpp"
#include "v_quantum_annealing/system/classical_ising_polynomial.hpp"
#include "v_quantum_annealing/system/continuous_time_ising.hpp"
#include "v_quantum_annealing/system/k_local_polynomial.hpp"
#include "v_quantum_annealing/system/transverse_ising.hpp"
#include "v_quantum_annealing/system/binary_polynomial_sa_system.hpp"
#include "v_quantum_annealing/system/ising_polynomial_sa_system.hpp"

#ifdef USE_CUDA
#include "v_quantum_annealing/system/gpu/chimera_gpu_classical.hpp"
#include "v_quantum_annealing/system/gpu/chimera_gpu_transverse.hpp"
#endif
