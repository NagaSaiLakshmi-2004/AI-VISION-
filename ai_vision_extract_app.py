import streamlit as st
from PIL import Image
import numpy as np
import io
from rembg import remove
import zipfile

# ------------------ Masking Function ------------------
def mask_object(img):
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    input_bytes = buf.getvalue()

    output_bytes = remove(input_bytes)
    masked_img = Image.open(io.BytesIO(output_bytes)).convert("RGBA")

    data = np.array(masked_img)
    alpha_channel = data[..., 3]

    # Transparent -> black
    data[..., :3][alpha_channel == 0] = [0, 0, 0]
    data[..., 3] = 255

    return Image.fromarray(data)

# ------------------ Page Config ------------------
st.set_page_config(
    page_title="🎨 AI Object Extractor",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ------------------ Sidebar ------------------
st.sidebar.header("Customize Dashboard")
bg_color = st.sidebar.color_picker("Dashboard Background", "#E6E6FA")
sidebar_start = st.sidebar.color_picker("Sidebar Gradient Start", "#FFB6C1")
sidebar_end = st.sidebar.color_picker("Sidebar Gradient End", "#87CEFA")

st.sidebar.header("Upload Your Images")
uploaded_files = st.sidebar.file_uploader(
    "Choose image(s) (JPG, PNG)",
    type=["jpg","jpeg","png"],
    accept_multiple_files=True
)

st.sidebar.markdown("""
**Instructions:**
- Upload one or more images.
- Row 1: Original and Masked images side by side.
- Row 2: Overlay slider & overlay image in the middle (same size as above).
- Download each masked image or all as ZIP.
""")

# ------------------ Custom CSS ------------------
st.markdown(f"""
<style>
[data-testid="stAppViewContainer"] {{
    background-color: {bg_color};
}}
h1 {{
    text-align: center;
    color: white;
    font-family: 'Arial', sans-serif;
}}
.css-1d391kg {{
    background: linear-gradient(to bottom, {sidebar_start}, {sidebar_end});
    color: white;
    font-weight: bold;
}}
h2, h3 {{
    color: #4B0082;
}}
.stButton button {{
    background-color: #FF69B4;
    color: white;
    border-radius: 10px;
    height: 40px;
    width: 220px;
    font-size: 16px;
    font-weight: bold;
}}
</style>
""", unsafe_allow_html=True)

# ------------------ Header ------------------
st.markdown(f"""
<div style='text-align: center; padding: 20px; 
            background: linear-gradient(to right, {sidebar_start}, {sidebar_end});
            color: white; border-radius:10px;'>
    <h1>🤖 AI Object Extractor Dashboard</h1>
    <p style='text-align: center; font-size:18px; color:white;'>
    Upload images, extract objects, and download results!</p>
    <hr style='border:2px solid white'>
</div>
""", unsafe_allow_html=True)

# ------------------ Main Processing ------------------
if uploaded_files:
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED) as zip_file:
        for uploaded_file in uploaded_files:
            original_image = Image.open(uploaded_file).convert("RGB")
            masked_image = mask_object(original_image)

            # ---------------- Row 1: Original | Masked ----------------
            col1, col2 = st.columns(2)
            with col1:
                st.subheader(f"🖼 Original: {uploaded_file.name}")
                st.image(original_image, use_column_width=True)
            with col2:
                st.subheader(f"✨ Masked: {uploaded_file.name}")
                st.image(masked_image, use_column_width=True)
                
                # Save masked for download
                buf = io.BytesIO()
                masked_image.save(buf, format="PNG")
                st.download_button(
                    label=f"📥 Download Masked",
                    data=buf.getvalue(),
                    file_name=f"masked_{uploaded_file.name}",
                    mime="image/png"
                )
                zip_file.writestr(f"masked_{uploaded_file.name}", buf.getvalue())

            st.markdown("---")  # separator

            # ---------------- Row 2: Overlay Slider & Image ----------------
            st.subheader(f"🔄 Overlay for: {uploaded_file.name}")
            opacity = st.slider(f"Overlay Opacity", 0.0, 1.0, 0.5, key=f"slider_{uploaded_file.name}")
            overlay = Image.blend(original_image, masked_image.convert("RGB"), alpha=opacity)

            # Center overlay using columns, width same as original/masked images
            col_left, col_center, col_right = st.columns([1, 2, 1])
            with col_center:
                st.image(overlay, use_column_width=True, caption=f"Overlay ({opacity*100:.0f}%)")
    
    # Batch download ZIP
    st.download_button(
        label="📦 Download All Masked Images as ZIP",
        data=zip_buffer.getvalue(),
        file_name="masked_images.zip",
        mime="application/zip"
    )

else:
    st.info("Please upload one or more images to start processing.")
