import streamlit as st
from scanner import run_scanner, PROVINCE_MAP
from passport import show_passport
from market import show_market

# 1. Cấu hình trang & CSS (Phần giúp App trông chuyên nghiệp hơn)
st.set_page_config(page_title="AgriGuard VN", page_icon="🌿", layout="wide")

st.markdown("""
    <style>
    /* Tổng thể font chữ và nền */
    @import url('https://fonts.googleapis.com/css2?family=Lexend:wght@300;400;600&display=swap');
    
    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Lexend', sans-serif;
        background-color: #fdf5e6;
    }
    
    /* Tùy chỉnh Sidebar màu xanh đậm */
    [data-testid="stSidebar"] { background-color: #1b5e20; border-right: 1px solid #2e7d32; }
    [data-testid="stSidebar"] * { color: white !important; }
    
    /* Thiết kế các khung (Card) chứa nội dung */
    [data-testid="stMainView"]div[data-testid="stVerticalBlock"] > div:has(div.stMarkdown) {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        border: 1px solid #e0e0e0;
        margin-bottom: 20px;
    }

    /* Xóa ô trắng thừa trong Sidebar (Khắc phục lỗi lúc trước) */
    [data-testid="stSidebar"] div[data-testid="stVerticalBlock"] > div {
        background-color: transparent !important;
        box-shadow: none !important;
        border: none !important;
    }
            
    /* Nút bấm kiểu Modern Green */
    .stButton>button {
        width: 100%;
        border-radius: 25px;
        background-color: #2E7D32;
        color: white;
        font-weight: 600;
        border: none;
        padding: 0.6rem 1rem;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #1b5e20;
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(46, 125, 50, 0.4);
    }
    
    /* Tùy chỉnh input */
    .stTextInput input, .stSelectbox select {
        border-radius: 10px !important;
    }
    </style>
    """, unsafe_allow_html=True)

# Lấy danh sách tỉnh từ scanner.py
VIETNAM_PROVINCES = list(PROVINCE_MAP.keys())

# 2. Màn hình Welcome (Khởi tạo định danh)
if 'user_name' not in st.session_state:
    st.markdown("<br><br>", unsafe_allow_html=True)
    _, col2, _ = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
            <div style="text-align: center;">
                <img src="https://pub-141831e61e69445289222976a15b6fb3.r2.dev/Image_to_url_V2/agrimmuno-imagetourl.cloud-1768127512323-xlb1if.png" width="150">
                <h1 style='color: #2e7d32; margin-bottom:0;'>Agrimunno</h1>
                <p style='color: #666;'>Hệ thống quản trị nông nghiệp thông minh</p>
            </div>
        """, unsafe_allow_html=True)
        
        with st.form("register_form"):
            st.markdown("### Thiết lập tài khoản")
            name = st.text_input("Họ tên chủ vườn:", placeholder="Ví dụ: Nguyễn Văn A")
            province = st.selectbox("Vị trí nơi trồng:", VIETNAM_PROVINCES, index=12) # Mặc định Cần Thơ
            farm_name = st.text_input("Mã vùng trồng:", placeholder="Ví dụ: VN-KTOR-0014")
            
            submit = st.form_submit_button("Kích hoạt hệ thống")
            if submit:
                if name and farm_name:
                    st.session_state['user_name'] = name
                    st.session_state['province'] = province
                    st.session_state['farm_id'] = farm_name
                    st.rerun()
                else:
                    st.error("Vui lòng không để trống thông tin.")
    st.stop()

# 3. Giao diện chính sau khi đăng nhập thành công
with st.sidebar:
    st.image("https://i.im.ge/2026/01/11/G7liEh.agrimmuno-2.png")
    st.markdown("")
    menu = st.radio("MENU TÍNH NĂNG", ["Trang chủ 🏠", "Máy quét AI 📸", "Hộ chiếu số 🛂", "Giá thị trường 💰"])
    
    st.markdown("")
    st.markdown("")
    st.markdown("")
    st.markdown("")
    st.markdown("")
    st.markdown("")
    st.markdown("")
    st.markdown("")
    st.markdown("")
    st.markdown("")
    if st.button("🔄 Đăng xuất"):
        for key in list(st.session_state.keys()): del st.session_state[key]
        st.rerun()

# 4. Điều hướng menu
if menu == "Trang chủ 🏠":
    st.markdown(f"## Chào mừng trở lại, {st.session_state['user_name']}! 👋")
    col_left, col_right = st.columns(2)
    with col_left:
        st.markdown("")
        st.markdown(f"""
        **Thông tin cơ sở:**
        * **Chủ vườn:** {st.session_state['user_name']}
        * **Khu vực:** {st.session_state['province']}
        * **Mã vùng trồng:** {st.session_state['farm_id']}
        """)

        st.markdown("")
        st.markdown("""
        **Tính năng hệ thống:**
        * **Máy quét AI**: Chẩn đoán bệnh cây trồng bằng AI, kết hợp dữ liệu thời tiết thực tế để đưa ra khuyến cáo tức thời cho người trồng.
        * **Hộ chiếu số**: Hồ sơ định danh lưu trữ toàn bộ lịch sử canh tác và dịch bệnh cây trồng khi đi qua cửa khẩu.
        * **Giá thị trường**: Công cụ theo dõi và phân tích biến động giá nông sản trong 5 ngày gần nhất.
        """)
    with col_right:
        st.markdown("")
        st.image("https://images.unsplash.com/photo-1625246333195-78d9c38ad449?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80", caption="Digital Farming 2026")

elif menu == "Máy quét AI 📸":
    run_scanner()

elif menu == "Hộ chiếu số 🛂":
    show_passport()

elif menu == "Giá thị trường 💰":
    show_market()

# 5. Chân trang
st.markdown("")
st.markdown("<center><p style='color: #888; font-size: 0.8em;'>© 2026 Agrimmuno System | SV_STARTUP VIII</p></center>", unsafe_allow_html=True)