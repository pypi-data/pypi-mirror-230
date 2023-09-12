from iftc.spell_checker.intentional import Intentional
from iftc.spell_checker.unintentional import Unintentional
from iftc.spell_checker.text_processor import remove_mask


def acronym_correction(text: str):
    corrector = Intentional()
    corrected_acronym = corrector.spelling_correction(text)

    return remove_mask(corrected_acronym)

def telex_correction(text: str):
    it_corrector = Intentional()
    acronym_corrected = it_corrector.spelling_correction(text)

    uit_corrector = Unintentional()
    sent_corrected   = uit_corrector.select_candidate(acronym_corrected)
    return sent_corrected