level_table = {"A1": 1, "A2": 2, "B1": 3, "B2": 4, "C1": 5, "C2": 6}

pos_table = {'ADJECTIVES': ['JJ', 'JJR', 'JJS'],
             'ADVERBS': ['RB', 'RBR', 'RBS']}

with open('data/tag2pos.txt', 'r', encoding='utf8') as fs:
    mappings = fs.read().split('\n')
    tag2pos_table = {row.split('\t')[0]: row.split('\t')[2] for row in mappings}
