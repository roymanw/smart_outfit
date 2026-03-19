import streamlit as st
from PIL import Image
import os

# 衣物存储文件夹，无需修改
UPLOAD_FOLDER = "clothes"  
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# ---------------------- 核心搭配逻辑 ----------------------
def generate_outfit(temp, occasion):
    # 从已上传的衣物里按类型分类
    tops = [c for c in st.session_state.get("clothes", []) if c["type"] == "上衣"]
    bottoms = [c for c in st.session_state.get("clothes", []) if c["type"] == "裤子"]
    shoes = [c for c in st.session_state.get("clothes", []) if c["type"] == "鞋子"]
    coats = [c for c in st.session_state.get("clothes", []) if c["type"] == "外套"]

    # 按具体温度筛选衣物
    if temp > 25:
        tops = [t for t in tops if "短袖" in t["style"] or "薄" in t["style"]]
    elif 15 <= temp <= 25:
        tops = [t for t in tops if "长袖" in t["style"] or "卫衣" in t["style"]]
    else:
        tops = [t for t in tops if "厚" in t["style"]]
        coats = [c for c in coats if "厚" in c["style"] or "羽绒服" in c["style"]]

    # 按场合筛选衣物
    if occasion == "工作":
        bottoms = [b for b in bottoms if "西裤" in b["style"] or "休闲裤" in b["style"]]
        shoes = [s for s in shoes if "皮鞋" in s["style"]]
    else:
        bottoms = [b for b in bottoms if "牛仔" in b["style"] or "运动" in b["style"]]
        shoes = [s for s in shoes if "运动" in s["style"] or "帆布" in s["style"]]

    return tops[:1], bottoms[:1], shoes[:1], coats[:1]

# ---------------------- 界面交互区 ----------------------
st.title("👔 我的智能穿搭助手")

# 侧边栏功能菜单
menu = st.sidebar.selectbox("选择功能", ["上传衣服", "生成搭配"])

# 页面1：上传衣物
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
            # 初始化衣物存储列表
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
    # 具体数字温度输入（带合理范围限制）
    temp = st.number_input(
        "输入当前温度（℃）",
        min_value=-20,  # 最低温度限制
        max_value=50,   # 最高温度限制
        value=20,       # 默认温度
        step=1          # 每次调整1℃
    )
    occasion = st.selectbox("今天的场合", ["休闲", "工作"])
    
    if st.button("生成搭配"):
        st.write(f"🌡️ 当前温度：{temp}℃")
        tops, bottoms, shoes, coats = generate_outfit(temp, occasion)
        
        # 展示推荐的搭配
        if tops and bottoms and shoes:
            st.subheader("推荐搭配：")
            # 有外套就显示4列，没有就显示3列
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