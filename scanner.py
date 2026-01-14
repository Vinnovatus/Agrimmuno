import streamlit as st
import numpy as np
from PIL import Image
import tensorflow as tf
import requests
import io
from passport import add_to_history

# 1. Mapping tỉnh thành sang API (English)
PROVINCE_MAP = {
    "An Giang": "An Giang", "Bà Rịa - Vũng Tàu": "Vung Tau", "Bắc Giang": "Bac Giang",
    "Bắc Kạn": "Bac Kan", "Bạc Liêu": "Bac Lieu", "Bắc Ninh": "Bac Ninh",
    "Bến Tre": "Ben Tre", "Bình Định": "Qui Nhon", "Bình Dương": "Thu Dau Mot",
    "Bình Phước": "Dong Xoai", "Bình Thuận": "Phan Thiet", "Cà Mau": "Ca Mau",
    "Cần Thơ": "Can Tho", "Cao Bằng": "Cao Bang", "Đà Nẵng": "Da Nang",
    "Đắk Lắk": "Buon Ma Thuot", "Đắk Nông": "Gia Nghia", "Điện Biên": "Dien Bien Phu",
    "Đồng Nai": "Bien Hoa", "Đồng Tháp": "Cao Lanh", "Gia Lai": "Pleiku",
    "Hà Giang": "Ha Giang", "Hà Nam": "Phu Ly", "Hà Nội": "Hanoi",
    "Hà Tĩnh": "Ha Tinh", "Hải Dương": "Hai Duong", "Hải Phòng": "Haiphong",
    "Hậu Giang": "Vi Thanh", "Hòa Bình": "Hoa Binh", "Hưng Yên": "Hung Yen",
    "Khánh Hòa": "Nha Trang", "Kiên Giang": "Rach Gia", "Kon Tum": "Kon Tum",
    "Lai Châu": "Lai Chau", "Lâm Đồng": "Da Lat", "Lạng Sơn": "Lang Son",
    "Lào Cai": "Lao Cai", "Long An": "Tan An", "Nam Định": "Nam Dinh",
    "Nghệ An": "Vinh", "Ninh Bình": "Ninh Binh", "Ninh Thuận": "Phan Rang",
    "Phú Thọ": "Viet Tri", "Phú Yên": "Tuy Hoa", "Quảng Bình": "Dong Hoi",
    "Quảng Nam": "Tam Ky", "Quảng Ngãi": "Quang Ngai", "Quảng Ninh": "Ha Long",
    "Quảng Trị": "Dong Ha", "Sóc Trăng": "Soc Trang", "Sơn La": "Son La",
    "Tây Ninh": "Tay Ninh", "Thái Bình": "Thai Binh", "Thái Nguyên": "Thai Nguyen",
    "Thanh Hóa": "Thanh Hoa", "Thừa Thiên Huế": "Hue", "Tiền Giang": "My Tho",
    "TP. Hồ Chí Minh": "Ho Chi Minh City", "Trà Vinh": "Tra Vinh",
    "Tuyên Quang": "Tuyen Quang", "Vĩnh Long": "Vinh Long", "Vĩnh Phúc": "Vinh Yen",
    "Yên Bái": "Yen Bai"
}

def get_real_weather(display_name):
    api_key = "656318b79fc08c29540d4973f7c4f4b9"
    city_api = PROVINCE_MAP.get(display_name)
    
    # Dữ liệu mặc định nếu API lỗi
    fallback = {"temp": 30, "humidity": 70, "desc": "Mây rải rác (Dự phòng)"}
    
    params = {
        "q": f"{city_api},VN",
        "appid": api_key,
        "units": "metric",
        "lang": "vi"
    }
    
    try:
        url = "https://api.openweathermap.org/data/2.5/weather"
        response = requests.get(url, params=params, timeout=5)
        
        if response.status_code != 200:
            # In lỗi ra Terminal để bạn chẩn đoán
            print(f"❌ Weather API Error {response.status_code}: {response.text}")
            return fallback

        data = response.json()
        return {
            "temp": data['main']['temp'],
            "humidity": data['main']['humidity'],
            "desc": data['weather'][0]['description']
        }
    except Exception as e:
        print(f"❌ Connection Error: {e}")
        return fallback
        

def get_action_logic(class_name, weather):
    h, t = weather['humidity'], weather['temp']
    db = {
    "rice_bacterial_leaf_blight": {
        "title": "Nhóm Chẩn Đoán: Bạc Lá / Cháy Bìa Lá",
        "action": "1. Ngừng bón Đạm (N) ngay lập tức. 2. Thay nước ruộng để giảm mật số vi khuẩn. 3. Phun thuốc đặc trị vi khuẩn (Kasuran, Xanthomix). 4. Kiểm tra độ mặn của nước nếu ở vùng ven biển.",
        "insight": f"Dựa trên Ẩm độ {h}%, hệ thống gợi ý 5 khả năng tương đồng:\n"
                   "• (1) Bạc lá vi khuẩn (vết bệnh gợn sóng)\n"
                   "• (2) Cháy bìa lá sinh lý (do gió/mặn)\n"
                   "• (3) Thiếu hụt Kali (khô từ chóp lá thẳng xuống)\n"
                   "• (4) Ngộ độc phèn nhôm\n"
                   "• (5) Vàng lá chín sớm (giai đoạn trỗ)"
    },
    "rice_brown_spot": {
        "title": "Nhóm Chẩn Đoán: Đốm Nâu / Suy Nhược Rễ",
        "action": "1. Bổ sung ngay Lân và Kali. 2. Bón vôi nếu pH đất thấp. 3. Phun vi lượng Silic và Kẽm để làm dày vách tế bào lá. 4. Kiểm tra rễ xem có bị đen/thối không.",
        "insight": "AI nhận diện dấu hiệu đốm trên lá, có thể thuộc 5 trường hợp:\n"
                   "• (1) Đốm nâu (do đất nghèo mùn)\n"
                   "• (2) Ngộ độc hữu cơ (rễ thối làm lá đốm)\n"
                   "• (3) Thiếu Magie (vàng giữa gân lá)\n"
                   "• (4) Đốm tiêm sầm (vết sọc nâu ngắn)\n"
                   "• (5) Dấu chích hút của côn trùng"
    },
    "coffee_rust": {
        "title": "Nhóm Chẩn Đoán: Nấm Lá Cà Phê",
        "action": "1. Cắt tỉa cành sát đất tạo độ thông thoáng. 2. Phun thuốc gốc Đồng hoặc Anvil mặt dưới lá. 3. Không tưới nước trực tiếp lên tán lá vào chiều tối.",
        "insight": f"Nhiệt độ {t}°C thuận lợi cho nấm. Cần đối chiếu 5 biểu hiện:\n"
                   "• (1) Gỉ sắt (có bột cam mặt dưới lá)\n"
                   "• (2) Nấm hồng (héo cành nhanh)\n"
                   "• (3) Thán thư (đốm vòng đồng tâm)\n"
                   "• (4) Cháy nắng sinh lý\n"
                   "• (5) Rêu bám bề mặt lá (trong mùa mưa)"
    },
    "durian_rust": {
        "title": "Nhóm Chẩn Đoán: Cháy Lá / Vàng Lá Sầu Riêng",
        "action": "1. Kiểm tra thoát nước gốc. 2. Phun thuốc nấm định kỳ trong mùa mưa. 3. Bổ sung Trichoderma bảo vệ rễ. 4. Hạn chế phun phân bón lá quá liều.",
        "insight": "Mã QR ghi nhận dấu hiệu cháy lá. Kiểm tra 5 khả năng:\n"
                   "• (1) Gỉ sắt sầu riêng (rụng lá già)\n"
                   "• (2) Cháy lá chết ngọn (Rhizoctonia)\n"
                   "• (3) Thán thư lá (vết bệnh từ rìa lá)\n"
                   "• (4) Sốc nước (cháy lá sau mưa lớn)\n"
                   "• (5) Thiếu Kali (cháy mép lá đều)"
    },
    "orange_rust": {
        "title": "Nhóm Chẩn Đoán: Suy Yếu Cổ Rễ / Vàng Lá",
        "action": "1. Xới nhẹ đất quanh tán, tưới Ridomil Gold. 2. Tuyệt đối ngừng phân hóa học khi rễ đang thối. 3. Quét vôi gốc cây. 4. Bổ sung hữu cơ hoai mục.",
        "insight": "Vàng lá có thể không chỉ do nấm. Xét 5 khả năng:\n"
                   "• (1) Thối rễ Phytophthora\n"
                   "• (2) Vàng lá gân xanh (HLB - lây do rầy)\n"
                   "• (3) Thiếu hụt Vi lượng (Sắt/Kẽm)\n"
                   "• (4) Ngập úng làm thối rễ non\n"
                   "• (5) Tuyến trùng rễ gây suy kiệt"
    },
    "healthy": {
        "title": "Trạng Thái: Chưa Phát Hiện Bất Thường",
        "action": "1. Duy trì lịch trình bón phân hữu cơ. 2. Kiểm tra bẫy côn trùng. 3. Thăm vườn định kỳ 1 lần/tuần.",
        "insight": "AI xác nhận hình ảnh không có dấu hiệu bệnh điển hình. Lưu ý 5 chỉ số:\n"
                   "• (1) Độ pH đất ổn định\n"
                   "• (2) Mật độ thiên địch\n"
                   "• (3) Màu sắc diệp lục\n"
                   "• (4) Độ tơi xốp của đất\n"
                   "• (5) Tốc độ ra đọt/chồi non"
    }

    }
    res = db.get(class_name, db["healthy"])
    risk = "CAO" if h > 80 else "TRUNG BÌNH"
    return res, risk

def run_scanner():
    st.markdown("### 📸 Máy quét AI & Hỗ trợ cây trồng")
    
    # Tự động đồng bộ tỉnh thành
    VIETNAM_PROVINCES = list(PROVINCE_MAP.keys())

    user_prov = st.session_state.get('province', "Cần Thơ")

    # 3. Tìm index để hiển thị lên Selectbox
    try:
        # Kiểm tra xem user_prov có trong list không trước khi lấy index
        if user_prov in VIETNAM_PROVINCES:
            idx = VIETNAM_PROVINCES.index(user_prov)
        else:
            idx = 12 # Vị trí của Cần Thơ trong list alphabet
    except:
        idx = 0
    
    # 4. Hiển thị Selectbox
    selected_city = st.selectbox("📍 Xác nhận vị trí vườn:", VIETNAM_PROVINCES, index=idx)
    
    weather = get_real_weather(selected_city)

    # Cập nhật lại session_state để đảm bảo các hàm sau (như lấy thời tiết) luôn có key này
    st.session_state['province'] = selected_city
    
    st.info(f"🌤️ **Thời tiết {selected_city}:** {weather['temp']}°C | 💧 {weather['humidity']}% | {weather['desc']}")

    file = st.file_uploader("Chọn ảnh lá cây...", type=["jpg", "png", "jpeg"])
    if file:
        img = Image.open(file).convert("RGB")
        st.image(img, use_container_width=True)
        
        if st.button(" Phân tích! "):
            # Chạy Model TFLite
            interpreter = tf.lite.Interpreter(model_path="model_unquant.tflite")
            interpreter.allocate_tensors()
            input_idx = interpreter.get_input_details()[0]['index']
            output_idx = interpreter.get_output_details()[0]['index']

            img_input = img.resize((224, 224))
            input_data = np.expand_dims(np.asarray(img_input).astype(np.float32) / 127.5 - 1, axis=0)

            interpreter.set_tensor(input_idx, input_data)
            interpreter.invoke()
            preds = interpreter.get_tensor(output_idx)
            
            with open("labels.txt", "r", encoding="utf-8") as f:
                labels = [l.strip().split(' ', 1)[1] for l in f.readlines()]
            
            best_idx = np.argmax(preds)
            conf = preds[0][best_idx]
            conf_display = f"{conf * 100:.1f}%"

            if conf < 0.9:
                # Nếu thấp hơn 90%, ghi nhận là không nhận diện được và xóa kết quả cũ
                st.error("⚠️ Không nhận diện được")
                st.info("Độ tin cậy quá thấp. Vui lòng chụp lại ảnh rõ nét và gần lá cây hơn.")
                if 'result' in st.session_state: 
                    del st.session_state['result']
            else:
                # Nếu từ 50% trở lên mới xử lý in ra phân tích
                label = labels[best_idx]
                info, risk = get_action_logic(label, weather)

                st.session_state['result'] = {"label": info['title'], "conf": conf_display, "risk": risk, "ins": info['insight'], "act": info['action']}


    if 'result' in st.session_state:
        r = st.session_state['result']
        st.success(f"**Kết quả: {r['label']} (Tin cậy: {r['conf']})**")
        st.warning(f"⚠️ **Nguy cơ {r['risk']}:** {r['ins']}")
        st.info(f"💡 **Hành động:** {r['act']}")
        
        if st.button("💾 Lưu vào Hộ chiếu số"):
            add_to_history(r['label'], r['conf'])
            st.balloons()
