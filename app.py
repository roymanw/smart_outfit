import streamlit as st
import requests
from PIL import Image
import os

# ---------------------- ⚠️ 必须修改：替换成你自己的和风天气API Key ----------------------
# 注册获取地址：https://dev.qweather.com/ ，注册后创建Web API应用即可拿到免费Key
WEATHER_API_KEY = "替换成你的和风天气API Key"  

# 衣物存储文件夹，不用修改
UPLOAD_FOLDER = "clothes"  
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# ---------------------- 核心功能区（已加容错，不会再红屏） ----------------------
# 功能1：获取天气（加了完整异常处理，彻底解决KeyError）
def get_weather(city):
    try:
        # 和风天气免费接口地址
        url = f"https://devapi.qweather.com/v7/weather/now?location={city}&key={WEATHER_API_KEY}"
        # 发起请求，设置10秒超时避免卡住
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # 先判断返回结果有没有code字段，彻底避免KeyError
        if "code" not in data:
            st.error("❌ 天气接口异常，请检查你的API Key是否正确替换")
            return None, None
        
        # 接口返回成功，返回温度和天气
        if data["code"] == "200":
            return int(data["now"]["temp"]), data["now"]["text"]
        # 接口返回报错，把错误码告诉用户方便排查
        else:
            st.error(f"❌ 天气接口报错，错误码：{data['code']}，请检查API Key是否正确、城市名是否有效")
            return None, None
    
    # 捕获所有异常，不会再红屏
    except Exception as e:
        st.error(f"❌ 请求天气失败：{str(e)}，请检查网络、API Key是否正确")
        return None, None

# 功能2：搭配逻辑（和之前一致，兼容外套）
def generate_outfit(temp, occasion):
    # 从已上传的衣物里分类
    tops = [c for c in st.session_state.get("clothes", []) if c["type"] == "上衣"]
    bottoms = [c for c in st.session_state.get("clothes", []) if c["type"] == "裤子"]
    shoes = [c for c in st.session_state.get("clothes", []) if c["type"] == "鞋子"]
    coats = [c for c in st.session_state.get("clothes", []) if c["type"] == "外套"]

    # 按温度筛选
    if temp > 25:
        tops = [t for t in tops if "短袖" in t["style"] or "薄" in t["style"]]
    elif 15 <= temp <= 25:
        tops = [t for t in tops if "长袖" in t["style"] or "卫衣" in t["style"]]
    else:
        tops = [t for t in tops if "厚" in t["style"]]
        coats = [c for c in coats if "厚" in c["style"] or "羽绒服" in c["style"]]

    # 按场合筛选
    if occasion == "工作":
        bottoms = [b for b in bottoms if "西裤" in b["style"] or "休闲裤" in b["style"]]
        shoes = [s for s in shoes if "皮鞋" in s["style"]]
    else:
        bottoms = [b for b in bottoms if "牛仔" in b["style"] or "运动" in b["style"]]
        shoes = [s for s in shoes if "运动" in s["style"] or "帆布" in s["style"]]

    return tops[:1], bottoms[:1], shoes[:1], coats[:1]

# ---------------------- 界面区（和之前一致） ----------------------
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
            # 初始化衣物列表
            if "clothes" not in st.session_state:
                st.session_state.clothes = []
            # 保存衣物信息
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
    city = st.text_input("输入你的城市（如：北京、上海、广州、深圳）")
    occasion = st.selectbox("今天的场合", ["休闲", "工作"])
    
    if st.button("生成搭配"):
        # 先判断有没有填城市
        if not city:
            st.warning("请先输入你的城市名")
        else:
            temp, weather = get_weather(city)
            # 只有拿到天气数据才生成搭配
            if temp is not None and weather is not None:
                st.write(f"🌤️ 当前天气：{weather}，{temp}℃")
                tops, bottoms, shoes, coats = generate_outfit(temp, occasion)
                
                # 展示搭配
                if tops and bottoms and shoes:
                    st.subheader("推荐搭配：")
                    # 有外套就4列，没有就3列
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
                    st.warning("😅 衣物不够！先去「上传衣服」页面多传几件对应类型的衣物吧")