import streamlit as st
from datetime import datetime
import hashlib  # Dùng để giả lập thuật toán blockchain
import pandas as pd

def generate_block_hash(data_string):
    "Sử dụng hash SHA-256 để xác thực khối dữ liệu"
    return hashlib.sha256(data_string.encode()).hexdigest()[:16]

def add_to_history(diagnosis, confidence):
    """Hàm lưu dữ liệu vào cấu trúc blockchain"""
    if 'history' not in st.session_state:
        st.session_state['history'] = []
    
    timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    
    # Lấy prev_hash (nếu có)
    prev_hash = st.session_state['history'][-1]['hash'] if st.session_state['history'] else "0000000000000000"
    
    # Tạo curr_hash
    block_content = f"{timestamp}-{diagnosis}-{confidence}-{prev_hash}"
    current_hash = generate_block_hash(block_content)
    
    new_block = {
        "date": timestamp,
        "diagnosis": diagnosis,
        "confidence": confidence,
        "status": "xác nhận",
        "hash": current_hash,
        "prev_hash": prev_hash
    }
    st.session_state['history'].append(new_block)

def show_passport():
    # 1. Lấy thông tin cơ bản
    user_name = st.session_state.get('user_name', 'N/A')
    farm_id = st.session_state.get('farm_id', 'N/A')
    province = st.session_state.get('province', 'N/A')
    
    # 2. Lấy danh sách lịch sử (giả sử đã được lưu trong session_state)
    history = st.session_state.get('history', [])
    
    # 3. Tạo chuỗi dữ liệu lịch sử rút gọn để nhúng vào QR
    # Cấu trúc: Tên_Bệnh(Ngày)|Tên_Bệnh(Ngày)
    history_str = ""
    if history:
        # Lấy tối đa 5 bản ghi gần nhất để tránh mã QR quá lớn
        recent_history = history[-5:]
        history_items = [f"{item['diagnosis'].upper()}({item['date'][:5]})" for item in recent_history]
        history_str = " -LOG:" + "|".join(history_items)
    else:
        history_str = " -LOG:Clean"

    # 4. Tạo Data cho QR Code (Kết hợp Profile + Lịch sử)
    qr_data = f"OWNER:{user_name} -FARM:{farm_id} -LOC:{province}{history_str}"
    
    # Tạo URL mã QR (Sử dụng API miễn phí)
    qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data={qr_data}"

    # 5. Giao diện Hộ chiếu số
    st.markdown(f"""
        <div style="background: #82B984; color: #0a0a0a; padding: 25px; border-radius: 20px; border: 2px solid #0a0a0a; font-family: 'Courier New', monospace;">
            <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                <div>
                    <h2 style="color: #0a0a0a; margin:0;">Hộ chiếu số Agrimmuno</h2>
                    <p style="margin:5px 0;"><b>Chủ sở hữu: <b>{user_name.upper()}</b></p>
                    <p style="margin:5px 0;"><b>Nơi trồng: <b>{farm_id.upper()}</b></p>
                    <p style="margin:5px 0;"><b>Khu vực: <b>{province.upper()}</b></p>
                </div>
                <div style="text-align: center; background: white; padding: 10px; border-radius: 10px;">
                    <img src="{qr_url}" width="130">
                    <p style="color: black; font-size: 10px; margin-top: 5px; font-weight: bold;">QUÉT TRUY XUẤT</p>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Đoạn mô tả bạn muốn
    st.markdown("")
    st.markdown("""
    > **Ghi chú cửa khẩu:** Mã QR phía trên chứa định danh chủ vườn và chuỗi mã hóa lịch sử dịch bệnh. 
    > Khi cán bộ kiểm định quét mã, hệ thống sẽ tự động đối chiếu dữ liệu này với sổ để xác nhận nông sản đủ điều kiện xuất khẩu.
    """)
    
    # Hiển thị bảng lịch sử chi tiết bên dưới cho người dùng xem
    if history:
        st.write("### 📜 Chi tiết lịch sử ghi nhận")
        st.table(history)