import streamlit as st
import tempfile

from core.analyzer import analyze_image
from core.qa import answer_question
from utils.formatter import format_product_output

st.title("🧠 AI Product Assistant")

mode = st.radio(
    "Choose Input",
    ["Upload Image", "Camera", "Product Link"]
)

image_path = None

# -------------------------
# Upload Image
# -------------------------
if mode == "Upload Image":
    uploaded = st.file_uploader("Upload image", type=["jpg", "png"])

    if uploaded:
        st.image(uploaded)
        tfile = tempfile.NamedTemporaryFile(delete=False)
        tfile.write(uploaded.read())
        image_path = tfile.name


# -------------------------
# Camera Input
# -------------------------
elif mode == "Camera":
    photo = st.camera_input("Capture")

    if photo:
        st.image(photo)
        tfile = tempfile.NamedTemporaryFile(delete=False)
        tfile.write(photo.getvalue())
        image_path = tfile.name


# -------------------------
# Product Link Input
# -------------------------
elif mode == "Product Link":

    url = st.text_input("Paste product link")

    if url:
        with st.spinner("Fetching product info..."):

            from core.analyzer import analyze_link

            result = analyze_link(url)

            # 🔥 FIX: Safe handling
            if result is None:
                st.error("Failed to fetch product info.")

            elif isinstance(result, dict) and "error" in result:
                st.error(result["error"])

            else:
                st.subheader("📦 Product Information")
                st.write(result)

                st.session_state.product = result
                st.session_state.expl = result.get("explanation", "")


# -------------------------
# Image / Camera Processing
# -------------------------
if image_path:
    with st.spinner("Analyzing image..."):

        result = analyze_image(image_path)

        # 🔥 FIX: Safe handling
        if result is None:
            st.error("Failed to analyze image. Please try again.")

        elif isinstance(result, dict) and "error" in result:
            st.error(result["error"])

        else:
            formatted = format_product_output(result)

            st.subheader("🛍️ Product Details")
            st.text(formatted)

            st.session_state.product = result
            st.session_state.expl = result.get("explanation", "")


# -------------------------
# Q&A Section
# -------------------------
if "product" in st.session_state:

    st.subheader("❓ Ask Questions About the Product")

    q = st.text_input("Your question")

    if q:
        try:
            ans = answer_question(
                st.session_state.product,
                st.session_state.expl,
                q
            )
            st.write(ans)

        except Exception:
            st.error("Failed to generate answer. Please try again.")