import streamlit as st
from datetime import datetime
import hashlib  # Dùng để giả lập thuật toán blockchain
import pandas as pd

def generate_block_hash(data_string):
    "Sử dụng hash SHA-256 để xác thực khối dữ liệu"
    return hashlib.sha256(data_string.encode()).hexdigest()[:16]

def add_to_history(diagnosis, confidence):
    """Hàm lưu dữ liệu vào cấu trúc blockchain và đồng bộ Google Sheets"""
    conf_value = float(confidence.replace('%', '')) if isinstance(confidence, str) else confidence
    
    if conf_value < 90:
        diagnosis = "Không nhận diện được"
        confidence = f"{conf_value}%"
        status_to_save = "Không xác định"
    else:
        status_to_save = diagnosis

    if 'history' not in st.session_state:
        st.session_state['history'] = []
    
    timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    prev_hash = st.session_state['history'][-1]['hash'] if st.session_state['history'] else "0000000000000000"
    
    block_content = f"{timestamp}-{diagnosis}-{confidence}-{prev_hash}"
    current_hash = generate_block_hash(block_content)
    
    new_block = {
        "date": timestamp,
        "diagnosis": diagnosis,
        "confidence": confidence,
        "status": "xác nhận" if conf_value >= 90 else "từ chối",
        "hash": current_hash,
        "prev_hash": prev_hash
    }
    st.session_state['history'].append(new_block)

    # Ghi vào Google Sheets qua database.py
    try:
        from database import save_farming_history
        farm_id = st.session_state.get('farm_id', 'N/A')
        # Lưu vào log Sheets
        save_farming_history(farm_id, f"Quét AI: {diagnosis} ({confidence})")
    except:
        pass
    # --------------------------------------------------------

def show_passport():
    # 1. Lấy thông tin cơ bản
    user_name = st.session_state.get('user_name', 'N/A')
    farm_id = st.session_state.get('farm_id', 'N/A')
    province = st.session_state.get('province', 'N/A')
    
    # 2. Lấy danh sách lịch sử
    history = st.session_state.get('history', [])
    
    # 3. Tạo chuỗi dữ liệu lịch sử rút gọn để nhúng vào QR
    history_str = ""
    if history:
        recent_history = history[-5:]
        history_items = [f"{item['diagnosis'].upper()}({item['date'][:5]})" for item in recent_history]
        history_str = " -LOG:" + "|".join(history_items)
    else:
        history_str = " -LOG:Clean"

    # 4. Tạo Data cho QR Code
    qr_data = f"OWNER:{user_name} -FARM:{farm_id} -LOC:{province}{history_str}"
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

    st.markdown("")
    st.markdown("""
    > **Ghi chú cửa khẩu:** Mã QR phía trên chứa định danh chủ vườn và chuỗi mã hóa lịch sử dịch bệnh. 
    > Khi cán bộ kiểm định quét mã, hệ thống sẽ tự động đối chiếu dữ liệu này với sổ để xác nhận nông sản đủ điều kiện xuất khẩu.
    """)
    
    if history:
        st.write("### 📜 Chi tiết lịch sử ghi nhận")
        st.table(history)
