from generators_v2.bingo_generator_2 import *
import json
import math
import random
from pydantic import TypeAdapter

class CCommV1(BingoGeneratorV2):
    def validate_custom_json(self, custom_json : str, size : int = 5) -> CcommV1Generator | None:
        """Check if the custom_json (as raw string) is a valid generator json
        Return the structured generator object as get_card will expect it, or None for an invalid generator"""
        adapter = TypeAdapter(CcommV1Generator)
        generator: CcommV1Generator
        try:
            generator = adapter.validate_json(custom_json)
        except Exception:
            return None

        # TODO: validate generator tier count, etc.
        return generator

    def generate(self, 
                   seed : int, 
                   generator_json : CcommV1Generator, 
                   size : int) -> GeneratorOutput:
        """Generate a card of the given size, from the given seed, from the given generator.
        Subclasses should override this method, NOT get_card().
        Error cases can call back to _backup_generate()"""

        self.rand = random.Random(seed)

        if len(generator_json) != size * size:
            generator_json = self.rebalance_tiers(generator_json, size)

        self.init_difficulty(size)

        bingo_board = [GeneratorOutputSquare(name="", tier=0)] * (size * size)
        for i in range(size * size):
            tier = self.difficulty(size, i)
            bingo_board[i] = GeneratorOutputSquare(name=f"Tier {tier} Objective", tier=tier)

        for i in range(size * size):
            tier = bingo_board[i].tier

            shuffled_goals = self.get_shuffled_goals(tier, generator_json)
            j = 0
            synergy = 9999
            current_obj = None
            min_syn_obj = None
            min_index = 0
            while synergy != 0  and j < len(shuffled_goals):
                current_obj = GeneratorOutputSquare(
                    name=shuffled_goals[j].name,
                    tier=tier,
                    tags=shuffled_goals[j].types)
                bingo_board[i] = current_obj
                obj_synergy = self.check_line_synergy(i, size, bingo_board)
                if min_syn_obj == None or obj_synergy < synergy:
                    min_syn_obj = current_obj
                    synergy = obj_synergy
                    min_index = j
                j += 1
            bingo_board[i] = min_syn_obj

        return bingo_board


    def rebalance_tiers(self, generator : CcommV1Generator, size : int):
        all_objs = [obj for tier in generator for obj in tier]
        count = len(all_objs)
        per_each = math.floor(count / (size * size))
        remainder = count % (size * size)

        obj_iter = 0
        gen : CcommV1Generator = [[] for i in range(size * size)]
        for i in range(size * size):
            for j in range(per_each):
                gen[i].append(all_objs[obj_iter])
                obj_iter += 1
            if i < remainder:
                gen[i].append(all_objs[obj_iter])
                obj_iter += 1
        return gen


    def check_line_synergy(self, square : int, size : int, board : GeneratorOutput) -> int:
        """Iterate the given square's rows and columns to count objectives with synergy"""
        self_tags = board[square].tags
        synergy = 0
        for other_square in self.get_synergy_locations(size, square):
            for tag in self_tags:
                if tag in board[other_square].tags:
                    synergy += 1
        return synergy
 

    def shuffle(self, list : list):
        for i in range(len(list)):
            elt = self.rand.randint(0, i)
            temp = list[i]
            list[i] = list[elt]
            list[elt] = temp

    def get_shuffled_goals(self, tier : int, board : CcommV1Generator):
        tier_copy = board[tier].copy()
        self.shuffle(tier_copy)
        return tier_copy

    def init_difficulty(self, size):
        if size == 5:
            # Taken from legacy ccomm_v1
            self.rt1 = [*range(5)]
            self.shuffle(self.rt1)

            self.rt2 = [*range(5)]
            self.shuffle(self.rt2)

            self.random_seed_x = self.rand.randint(0, 4)
        else:
            self.rand_tiers = [*range(size * size)]
            self.shuffle(self.rand_tiers)

    def difficulty(self, size, tier):
            # This function takes a space on the board between 0 and 24, and returns its difficulty score, also between 0 and 24.
            # For some sizes, these should always form a magic square if seed remains the same
        if size == 5:
            return self.difficulty_5(tier)

        return self.rand_tiers[tier]

    def difficulty_5(self, tier):
        y = tier // 5
        x = (tier + self.random_seed_x) % 5
        index1 = (x + 3 * y) % 5
        index2 = (3 * x + y) % 5

        row = self.rt1[index1]
        col = self.rt2[index2]
        return (5 * row) + col

    def get_synergy_locations(self, size: int, square: int):
        if size == 5:
            return size_5_synergy[square]
        
        row = square % size
        col = square // size
        for i in range(size):
            if i != col:
                yield (i * size) + row
            if i != row:
                yield (col * size) + i

        if row == col:
            for i in range(size):
                if i != row:
                    yield (i * size) + i
        if row == (size - col - 1):
            if i != col:
                yield (i * size) + size - i - 1

size_5_synergy = [
    [1, 2, 3, 4,        5, 10, 15, 20,      6, 12, 18, 24], # square 0
    [0, 2, 3, 4,        6, 11, 16, 21], # square 1
    [0, 1, 3, 4,        7, 12, 17, 22], # square 2
    [0, 1, 2, 4,        8, 13, 18, 23], # square 3
    [0, 1, 2, 3,        9, 14, 19, 24,      8, 12, 16, 20], # square 4
    [6, 7, 8, 9,        0, 10, 15, 20], # square 5
    [5, 7, 8, 9,        1, 11, 16, 21,       0, 12, 18, 24], # square 6
    [5, 6, 8, 9,        2, 12, 17, 22], # square 7
    [5, 6, 7, 9,        3, 13, 18, 23,      4, 12, 16, 20], # square 8
    [5, 6, 7, 8,        4, 14, 19, 24], # square 9
    [11, 12, 13, 14,    0, 5, 15, 20], # square 10
    [10, 12, 13, 14,    1, 6, 16, 21], # square 11
    [10, 11, 13, 14,    2, 7, 17, 22,       0, 6, 18, 24,       4, 8, 16, 20], # square 12
    [10, 11, 12, 14,    3, 8, 18, 23], # square 13
    [10, 11, 12, 13,    4, 9, 19, 24], # square 14
    [16, 17, 18, 19,    0, 5, 10, 20], # square 15
    [15, 17, 18, 19,    1, 6, 11, 21,       4, 8, 12, 20], # square 16
    [15, 16, 18, 19,    2, 7, 12, 22], # square 17
    [15, 16, 17, 19,    3, 8, 13, 23,       0, 6, 12, 24], # square 18
    [15, 16, 17, 18,    4, 9, 14, 24], # square 19
    [21, 22, 23, 24,    0, 5, 10, 15,       4, 8, 12, 16], # square 20
    [20, 22, 23, 24,    1, 6, 11, 16], # square 21
    [20, 21, 23, 24,    2, 7, 12, 17], # square 22
    [20, 21, 22, 24,    3, 8, 13, 18], # square 23
    [20, 21, 22, 23,    4, 9, 14, 19,       0, 6, 12, 18], # square 24
]