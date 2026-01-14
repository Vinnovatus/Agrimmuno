import streamlit as st
from scanner import run_scanner, PROVINCE_MAP
from passport import show_passport
from market import show_market
from database import save_farming_history
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import time 

# 1. Cấu hình trang & CSS (Giữ nguyên phần này)
st.set_page_config(page_title="Agrimmuno", page_icon="🌿", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Lexend:wght@300;400;600&display=swap');
    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Lexend', sans-serif;
        background-color: #fdf5e6;
    }
    [data-testid="stSidebar"] { background-color: #1b5e20; border-right: 1px solid #2e7d32; }
    [data-testid="stSidebar"] * { color: white !important; }
    [data-testid="stMainView"] div[data-testid="stVerticalBlock"] > div:has(div.stMarkdown) {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        border: 1px solid #e0e0e0;
        margin-bottom: 20px;
    }
    [data-testid="stSidebar"] div[data-testid="stVerticalBlock"] > div {
        background-color: transparent !important;
        box-shadow: none !important;
        border: none !important;
    }
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
    .stTextInput input, .stSelectbox select { border-radius: 10px !important; }
    </style>
    """, unsafe_allow_html=True)

# GOOGLE SHEETS processing
conn = st.connection("gsheets", type=GSheetsConnection)

def sync_user_to_sheets(name, province, farm_id):
    try:
        df = conn.read(ttl="60s")
    except:
        df = pd.DataFrame(columns=["name", "province", "farm_id"])
    
    existing_user = df[df['farm_id'] == farm_id]
    if not existing_user.empty:
        if existing_user.iloc[0]['name'] == name:
            save_farming_history(farm_id, "Đăng nhập hệ thống")
            return True, "Chào mừng quay trở lại!"
        else:
            return False, "Mã vùng trồng này đã được đăng ký bởi chủ vườn khác."
    else:
        new_row = pd.DataFrame([{"name": name, "province": province, "farm_id": farm_id}])
        updated_df = pd.concat([df, new_row], ignore_index=True)
        conn.update(data=updated_df)
        save_farming_history(farm_id, "Kích hoạt tài khoản mới")
        return True, "Kích hoạt mã vùng trồng mới thành công!"

VIETNAM_PROVINCES = list(PROVINCE_MAP.keys())

# 2. Màn hình Welcome
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
            st.markdown("### Thiết lập tài khoản / Đăng nhập")
            name = st.text_input("Họ tên chủ vườn:", placeholder="Ví dụ: Nguyễn Văn A")
            province = st.selectbox("Vị trí nơi trồng:", VIETNAM_PROVINCES, index=12)
            farm_name = st.text_input("Mã vùng trồng:", placeholder="Ví dụ: VN-KTOR-0014")
            submit = st.form_submit_button("Kích hoạt hệ thống")
            if submit:
                if name and farm_name:
                    success, message = sync_user_to_sheets(name, province, farm_name)
                    if success:
                        st.session_state['user_name'] = name
                        st.session_state['province'] = province
                        st.session_state['farm_id'] = farm_name
                        st.success(message)
                        st.rerun()
                    else: st.error(message)
                else: st.error("Vui lòng không để trống thông tin.")
    st.stop()

# 3. Sidebar
with st.sidebar:
    st.image("https://i.im.ge/2026/01/11/G7liEh.agrimmuno-2.png")
    menu = st.radio("MENU TÍNH NĂNG", ["Trang chủ 🏠", "Máy quét AI 📸", "Hộ chiếu số 🛂", "Giá thị trường 💰"])
    if st.button("🔄 Đăng xuất"):
        for key in list(st.session_state.keys()): del st.session_state[key]
        st.rerun()

# 4. Điều hướng menu
if menu == "Trang chủ 🏠":
    st.markdown(f"## Chào mừng trở lại, {st.session_state['user_name']}! 👋")
    
    # --- PHẦN 1: GIỮ NGUYÊN GIAO DIỆN CŨ ---
    col_left, col_right = st.columns(2)
    with col_left:
        st.markdown(f"""
        **Thông tin cơ sở:**
        * **Chủ vườn:** {st.session_state['user_name']}
        * **Khu vực:** {st.session_state['province']}
        * **Mã vùng trồng:** {st.session_state['farm_id']}
        """)

        st.markdown("""
        **Tính năng hệ thống:**
        * **Máy quét AI**: Chẩn đoán bệnh cây trồng bằng AI, kết hợp dữ liệu thời tiết thực tế để đưa ra khuyến cáo tức thời cho người trồng.
        * **Hộ chiếu số**: Hồ sơ định danh lưu trữ toàn bộ lịch sử canh tác và dịch bệnh cây trồng khi đi qua cửa khẩu.
        * **Giá thị trường**: Công cụ theo dõi và phân tích biến động giá nông sản trong 5 ngày gần nhất.
        """)
    with col_right:
        st.image("https://images.unsplash.com/photo-1625246333195-78d9c38ad449?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80", caption="Digital Farming 2026")

    # --- PHẦN 2: THÊM LOG VÀ QR Ở DƯỚI ---
    st.divider()
    col_log, col_qr = st.columns([2, 1])
    
    with col_log:
        st.markdown("### 📋 Nhật ký canh tác gần đây")
        try:
            hist_df = conn.read(worksheet="farming_history", ttl="0s")
            st.cache_data.clear()
            user_hist = hist_df[hist_df['farm_id'] == st.session_state['farm_id']].tail(5)
            if not user_hist.empty:
                st.dataframe(user_hist[['timestamp', 'activity', 'qr_session']], use_container_width=True)
            else:
                st.info("Chưa có lịch sử hoạt động.")
        except:
            st.warning("Vui lòng tạo sheet 'farming_history' để xem nhật ký.")

    with col_qr:
        st.markdown("### QR phiên làm việc")
    
        # Lấy lịch sử bệnh từ session_state để concat vào QR
        history = st.session_state.get('history', [])
        if history:
            # Lấy tên bệnh của lần quét cuối cùng để concat
            last_status = history[-1]['diagnosis']
            qr_tail = f"-STATUS:{last_status}"
        else:
            qr_tail = "-STATUS:Clean"
        
        # QR Code ở trang chủ bây giờ sẽ bao gồm: ID + Tỉnh + Tình trạng bệnh mới nhất
        full_qr_data = f"OWNER:{st.session_state['user_name']}-ID:{st.session_state['farm_id']}{qr_tail}"
        
        current_qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data={full_qr_data}"
        st.image(current_qr_url, caption="Mã QR định danh")

elif menu == "Máy quét AI 📸": run_scanner()
elif menu == "Hộ chiếu số 🛂": show_passport()
elif menu == "Giá thị trường 💰": show_market()

# 5. Chân trang
st.markdown("<center><p style='color: #888; font-size: 0.8em;'>© 2026 Agrimmuno System | SV_STARTUP VIII</p></center>", unsafe_allow_html=True)


