import copy
from hyperopt import fmin, tpe, hp, STATUS_OK, Trials

from simulate_8bit_multiplier_py.core import Multiplier
from simulate_8bit_multiplier_py.simulate_multiplier import evaluate

HA_NAMES = ["ha_1", "ha_13", "ha_14", "ha_16", "ha_18", "ha_21", "ha_24", "ha_27"]
FA_NAMES = ["fa_2", "fa_15", "fa_20", "fa_31", "fa_33", "fa_35"]
CA_NAMES = [
    "ca_3", "ca_4", "ca_5", "ca_6", "ca_7", "ca_8", "ca_9", "ca_10", "ca_11", "ca_12",
    "ca_17", "ca_19", "ca_22", "ca_23", "ca_25", "ca_26", "ca_28", "ca_29", "ca_30", "ca_32", "ca_34"
]


def reset_mul():
    mul = Multiplier()
    return mul


def objective(params):
    mul = reset_mul()

    idx = 0

    for ha_name in HA_NAMES:
        choice_val = params[idx]
        if choice_val == 1:
            mul.drop_adder_Carry_or_Cout(ha_name, "Cout")
        idx += 1

    for fa_name in FA_NAMES:
        choice_val = params[idx]
        if choice_val == 1:
            mul.drop_adder_Carry_or_Cout(fa_name, "Cout")
        idx += 1

    # 最后处理所有 CA
    for ca_name in CA_NAMES:
        choice_val = params[idx]  # 0,1,2,3
        if choice_val == 1:
            mul.drop_adder_Carry_or_Cout(ca_name, "Cout")
        elif choice_val == 2:
            mul.drop_adder_Carry_or_Cout(ca_name, "Carry")
        elif choice_val == 3:
            mul.drop_adder_Carry_or_Cout(ca_name, "Cout")
            mul.drop_adder_Carry_or_Cout(ca_name, "Carry")
        # else:
        #     mul.convert_mode(ca_name)
        idx += 1

    evaluate_value = evaluate(mul)

    return {
        'loss': -evaluate_value,
        'status': STATUS_OK,
        'evaluate_value': evaluate_value
    }


search_space = []

for ha_name in HA_NAMES:
    search_space.append(
        hp.choice(ha_name, [0])
    )

for fa_name in FA_NAMES:
    search_space.append(
        hp.choice(fa_name, [0])
    )

for ca_name in CA_NAMES:
    search_space.append(
        hp.choice(ca_name, [0, 1, 2, 3])
    )


def run_bayesian_optimization(max_evals=100):
    trials = Trials()
    best = fmin(
        fn=objective,
        space=search_space,
        algo=tpe.suggest,
        max_evals=max_evals,
        trials=trials
    )
    return best, trials


if __name__ == "__main__":
    best_params, all_trials = run_bayesian_optimization(max_evals=60)
    print(best_params)
