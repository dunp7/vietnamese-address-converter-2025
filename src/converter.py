from .parse import extract_ward_district_province
import os
import pandas as pd
from rapidfuzz import fuzz, process
import logging
import streamlit as st

BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # utils/
DATA_DIR = os.path.join(BASE_DIR, '..', 'data')       # ../data/

logger = logging.getLogger(__name__)


@st.cache_data()
def load_mapping_data():
    return pd.read_json(os.path.join(DATA_DIR, 'ward_mappings.json'))

def fuzzy_best_match(input_list, choices, top_k=3, score_cutoff=60):
    """
    Nếu input_list không có trong choices thì fallback fuzzy để tìm top_k match.
    Trả về list tên [match1, match2, ...]
    """
    results = []
    for item in input_list:
        matches = process.extract(
            item, choices, scorer=fuzz.ratio, limit=top_k, score_cutoff=score_cutoff
        )
        results.extend(matches)  


    results = sorted(results, key=lambda x: x[1], reverse=True)[:top_k]

    return ", ".join(set([x[0] for x in results]))


def get_new_address(address, mapping_data ,components=None, top_k=3):
    try:
        if components:
            add_components = components
        else:
            add_components = extract_ward_district_province(address)
        if not add_components:
            return [], None

        # Normalize về lowercase
        provinces = [p.lower() for p in add_components.get("province", [])]
        districts = [d.lower() for d in add_components.get("district", [])]
        wards = [w.lower() for w in add_components.get("ward", [])]

        input_ward = add_components.get("input_ward", "")
        input_district = add_components.get("input_district", "")
        input_province = add_components.get("input_province", "")
        # --- B1: check province ---
        province_df = mapping_data[
            mapping_data['old_province_name'].str.lower().isin(provinces)
        ]
        if province_df.empty:
            nearest_province = fuzzy_best_match(provinces, mapping_data['old_province_name'].str.lower().unique().tolist())
            raise ValueError(f"Không tìm thấy tỉnh/thành nào trong **{input_province}** trong dữ liệu mapping. Có phải tỉnh/ thành bạn mong muốn là **{nearest_province}**")

        # --- B2: check district ---
        district_df = province_df[
            province_df['old_district_name'].str.lower().isin(districts)
        ]
        if district_df.empty:
            nearest_district = fuzzy_best_match(districts, province_df['old_district_name'].str.lower().unique().tolist())
            raise ValueError(f"Không tìm thấy quận/huyện nào trong **{input_district}** thuộc các tỉnh/thành **{input_province}**. Có phải quận/huyện bạn mong muốn là **{nearest_district}**")

        # --- B3: check ward ---
        ward_df = district_df[
            district_df['old_ward_name'].str.lower().isin(wards)
        ]
        if ward_df.empty:
            nearest_ward = fuzzy_best_match(wards, district_df['old_ward_name'].str.lower().unique().tolist())
            raise ValueError(f"Không tìm thấy phường/xã nào trong **{input_ward}** thuộc các quận/huyện **{input_district}**. Có phải phường/xã bạn mong muốn là **{nearest_ward}**")

        # --- Build candidates ---
        candidates = []
        for _, row in ward_df.iterrows():
            new_addr = ""
            if len(add_components['left_over']) > 0:
                new_addr += f"{', '.join(add_components['left_over'])}, "
            new_addr += f"{row['new_ward_name']}, {row['new_province_name']}"

            candidates.append({
                "score": 3,  
                "new_address": new_addr
            })

        return candidates[:top_k], add_components

    except Exception as e:
        logger.error(f"Error in get_new_address: {str(e)}")
        raise



    


