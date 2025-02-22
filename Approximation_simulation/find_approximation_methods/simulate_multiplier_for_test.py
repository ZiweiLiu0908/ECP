from random import randint, seed
import numpy as np
from core import Multiplier
from functools import partial
from concurrent.futures import ProcessPoolExecutor
import math
from more_itertools import chunked

seed(42)
np.random.seed(42)

_cached_samples = None
_cached_standard_res = None
_cached_binary_inputs = None


def unsigned_to_binary(a, bit_width=8):
    return [int(bit) for bit in format(a, f"0{bit_width}b")]


def binary_to_unsigned(binary_dict):
    binary_list = [binary_dict[f"y{i}"] for i in range(15, -1, -1)]
    return int("".join(map(str, binary_list)), 2)


def generate_samples(sample_size=2000):
    global _cached_samples
    if _cached_samples is None:
        large_numbers = [(randint(128, 255), randint(128, 255)) for _ in range(sample_size)]
        medium_numbers = [(randint(64, 127), randint(64, 127)) for _ in range(sample_size)]
        small_numbers = [(randint(0, 63), randint(0, 63)) for _ in range(sample_size)]
        corner_case = [2 ** i - 1 for i in range(9)]
        _cached_samples = large_numbers + medium_numbers + small_numbers + [(a, b) for a in corner_case for b in
                                                                            corner_case]
    return _cached_samples


# def generate_all_values():
##     very slow, so we use the sample method
#     global _cached_samples
#     if _cached_samples is None:
#         _cached_samples=[]
#         for a,b in product(range(256),range(256)):
#             _cached_samples.append((a,b))
#     return _cached_samples

def get_standard_res(samples):
    global _cached_standard_res
    if _cached_standard_res is None:
        _cached_standard_res = [a * b for a, b in samples]
    return _cached_standard_res


def get_binary_inputs(samples):
    global _cached_binary_inputs
    if _cached_binary_inputs is None:
        _cached_binary_inputs = [{"a": unsigned_to_binary(a), "b": unsigned_to_binary(b)} for a, b in samples]
    return _cached_binary_inputs


def process_samples_batch(samples, mul):
    results = []
    for sample in samples:
        res = mul.forward(sample)
        results.append(binary_to_unsigned(res))
    return results


def timeit(func):
    def wrapper(*args, **kwargs):
        import time
        start = time.time()
        res = func(*args, **kwargs)
        print(f"Time Elapsed: {time.time() - start:.6f}s")
        return res

    return wrapper


def determine_batch_size(total_samples, num_workers):
    return math.ceil(total_samples / num_workers)


@timeit
def evaluate(mul):
    standard_mul = Multiplier()
    standard_mul_total_step = standard_mul.operation_step()
    mul_total_step = mul.operation_step()

    save_step = (standard_mul_total_step - mul_total_step) / standard_mul_total_step

    # 6000 samples，30 seconds, 5 min for all possible values.
    samples = generate_samples(200)
    standard_res = get_standard_res(samples)
    binary_inputs = get_binary_inputs(samples)

    with ProcessPoolExecutor() as executor:
        num_workers = executor._max_workers
        batch_size = determine_batch_size(len(binary_inputs), num_workers)
        batches = chunked(binary_inputs, batch_size)
        results = sum(executor.map(partial(process_samples_batch, mul=mul), batches), [])

    # Calculate errors
    error_sum = sum(abs(res - std) for res, std in zip(results, standard_res))
    print(f"Save Step Ratio: {save_step:.6f}, Error Sum: {error_sum}")
    return  error_sum /(save_step + 1e-2)


if __name__ == "__main__":
    mul = Multiplier()
    mul.support_drop_type()
    # evaluate_value = evaluate(mul)
    # print(f"Evaluation Value: {evaluate_value}")

    # support direct index drop
    mul.drop_adder_Carry_or_Cout(1, "Cout")
    evaluate_value = evaluate(mul)
    print(f"Evaluation Value: {evaluate_value}")

    # support direct name drop, the drop process is accumulative
    mul.drop_adder_Carry_or_Cout("ha_13", "Cout")
    evaluate_value = evaluate(mul)
    print(f"Evaluation Value: {evaluate_value}")
