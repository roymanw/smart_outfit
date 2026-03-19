import streamlit as st
import requests
from PIL import Image
import os

# ---------------------- ⚠️ 新手必看：配置区域 ----------------------
# 1. 先去「和风天气」官网注册，免费获取 API Key：https://dev.qweather.com/
# 2. 把下面的文字替换成你拿到的 Key，保留引号
WEATHER_API_KEY = "替换成你的和风天气API Key"  

# 存衣服图片的文件夹名字，不用改
UPLOAD_FOLDER = "clothes"  
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# ---------------------- 核心功能区（不用改） ----------------------
# 功能1：根据城市名获取当前温度和天气
def get_weather(city):
    url = f"https://devapi.qweather.com/v7/weather/now?location={city}&key={WEATHER_API_KEY}"
    data = requests.get(url).json()
    if data["code"] == "200":
        return int(data["now"]["temp"]), data["now"]["text"]
    return None, None

# 功能2：简单的搭配逻辑（后续你可以自己加规则）
def generate_outfit(temp, occasion):
    # 先从你上传的衣服里按类型分类
    tops = [c for c in st.session_state.get("clothes", []) if c["type"] == "上衣"]
    bottoms = [c for c in st.session_state.get("clothes", []) if c["type"] == "裤子"]
    shoes = [c for c in st.session_state.get("clothes", []) if c["type"] == "鞋子"]
    coats = [c for c in st.session_state.get("clothes", []) if c["type"] == "外套"]

    # 根据温度筛选上衣
    if temp > 25:
        # 25℃以上：选短袖、薄款
        tops = [t for t in tops if "短袖" in t["style"] or "薄" in t["style"]]
    elif 15 <= temp <= 25:
        # 15-25℃：选长袖、卫衣
        tops = [t for t in tops if "长袖" in t["style"] or "卫衣" in t["style"]]
    else:
        # 15℃以下：选厚款、外套
        tops = [t for t in tops if "厚" in t["style"]]
        coats = [c for c in coats if "厚" in c["style"] or "羽绒服" in c["style"]]

    # 根据场合筛选下装和鞋子
    if occasion == "工作":
        bottoms = [b for b in bottoms if "西裤" in b["style"] or "休闲裤" in b["style"]]
        shoes = [s for s in shoes if "皮鞋" in s["style"]]
    else:
        bottoms = [b for b in bottoms if "牛仔" in b["style"] or "运动" in b["style"]]
        shoes = [s for s in shoes if "运动" in s["style"] or "帆布" in s["style"]]

    # 返回第一套筛选出来的搭配
    return tops[:1], bottoms[:1], shoes[:1], coats[:1]

# ---------------------- 手机/平板界面区（不用改） ----------------------
st.title("👔 我的智能穿搭助手")

# 侧边栏菜单
menu = st.sidebar.selectbox("选择功能", ["上传衣服", "生成搭配"])

# 页面1：上传衣服
if menu == "上传衣服":
    st.header("📸 上传你的衣物")
    col1, col2 = st.columns(2)
    
    with col1:
        clothes_type = st.selectbox("衣物类型", ["上衣", "裤子", "鞋子", "外套"])
        style = st.text_input("衣物特点（如：短袖、衬衫、牛仔裤、羽绒服）")
    
    with col2:
        uploaded_file = st.file_uploader("选择图片", type=["jpg", "png"])
        if uploaded_file:
            img = Image.open(uploaded_file)
            st.image(img, width=150)
            # 保存衣服信息到临时内存
            if "clothes" not in st.session_state:
                st.session_state.clothes = []
            st.session_state.clothes.append({
                "type": clothes_type, 
                "style": style, 
                "image": os.path.join(UPLOAD_FOLDER, uploaded_file.name)
            })
            # 保存图片到文件夹
            with open(os.path.join(UPLOAD_FOLDER, uploaded_file.name), "wb") as f:
                f.write(uploaded_file.getbuffer())
            st.success("✅ 上传成功！可以继续上传下一件")

# 页面2：生成搭配
else:
    st.header("✨ 为你推荐搭配")
    city = st.text_input("输入你的城市（如：北京、上海、广州）")
    occasion = st.selectbox("今天的场合", ["休闲", "工作"])
    
    if st.button("生成搭配"):
        temp, weather = get_weather(city)
        if temp:
            st.write(f"🌤️ 当前天气：{weather}，{temp}℃")
            tops, bottoms, shoes, coats = generate_outfit(temp, occasion)
            
            # 展示搭配
            if tops and bottoms and shoes:
                st.subheader("推荐搭配：")
                # 根据衣服数量动态调整列数
                cols = st.columns(4 if coats else 3)
                
                with cols[0]:
                    st.image(Image.open(tops[0]["image"]), caption="上衣")
                with cols[1]:
                    st.image(Image.open(bottoms[0]["image"]), caption="裤子")
                with cols[2]:
                    st.image(Image.open(shoes[0]["image"]), caption="鞋子")
                if coats:
                    with cols[3]:
                        st.image(Image.open(coats[0]["image"]), caption="外套")
            else:
                st.warning("😅 衣服不够穿啦！先去「上传衣服」页面多传几件吧")
        else:
            st.error("❌ 城市名输错啦，或者API Key没换对，检查一下吧")