from generators_v2.bingo_generator_2 import *
from generators_v2.bg2_ccomm_v1 import CCommV1

class SinkoutRoyale(CCommV1):
    def get_card(
                self, 
                _seed : (str | None) = None,
                generator_json : CcommV1Generator | CcommV2Generator | None = None,
                _size : int | str = 5) -> tuple[int, dict[str, any]]:
        if type(_size) is str:
            try:
                size = int(_size)
            except Exception:
                size = 5
        else:
            size = _size
        if size % 2 != 0:
            raise Exception("Cannot generate Sinkout Royale for non-even board size")
        return super().get_card(_seed, generator_json, size)

    def generate(self, 
            seed : int, 
            generator_json : CcommV1Generator, 
            size : int) -> GeneratorOutput:
        half_size = int(size / 2)

        gen1 = generator_json
        board1 = super().generate(seed, gen1, half_size)
        gen2 = self.prune_generator(gen1, board1)
        board2 = super().generate(seed, gen2, half_size)
        gen3 = self.prune_generator(gen2, board2)
        board3 = super().generate(seed, gen3, half_size)
        gen4 = self.prune_generator(gen3, board3)
        board4 = super().generate(seed, gen4, half_size)

        boards = [board1, board2, board3, board4]
        self.shuffle(boards)

        board: list[GeneratorOutputSquare] = []
        for i in range(half_size):
            loc = i * half_size
            board += boards[0][loc:loc+half_size]
            board += boards[1][loc:loc+half_size]
        for i in range(half_size):
            loc = i * half_size
            board += boards[2][loc:loc+half_size]
            board += boards[3][loc:loc+half_size]
        return board

    def prune_generator(self,
                        generator_json: CcommV1Generator,
                        board: GeneratorOutput) -> CcommV1Generator:
        obj_names = [square.name for square in board]
        return [
            [obj for obj in tier if obj.name not in obj_names] for tier in generator_json
        ]