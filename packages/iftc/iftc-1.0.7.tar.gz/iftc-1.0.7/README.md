# IFT Correction

IFT Correction(Informal Text Correction) is a library of spelling correction for Vietnamese informal text type(informal text is the type of text as daily communication messages)

## Installation

```
pip install iftc
```

## Example Usage

### Only spelling correction for acronyms

```python
from iftc.spelling_corrector import acronym_correction

corrected_text = acronym_correction('b ơi, món này giá bn thế')
print(corrected_text)
```

This should print:

```console
'bạn ơi, món này giá bao nhiêu thế'
```

### Spelling correction for acronyms and telex

```python
from iftc.spelling_corrector import telex_correction

corrected_text = telex_correction('b ơi, mons nayd giá bn thế')
print('corrected text: {0}'.format(corrected_text))
```

This should print:

```console
'bạn ơi món này giá bao nhiêu thế'
```