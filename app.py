import streamlit as st
import tempfile
import product_analyzer

st.title("🧠 AI Product Assistant")

mode = st.radio(
    "Choose Input Method",
    ["Upload Image", "Camera Scanner"]
)

image_path = None


# -------------------------
# Upload Image
# -------------------------
if mode == "Upload Image":

    uploaded = st.file_uploader(
        "Upload product image",
        type=["jpg", "jpeg", "png"]
    )

    if uploaded:
        st.image(uploaded, width=300)

        tfile = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
        tfile.write(uploaded.read())
        image_path = tfile.name


# -------------------------
# Camera Scanner
# -------------------------
elif mode == "Camera Scanner":

    st.write("📷 Point the camera at the product and capture it.")

    photo = st.camera_input("Scan Product")

    if photo:

        st.image(photo, width=300)

        tfile = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
        tfile.write(photo.getvalue())

        image_path = tfile.name


# -------------------------
# Run AI
# -------------------------
if image_path:

    with st.spinner("Analyzing product..."):

        result = product_analyzer.analyze_image(image_path)

        st.subheader("Detected Product Information")

        st.subheader("Product Name")
        st.write(result["product_name"])

        st.subheader("Category")
        st.write(result["category"])

        st.subheader("Visible Text on Product")
        st.write(result["visible_text"])

        st.subheader("Colors")
        st.write(", ".join(result.get("colors", [])))

        st.subheader("Visible Parts")
        st.write(", ".join(result.get("visible_parts", [])))

        st.subheader("Detection Confidence")
        st.write(result["confidence"])

        st.subheader("Product Explanation")
        st.write(result["explanation"])

        st.subheader("Safety Guidance")

        safety = result.get("safety_guidance", [])

        if isinstance(safety, list):
            for tip in safety:
                st.write("•", tip)
        else:
            st.write(safety)

        st.session_state.product_data = result
        st.session_state.explanation = result["explanation"]


# -------------------------
# Q&A Section
# -------------------------
if "product_data" in st.session_state:

    st.subheader("Ask Questions About the Product")

    question = st.text_input("Your question")

    if question:

        answer = product_analyzer.answer_question(
            st.session_state.product_data,
            st.session_state.explanation,
            question
        )

        st.write(answer)