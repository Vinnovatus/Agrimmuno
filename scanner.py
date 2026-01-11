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
        "rice_bacterial_leaf_blight": {"title": "Bạc Lá Lúa", "action": "Ngay lập tức ngừng việc bón tất cả các loại phân đạm và phân bón lá có hàm lượng đạm cao. Tiến hành thay nước trong ruộng nếu có thể để loại bỏ vi khuẩn trôi nổi. Phun các loại thuốc đặc trị vi khuẩn như Kasuran, Totan hoặc Xanthomix vào lúc sáng sớm hoặc chiều mát.", "insight": f"Ẩm độ {h}% cao, khuẩn lây nhanh qua nước. Bệnh do vi khuẩn Xanthomonas oryzae gây ra, thường xuất hiện sau các đợt mưa giông hoặc bão. Vết bệnh chạy dọc mép lá từ chóp xuống, có màu vàng trắng, làm lá khô xác và giảm khả năng quang hợp nghiêm trọng"},
        "rice_brown_spot": {"title": "Đốm Nâu Lúa", "action": "Ưu tiên bón bổ sung phân Kali và phân lân để tăng sức đề kháng cho bộ rễ. Sử dụng vôi bột để khử phèn nếu đất bị chua. Có thể kết hợp phun bổ sung phân bón lá vi lượng giàu Silic và kẽm để lá lúa cứng cáp hơn, ngăn chặn nấm xâm nhiễm sâu vào tế bào.", "insight": "Đây là dấu hiệu của việc cây lúa đang bị 'đói' dinh dưỡng hoặc đất bị nhiễm phèn, ngộ độc hữu cơ. Vết bệnh là các chấm nhỏ màu nâu tròn hoặc bầu dục, tâm màu xám nhạt, xuất hiện nhiều trên các chân đất nghèo mùn."},
        "coffee_rust": {"title": "Bệnh Gỉ Sắt Cà Phê", "action": "Thực hiện cắt tỉa các cành bị bệnh nặng và cành sát mặt đất để tạo độ thông thoáng cho vườn, giảm độ ẩm lưu trữ. Sử dụng các loại thuốc chứa gốc đồng hoặc các hoạt chất như Anvil, Tilt Super để phun trực tiếp lên mặt dưới của lá. Sau khi điều trị, cần bón thêm phân hữu cơ để cây phục hồi sức sống.", "insight": f"Nhiệt độ {t}°C ấm áp giúp nấm nảy mầm.Loại bệnh nguy hiểm nhất đối với cây cà phê, do nấm Hemileia vastatrix gây ra. Mặt dưới lá xuất hiện các ổ bột màu cam vàng như gỉ sắt. Bệnh làm rụng lá hàng loạt, cây suy kiệt và có thể gây chết cây nếu không xử lý kịp thời."},
        "durian_rust": {"title": "Bệnh Gỉ Sắt Sầu Riêng", "action": "Kiểm tra hệ thống thoát nước quanh gốc cây, không để nước đọng lâu ngày. Phun thuốc đặc trị nấm bệnh định kỳ, đặc biệt là vào mùa mưa hoặc giai đoạn chuyển mùa. Bổ sung các chế phẩm sinh học như Trichoderma vào gốc để tiêu diệt mầm bệnh trong đất và bảo vệ bộ rễ.", "insight": "Bệnh phát triển mạnh trong điều kiện vườn rậm rạp, độ ẩm không khí cao (trên 85%). Bệnh khiến lá bị cháy khô từ rìa vào, làm cây mất sức, khó đậu quả hoặc rụng quả non do không đủ chất dinh dưỡng từ lá truyền xuống."},
        "orange_rust": {"title": "Bệnh Thối Rễ Cam Quýt", "action": "Xới nhẹ lớp đất mặt quanh tán cây và tưới thuốc đặc trị như Ridomil Gold hoặc Aliette trực tiếp vào vùng rễ. Tuyệt đối không bón phân hóa học trong giai đoạn cây đang bị thối rễ vì sẽ làm rễ bị 'cháy' nặng hơn. Cần quét vôi ở gốc cây để ngăn chặn côn trùng và vi khuẩn xâm nhập qua các vết thương hở.", "insight": "Gây ra bởi nấm Phytophthora kết hợp với vi khuẩn, làm thối đen các rễ cám và lây lan lên phần cổ rễ. Cây có biểu hiện vàng lá gân xanh, lá rụng dần và cành bị khô. Đây là bệnh rất khó điều trị dứt điểm nếu để rễ thối quá 50%."},
        "healthy": {"title": "Cây Khỏe Mạnh", "action": "Cây đang phát triển trong điều kiện sinh thái lý tưởng. Lá có màu xanh đặc trưng, bộ rễ khỏe và không có dấu hiệu xâm nhiễm của vi sinh vật gây hại.", "insight": "Tiếp tục theo dõi lịch trình bón phân định kỳ theo từng giai đoạn sinh trưởng. Thực hiện biện pháp phòng bệnh chủ động bằng cách giữ vườn sạch cỏ dại và kiểm tra mật độ côn trùng định kỳ 1 lần/tuần để đảm bảo cây luôn duy trì trạng thái tốt nhất."}
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
            label = labels[best_idx]
            conf = f"{preds[0][best_idx]*100:.1f}%"

            info, risk = get_action_logic(label, weather)
            st.session_state['result'] = {"label": info['title'], "conf": conf, "risk": risk, "ins": info['insight'], "act": info['action']}

    if 'result' in st.session_state:
        r = st.session_state['result']
        st.success(f"**Kết quả: {r['label']} (Tin cậy: {r['conf']})**")
        st.warning(f"⚠️ **Nguy cơ {r['risk']}:** {r['ins']}")
        st.info(f"💡 **Hành động:** {r['act']}")
        
        if st.button("💾 Lưu vào Hộ chiếu số"):
            add_to_history(r['label'], r['conf'])
            st.balloons()