# Level-Up: Learning to Improve Proficiency Level of Essays

### *Accepted in ACL 2019 System Demonstrations*
[ACL link](https://www.aclweb.org/anthology/P19-3033/)

### Abstract
We introduce a method for generating suggestions on a given sentence for improving the proficiency level. In our approach, the sentence is transformed into a sequence of grammatical elements aimed at providing suggestions of more advanced grammar elements based on originals. The method involves parsing the sentence, identifying grammatical elements, and ranking related elements to recommend a higher level of grammatical element. We present a prototype coaching system, Level-Up, that applies the method to English learners’ essays in order to assist them in writing and reading. Evaluation on a set of essays shows that our method does assist user in writing.


### Downloads 

##### Data
* [sims.json](https://drive.google.com/file/d/1E9AqC94V3oiJuHLOBidQavHA0ro37fU0/view?usp=sharing) (226 MB) Top 50 similar words dictionary from trained word2vec model, Google News Word2vec slim version
* [Word2vec slim version](https://drive.google.com/file/d/1PpOf7IrhNNQZLGB-8WTXfXcsJ-irKutq/view?usp=sharing) (163 MB)
* [lm.bin]() (762 MB) (Not released) Trained language model
* [bnc.parse.txt.gz]() (Not released) Parsed BNC corpus, not using all data


### Citation
```
@inproceedings{han-etal-2019-level,
    title = "Level-Up: Learning to Improve Proficiency Level of Essays",
    author = "Han, Wen-Bin  and
      Chen, Jhih-Jie  and
      Yang, Chingyu  and
      Chang, Jason",
    booktitle = "Proceedings of the 57th Annual Meeting of the Association for Computational Linguistics: System Demonstrations",
    month = jul,
    year = "2019",
    address = "Florence, Italy",
    publisher = "Association for Computational Linguistics",
    url = "https://www.aclweb.org/anthology/P19-3033",
    pages = "207--212",
    abstract = "We introduce a method for generating suggestions on a given sentence for improving the proficiency level. In our approach, the sentence is transformed into a sequence of grammatical elements aimed at providing suggestions of more advanced grammar elements based on originals. The method involves parsing the sentence, identifying grammatical elements, and ranking related elements to recommend a higher level of grammatical element. We present a prototype tutoring system, Level-Up, that applies the method to English learners{'} essays in order to assist them in writing and reading. Evaluation on a set of essays shows that our method does assist user in writing.",
}
```
