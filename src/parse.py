import re
import unicodedata
import logging

logger = logging.getLogger(__name__)

# preprocess

ward_abbr_map = {
    'p': 'phường',
    'x': 'xã',
    'tt': 'thị trấn'
}

district_abbr_map = {
    'q': 'quận',
    'h': 'huyện',
    'tp': 'thành phố',
    'tx': 'thị xã'
}

province_abbr_map = {
    'tp': 'thành phố',
    't': 'tỉnh'
}
direct_cities = ['hà nội', 'hồ chí minh', 'đà nẵng', 'hải phòng', 'cần thơ', 'huế']

def normalize_unicode(text: str) -> str:
    return unicodedata.normalize("NFC", text)


def expand_prefix(text, is_ward=False, is_district=False, is_province=False):
    """
    Chuẩn hóa tiền tố cho ward/district/province:
    - Nếu có prefix hợp lệ → giữ nguyên
    - Nếu có viết tắt → mở rộng
    - Nếu không có prefix → thêm tất cả default hợp lệ
    Trả về list các khả năng (toàn bộ lowercase)
    """
    global ward_abbr_map, district_abbr_map, province_abbr_map, direct_cities
    if not text:
        return []

    text = text.strip().lower()
    words = text.split()

    if is_ward:
        valid_prefixes = ['phường', 'xã', 'thị trấn']
        abbr_map = ward_abbr_map
        defaults = ['phường', 'xã', 'thị trấn']
    elif is_district:
        valid_prefixes = ['quận', 'huyện', 'thành phố', 'thị xã']
        abbr_map = district_abbr_map
        defaults = ['quận', 'huyện', 'thành phố', 'thị xã']
    elif is_province:
        # Province: check 6 thành phố trực thuộc trung ương
        if any(city in text for city in direct_cities):
            if text.startswith('thành phố'):
                return [text]
            return [f"thành phố {text}"]

        valid_prefixes = ['thành phố', 'tỉnh']
        abbr_map = province_abbr_map
        defaults = ['tỉnh', 'thành phố']
    else:
        return [text]

    # Nếu đã có prefix hợp lệ → chỉ trả về chính nó
    if any(text.startswith(p) for p in valid_prefixes):
        return [text]

    # Nếu có viết tắt → mở rộng
    first_word_lower = words[0]
    if first_word_lower in abbr_map:
        return [f"{abbr_map[first_word_lower]} {' '.join(words[1:])}"]

    # Không có prefix → trả về tất cả default hợp lệ
    return [f"{d} {text}" for d in defaults]

def extract_ward_district_province(address: str, ):

    # Normalize
    address = normalize_unicode(address)

    address = re.sub(r'[^\w\s,]', ' ', address)  # Remove special chars
    address = re.sub(r'\s+', ' ', address).strip()  # Normalize spaces
    
    # Split by comma (,)
    parts = [p.strip() for p in address.split(",")]
    
    # Remove country if exists
    if parts[-1].lower() in ["vietnam", "viet nam", "việt nam"]:
        parts = parts[:-1]

    
    # take attributes
    if len(parts) >= 3:
        left_over ,ward, district, province = parts[:-3], parts[-3], parts[-2], parts[-1]


        return {
            'left_over':left_over,
            'ward': expand_prefix(ward, is_ward=True),
            'district': expand_prefix(district, is_district=True),
            'province': expand_prefix(province, is_province=True),
            'input_ward': ward,
            'input_district': district,
            'input_province': province
        }
    else:
        raise Exception("Không đủ thông tin địa chỉ 3 cấp")
