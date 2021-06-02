from Models.RawProcessor import RawProcessor

if __name__ == '__main__':
    data_directory = './data'
    
    rawProcessor = RawProcessor(data_directory)
    rawProcessor.calc_ngram_and_count('bnc.parse.txt.gz')