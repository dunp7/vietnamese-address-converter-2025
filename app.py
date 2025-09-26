import streamlit as st
import logging 
from utils.converter import get_new_address, load_mapping_data
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

st.set_page_config(layout="wide", page_title="AI Tools")

mapping_data = load_mapping_data()
# Sidebar - Clear Cache
if st.sidebar.button("🧹 Clear Cache"):
    try:
        st.cache_data.clear()
        st.cache_resource.clear()
        st.sidebar.success("✅ Cache cleared successfully!")
    except Exception as e:
        st.error(f"Failed to clear cache: {e}")

st.title("📍 Address Converter")

st.header("🏠 Chuyển Địa Chỉ Cũ Sang Địa Chỉ Mới")
st.markdown("Nhập địa chỉ cũ bên dưới để nhận địa chỉ mới:")
st.info("ℹ️ **Lưu ý:** Nhập địa chỉ cách nhau bằng dấu phẩy (' ,  '), và nên sắp xếp theo đúng thứ tự: **số nhà/đường, phường, quận, thành phố**")
old_address = st.text_input(
    "Địa chỉ cũ:",
    key="old_address",
)

if st.button("🔄 Chuyển đổi địa chỉ", key="convert_address"):
    if old_address.strip() == "":
        st.warning("Vui lòng nhập địa chỉ cũ trước!")
    else:
        with st.spinner("Đang chuyển đổi địa chỉ..."):
            try:
                result, old_add = get_new_address(old_address, mapping_data, top_k=5)
                st.success(f"✅ Địa chỉ mới chuẩn nhất là: {result[0]['new_address']}")
                # with st.expander("📂 Xem dữ liệu chi tiết"):
                #     st.dataframe(result)
            except Exception as e:
                st.error(f"Không thể chuyển đổi địa chỉ: {e}")


