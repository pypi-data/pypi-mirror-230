import time
import nltk
import dill as pickle 
from nltk import word_tokenize
from nltk.lm import KneserNeyInterpolated

from iftc import ift_config
from iftc.spell_checker.candidate import Candidate

class Unintentional:
    def __init__(self):
        with open(ift_config.ngram_model_path, 'rb') as fin:
            print('load language model............')
            self.model = pickle.load(fin)
            print('done!!!!!')
        self.gen_candidate = Candidate()

    def select_candidate(self, message):
        try:
            candidate = self.gen_candidate.sentence_candidate(message)
            if len(candidate) == 1:
                return candidate[0]

            tokenized_text = [list(map(str.lower, word_tokenize(sent)))
                                for sent in candidate]
            #n = 2
            sentences = [nltk.bigrams(t,  pad_right=True, pad_left=True, left_pad_symbol="<s>", right_pad_symbol="</s>") for t in tokenized_text]

            print('predict sentence correct.......')
            p = []
            for i,sent in enumerate(sentences):
                #start_time = time.time()
                temp = self.model.perplexity(sent)
                p.append(temp)
                print("PP({0}):{1}".format(candidate[i], temp))
                #print("--- %s seconds ---" % (time.time() - start_time))
            
            sent_corrected = candidate[p.index(min(p))]
            return sent_corrected
        except Exception as e:
            print(e)
            return message
