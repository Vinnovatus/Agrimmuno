import streamlit as st
import pandas as pd
import time
from streamlit_gsheets import GSheetsConnection

def save_farming_history(farm_id, activity):
    """Hàm trung gian để lưu dữ liệu mà không gây lỗi sidebar"""
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        # Đọc dữ liệu với ttl=0 để luôn lấy mới nhất
        try:
            history_df = conn.read(worksheet="farming_history", ttl=0)
        except:
            history_df = pd.DataFrame(columns=["farm_id", "timestamp", "activity", "qr_session"])
        
        qr_code = f"AGRI-{farm_id}-{int(time.time())}"
        new_data = pd.DataFrame([{
            "farm_id": farm_id,
            "timestamp": pd.Timestamp.now().strftime("%d/%m/%Y %H:%M"),
            "activity": activity,
            "qr_session": qr_code
        }])
        
        updated_df = pd.concat([history_df, new_data], ignore_index=True)
        conn.update(worksheet="farming_history", data=updated_df)
        return True
    except Exception as e:
        return False
