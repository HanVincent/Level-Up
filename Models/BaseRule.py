class BaseRule:

    def __init__(self):
        self.level_mapping = {"_": 0, "A1": 1, "A2": 2,
                              "B1": 3, "B2": 4, "C1": 5, "C2": 6}
        self.reverse_level_mapping = ["_", "A1", "A2", "B1", "B2", "C1", "C2"]
        self.pos_mapping = {'ADJECTIVES': ['JJ', 'JJR', 'JJS'],
                            'ADVERBS': ['RB', 'RBR', 'RBS']}

    def get_higher_levels(self, level):
        index = self.level_mapping[level]
        return self.reverse_level_mapping[index+1:]
