import os

WORK_DIR = os.path.dirname(os.path.abspath(__file__))

bi_acronyms_path = os.path.join(WORK_DIR, "data/dictionary/_bi_acronyms.json")
uni_acronyms_path = os.path.join(WORK_DIR, "data/dictionary/_uni_acronyms.json")
knowledge_base_path = os.path.join(WORK_DIR, "data/dictionary/_knowledge_base.json")

vowel_path = os.path.join(WORK_DIR, "data/dictionary/_vowel.json")
vn_syl_path = os.path.join(WORK_DIR, "data/dictionary/_vn_syl.json")

ngram_model_path = os.path.join(WORK_DIR, "data/language_model/voz_2gram_model.pkl")

M_START = '[start]'
M_END = '[end]'