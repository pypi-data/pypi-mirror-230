from spell_checker.intentional import Intentional
from spell_checker.unintentional import Unintentional
from spell_checker.text_processor import remove_mask

corrector = Intentional()
ittn_corrected = corrector.spelling_correction('b ơi, midnh huỷ hoá đơn va đã chọn tbss và huỷ. giờ vào đâu để xoá được chứng từ bán hàng a?')
ittn_corrected = remove_mask(ittn_corrected)
# x = Unintentional()
# a=x.select_candidate(ittn_corrected)
print(ittn_corrected)
