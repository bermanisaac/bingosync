from boardgen import *
import os
import time
import multiprocessing
import random
from collections import defaultdict

def get_inline_squares(board: GeneratorOutput, idx: int, size: int):
    row = idx % size

    row_start = idx - row
    row_elts = board[row_start:row_start+size]

    col_elts = board[row::size]

    return row_elts + col_elts

def gen_board(json: str, seed_start: int, count: int, gen_str: str):
    gen = BingoGeneratorLegacyNodejs(json)
    counts : defaultdict[str, int] = defaultdict(int)
    pairwise_counts : defaultdict[(str, str), int] = defaultdict(int)
    pairwise_line_counts : defaultdict[(str, str), int] = defaultdict(int)

    for i in range(count):
        board = gen.generate(seed_start + i)

        for idx, obj in enumerate(board):
            counts[f"{obj.tier}: {obj.name}"] += 1
            for obj2 in board:
                pairwise_counts[(obj.name, obj2.name)] += 1
            for obj2 in get_inline_squares(board, idx, 5):
                pairwise_line_counts[(obj.name, obj2.name)] += 1

    with open(f"brute_forcer_out/{gen_str}_counts_{seed_start}-{seed_start+count - 1}.txt", "w", encoding="utf-8") as file:
        for key, val in counts.items():
            file.write(f"{key}: {val}\n")

    with open(f"brute_forcer_out/{gen_str}_pairwise_counts_{seed_start}-{seed_start+count - 1}.txt", "w", encoding="utf-8") as file:
        for key, val in pairwise_counts.items():
            file.write(f"{key}: {val}\n")

    with open(f"brute_forcer_out/{gen_str}_pairwise_line_counts_{seed_start}-{seed_start+count - 1}.txt", "w", encoding="utf-8") as file:
        for key, val in pairwise_counts.items():
            file.write(f"{key}: {val}\n")


def multi_gen(json: str, thread_count: int, count_per: int, gen_str: str):
    processes : list[multiprocessing.Process] = []
    for i in range(thread_count):
        seed = count_per * i + 1
        process = multiprocessing.Process(target=gen_board, args=(json, seed, count_per, gen_str))
        process.start()
        processes.append(process)


    for process in processes:
        process.join()

def run_boards_with_perf(json: str):
        start_time = time.perf_counter()

        multi_gen(json, thread_count, board_count, gen_str)

        end_time = time.perf_counter()
        execution_time = end_time - start_time

        total_count = board_count * thread_count
        bps = total_count / execution_time

        print(f"Execution time for {total_count} boards: {execution_time:.6f} seconds")
        print(f"{(bps):.6f} boards per second")

gen_str = "3_2_3"
# board_count = 100_00
board_count = 1
thread_count = 1
if __name__ == "__main__":


    gen = BingoGeneratorLegacyNodejs('boardgen/js/celeste_generator.js', debug=True)

    for i in range(10):
        gen.generate(random.randint(0,999999))

    json = 'boardgen/js/celeste_generator.js'
    # run_boards_with_perf(json)