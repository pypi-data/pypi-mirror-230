from typing import List, Optional


class DwaveSamplerParameterModel:
    def __init__(
        self,
        num_reads: Optional[int] = 1,
        chain_strength: Optional[int] | None = None,
        anneal_offsets: Optional[List[float]] | None = None,
        anneal_schedule: Optional[List[List[float]]] | None = None,
        annealing_time: Optional[float] | None = None,
        auto_scale: Optional[bool] | None = None,
        flux_biases: Optional[List[float]] | None = None,
        flux_drift_compensation: Optional[bool] | None = None,
        h_gain_schedule: Optional[List[List[float]]] | None = None,
        initial_state: Optional[dict] | None = None,
        max_answers: Optional[int] | None = None,
        num_spin_reversal_transforms: Optional[int] | None = None,
        programming_thermalization: Optional[float] | None = None,
        readout_thermalization: Optional[float] | None = None,
        reduce_intersample_correlation: Optional[bool] | None = None,
        reinitialize_state: Optional[bool] | None = None,
        time_limit: Optional[float] | None = None,
    ) -> None:
        # See https://docs.dwavesys.com/docs/latest/c_solver_parameters.html
        # for details

        # Number of samples to run
        self.num_reads = num_reads
        # Weight of the links between qubits representig on variable
        self.chain_strength = chain_strength
        # Provides offsets to annealing paths, per qubit
        self.anneal_offsets = anneal_offsets
        # Introduces variations to the global anneal schedule.
        self.anneal_schedule = anneal_schedule
        # Sets the duration, in microseconds with a resolution of 0.01 𝜇𝑠
        # of quantum annealing time, per read
        self.annealing_time = annealing_time
        # Indicates whether ℎ and 𝐽 values are rescaled:
        self.auto_scale = auto_scale
        # List of flux-bias offset values with which to calibrate a chain.
        self.flux_biases = flux_biases
        # Boolean flag indicating whether the D-Wave system compensates for flux drift.
        self.flux_drift_compensation = flux_drift_compensation
        # Sets a time-dependent gain for linear coefficients (qubit biases, see the h parameter) in the Hamiltonian.
        self.h_gain_schedule = h_gain_schedule
        # Initial state to which the system is set for reverse annealing.
        self.initial_state = initial_state
        # Limits the returned values to the first max_answers of num_reads samples.
        self.max_answers = max_answers
        # Specifies the number of spin-reversal transforms to perform.
        self.num_spin_reversal_transforms = num_spin_reversal_transforms
        # Sets the time, in microseconds with a resolution of 0.01 𝜇𝑠,
        # to wait after programming the QPU for it to cool back to base
        # temperature (i.e., post-programming thermalization time).
        self.programming_thermalization = programming_thermalization
        # Sets the time, in microseconds with a resolution of 0.01 𝜇𝑠,
        # to wait after each state is read from the QPU for it to cool
        # back to base temperature (i.e., post-readout thermalization time).
        self.readout_thermalization = readout_thermalization
        # Reduces sample-to-sample correlations caused by the spin-bath polarization
        # effect by adding a delay between reads.
        self.reduce_intersample_correlation = reduce_intersample_correlation
        # When using the reverse annealing feature, you must supply the initial state
        # to which the system is set; see the initial_state parameter
        self.reinitialize_state = reinitialize_state
        # Specifies the maximum run time, in seconds, the solver is allowed to work on the given problem.
        self.time_limit = time_limit


class JijSAParameterModel:
    def __init__(
        self,
        feed_dict: Optional[dict] | None = None,
        num_search: Optional[int] = 1,
        multipliers: Optional[dict] | None = None,
        beta_min: float | None = None,
        beta_max: float | None = None,
        num_sweeps: int | None = None,
        num_reads: int | None = None,
        initial_state: list | dict | None = None,
        updater: str | None = None,
        sparse: bool | None = None,
        reinitialize_state: bool | None = None,
        seed: int | None = None,
        needs_square_constraints: dict[str, bool] | None = None,
        relax_as_penalties: dict[str, bool] | None = None,
    ) -> None:
        # See https://www.documentation.jijzept.com/docs/jijmodeling/
        # for details

        # Dictionary of coefficients for jm.Problem
        self.feed_dict = feed_dict
        # Number of times algorithm will be run
        self.num_search = num_search
        # Multipliers for any constraints in jm.Problem
        self.multipliers = multipliers
        # inverse temperature. If `None`, this will be set automatically.
        self.beta_min = beta_min
        # inverse temperature. If `None`, this will be set automatically.
        self.beta_max = beta_max
        #  The number of Monte-Carlo steps. If `None`, 1000 will be set.
        self.num_sweeps = num_sweeps
        #  The number of samples. If `None`, 1 will be set.
        self.num_reads = num_reads
        # Initial state. If `None`, this will be set automatically.
        self.initial_state = initial_state
        # Updater algorithm. "single spin flip" or "swendsen wang". If `None`, "single spin flip" will be set.
        self.updater = updater
        # If `True`, only non-zero matrix elements are stored, which will save memory. If `None`, `False` will be set.
        self.sparse = sparse
        # If `True`, reinitialize state for each run. If `None`, `True` will be set.
        self.reinitialize_state = reinitialize_state
        # Seed for Monte Carlo algorithm. If `None`, this will be set automatically.
        self.seed = seed
        # This dictionary object is utilized to determine whether to square the constraint condition while incorporating it into the QUBO/HUBO penalty term. Here, the constraint's name is used as the key. If the value is set to True, the corresponding constraint is squared upon its addition to the QUBO/HUBO penalty term. By default, the value is set to True for linear constraints, and to False for non-linear ones.
        self.needs_square_constraints = needs_square_constraints
        # This dictionary object is designed to regulate the incorporation of constraint conditions into the QUBO/HUBO penalty term, with the constraint's name functioning as the key. If the key's value is True, the respective constraint is added to the QUBO/HUBO penalty term. If the value is False, the constraint is excluded from the penalty term, though it remains subject to evaluation to verify if it meets the constraint conditions. By default, all constraint conditions have this value set to True.
        self.relax_as_penalties = relax_as_penalties


class JijSQAParameterModel:
    def __init__(
        self,
        feed_dict: Optional[dict] | None = None,
        num_search: Optional[int] = 1,
        multipliers: Optional[dict] | None = None,
        beta: float | None = None,
        gamma: float | None = None,
        trotter: int | None = None,
        num_sweeps: int | None = None,
        num_reads: int | None = None,
        sparse: bool | None = None,
        reinitialize_state: bool | None = None,
        seed: int | None = None,
        needs_square_constraints: dict[str, bool] | None = None,
        relax_as_penalties: dict[str, bool] | None = None,
    ) -> None:
        # See https://www.documentation.jijzept.com/docs/jijmodeling/
        # for details

        # Dictionary of coefficients for jm.Problem
        self.feed_dict = feed_dict
        # Number of times algorithm will be run
        self.num_search = num_search
        # Multipliers for any constraints in jm.Problem
        self.multipliers = multipliers
        # inverse temperature. If `None`, this will be set automatically.
        self.beta = beta
        # Strength of transverse field. this will be set automatically.
        self.gamma = gamma
        # The number of Trotter. this will be set automatically.
        self.trotter = trotter
        #  The number of Monte-Carlo steps. If `None`, 1000 will be set.
        self.num_sweeps = num_sweeps
        #  The number of samples. If `None`, 1 will be set.
        self.num_reads = num_reads
        # If `True`, only non-zero matrix elements are stored, which will save memory. If `None`, `False` will be set.
        self.sparse = sparse
        # If `True`, reinitialize state for each run. If `None`, `True` will be set.
        self.reinitialize_state = reinitialize_state
        # Seed for Monte Carlo algorithm. If `None`, this will be set automatically.
        self.seed = seed
        # This dictionary object is utilized to determine whether to square the constraint condition while incorporating it into the QUBO/HUBO penalty term. Here, the constraint's name is used as the key. If the value is set to True, the corresponding constraint is squared upon its addition to the QUBO/HUBO penalty term. By default, the value is set to True for linear constraints, and to False for non-linear ones.
        self.needs_square_constraints = needs_square_constraints
        # This dictionary object is designed to regulate the incorporation of constraint conditions into the QUBO/HUBO penalty term, with the constraint's name functioning as the key. If the key's value is True, the respective constraint is added to the QUBO/HUBO penalty term. If the value is False, the constraint is excluded from the penalty term, though it remains subject to evaluation to verify if it meets the constraint conditions. By default, all constraint conditions have this value set to True.
        self.relax_as_penalties = relax_as_penalties


class JijLeapHybridCQMParameterModel:
    def __init__(
        self,
        feed_dict: Optional[dict] | None = None,
        num_search: Optional[int] = 1,
        time_limit: int | float | None = None,
    ) -> None:
        # See https://www.documentation.jijzept.com/docs/jijmodeling/
        # for details

        # Dictionary of coefficients for jm.Problem
        self.feed_dict = feed_dict
        # Number of times algorithm will be run
        self.num_search = num_search
        # The maximum run time
        self.time_limit = time_limit


class AquilaParameterModel:
    def __init__(
        self,
        unit_disk_radius: float,
        shots: Optional[int] = 100,
    ) -> None:
        # Radius of interactions for specified graph
        self.unit_disk_radius = unit_disk_radius
        # Number of times experiemnt will be run and qubits will be measured
        self.shots = shots


class NECParameterModel:
    def __init__(
        self,
        offset: Optional[float] = 0.0,
        num_reads: Optional[int] | None = None,
        num_results: Optional[int] | None = None,
        num_sweeps: Optional[int] | None = None,
        beta_range: Optional[List[float]] | None = None,
        beta_list: Optional[List[float]] | None = None,
        dense: Optional[bool] | None = None,
        vector_mode: Optional[str] | None = None,
        timeout: Optional[List[List[float]]] | None = None,
        Ve_num: Optional[int] | None = None,
        onehot: Optional[int] | None = None,
        fixed: Optional[list] | Optional[dict] | None = None,
        andzero: Optional[list] | None = None,
        orone: Optional[list] | None = None,
        supplement: Optional[list] | None = None,
        maxone: Optional[list] | None = None,
        minmaxone: Optional[list] | None = None,
        init_spin: Optional[list] | None = None,
        spin_list: Optional[list] | None = None,
    ) -> None:
        # Offset for the normalized weight information stored in the qubo
        self.offset = offset
        # VA sampling rate
        self.num_reads = num_reads
        # Number of VA annealing results
        self.num_results = num_results
        # Number of VA annealing sweeps
        self.num_sweeps = num_sweeps
        # VA beta value [start, end, steps] format
        self.beta_range = beta_range
        # Beta value array for each VA sweep
        self.beta_list = beta_list
        # VA matrix mode
        self.dense = dense
        # Mode during VA annealing
        self.vector_mode = vector_mode
        # Job execution timeout
        self.timeout = timeout
        # Number of VEs used in VA annealing
        self.Ve_num = Ve_num
        # VA onehot constraint parameter
        self.onehot = onehot
        # VA fixed constraint parameter
        self.fixed = fixed
        # VA andzero constraint parameter
        self.andzero = andzero
        # VA orone constraint parameter
        self.orone = orone
        # VA supplement constraint parameter
        self.supplement = supplement
        # VA maxone constraint parameter
        self.maxone = maxone
        # VA minmaxone constraint parameter
        self.minmaxone = minmaxone
        # VA initial spin parameter
        self.init_spin = init_spin
        # VA spin list parameter
        self.spin_list = spin_list


class QuantagoniaParameterModel:
    def __init__(
        self,
        sense: Optional[str] = "MINIMIZE",
    ) -> None:
        # Type of cost function: MINIMIZE or MAXIMIZE
        self.sense = sense


class GurobiParameterModel:
    def __init__(
        self,
        max_seconds: Optional[int] | None = None,
    ) -> None:
        # Maximum runtime for problem
        self.max_seconds = max_seconds

        # TODO: Add more parameters: https://www.gurobi.com/documentation/10.0/refman/parameters.html#sec:Parameters  # noqa


class ToshibaParameterModel:
    def __init__(
        self,
        algo: Optional[str] = "2.0",
        steps: Optional[int] | None = None,
        loops: Optional[int] | None = None,
        timeout: Optional[int] | None = None,
        target: Optional[float] | None = None,
        maxout: Optional[int] | None = None,
        dt: Optional[float] | None = None,
        C: Optional[float] | None = None,
        auto: Optional[bool] | None = None,
    ) -> None:
        # For details: https://learn.microsoft.com/en-us/azure/quantum/provider-toshiba

        # Specifies the type of SQBM+ computation algorithm.
        self.algo = algo
        # Specifies the number of steps in a computation request.
        self.steps = steps
        # Specifies the number of loops in SQBM+ computation.
        self.loops = loops
        # Specifies the maximum computation time (timeout) in seconds.
        self.timeout = timeout
        # Specifies the end condition of a computation request.
        self.target = target
        # Specifies the upper limit of the number of solutions to be outputted.
        self.maxout = maxout
        # Specifies the time per step.
        self.dt = dt
        # Corresponds to the constant ξ0, appearing in the paper by Goto,
        # Tatsumura, & Dixon (2019, p. 2), which is the theoretical basis of SQBM+.
        self.C = C
        # 	Specifies the parameter auto tuning flag.
        self.auto = auto
