import os
import base64
from io import BytesIO
from typing import Optional

import requests
from PIL import Image
import streamlit as st


APP_TITLE = "Deepfake-Proof eKYC System"

# Resolve asset paths relative to this file
_CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
_LOGO_PATH = os.path.join(_CURRENT_DIR, "logo.png")

st.set_page_config(
    page_title=APP_TITLE,
    page_icon=_LOGO_PATH if os.path.exists(_LOGO_PATH) else "🛡️",
    layout="wide",
)

# Custom CSS
st.markdown(
    """
    <style>
      .main-header { text-align:center; color:#1f77b4; font-size:2.2rem; font-weight:700; margin: 0.25rem 0 0.5rem; }
      .subtle { color:#6b7280; }
      .footer { text-align:center; margin-top:2rem; padding:1rem; color:#666; }
    </style>
    """,
    unsafe_allow_html=True,
)

# Sidebar: settings and help
st.sidebar.header("Settings")
_default_backend = os.getenv("BACKEND_URL", "http://localhost:5000").strip()
backend_url = st.sidebar.text_input("Backend URL", value=_default_backend).strip() or _default_backend
use_demo = st.sidebar.checkbox("Demo mode (no backend)", value=False, help="Generate sample results without calling the backend.")

if st.sidebar.button("Reset session"):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

with st.sidebar.expander("How to use", expanded=True):
    st.markdown(
        "- Upload or capture two face images.\n"
        "- Click Authenticate to run verification.\n"
        "- Optionally request an explanation heatmap."
    )

# Session state
if "verification_done" not in st.session_state:
    st.session_state.verification_done = False
if "results" not in st.session_state:
    st.session_state.results = None
if "images" not in st.session_state:
    st.session_state.images = {"img1": None, "img2": None}


def _choose_image(upload_file, camera_file) -> Optional[Image.Image]:
    try:
        if camera_file is not None:
            return Image.open(camera_file)
        if upload_file is not None:
            return Image.open(upload_file)
    except Exception:
        st.error("Unable to read the selected image. Please try a different file.")
    return None


def _img_to_bytes(img: Image.Image) -> BytesIO:
    buf = BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf


# Header with optional centered logo
col_l, col_c, col_r = st.columns([1, 2, 1])
with col_c:
    if os.path.exists(_LOGO_PATH):
        lc1, lc2, lc3 = st.columns([1, 1, 1])
        with lc2:
            st.image(_LOGO_PATH, width=80)
    st.markdown(f"<div class='main-header'>{APP_TITLE}</div>", unsafe_allow_html=True)

st.caption("Deepfake-resistant eKYC using face similarity, liveness, and explainability.")
st.markdown("---")

# Step 1: Inputs
st.subheader("📸 Step 1: Provide Two Face Images")
left, right = st.columns(2)

final_img1: Optional[Image.Image] = None
final_img2: Optional[Image.Image] = None

with left:
    st.markdown("### Face 1: Reference Image (ID Proof)")
    img1_upload = st.file_uploader("Upload Face 1", type=["jpg", "jpeg", "png"], key="upload1")
    img1_cam = st.camera_input("Or Capture Face 1", key="cam1")
    final_img1 = _choose_image(img1_upload, img1_cam)
    if final_img1 is not None:
        st.image(final_img1, caption="Selected Face 1", use_container_width=True)

with right:
    st.markdown("### Face 2: Live Verification (Selfie)")
    img2_upload = st.file_uploader("Upload Face 2", type=["jpg", "jpeg", "png"], key="upload2")
    img2_cam = st.camera_input("Or Capture Face 2", key="cam2")
    final_img2 = _choose_image(img2_upload, img2_cam)
    if final_img2 is not None:
        st.image(final_img2, caption="Selected Face 2", use_container_width=True)

st.markdown("---")

# Step 2: Authenticate
st.subheader("🔐 Step 2: Authenticate")

auth_clicked = st.button("🔍 Authenticate", type="primary", use_container_width=True)
if auth_clicked:
    if final_img1 is None or final_img2 is None:
        st.warning("⚠️ Please provide both images before authentication.")
    else:
        st.session_state.images["img1"] = final_img1
        st.session_state.images["img2"] = final_img2
        with st.spinner("🔄 Authenticating... Please wait"):
            try:
                if use_demo:
                    # Demo results, no backend call
                    st.session_state.results = {
                        "similarity_score": 0.87,
                        "liveness_score": 0.93,
                        "authenticity": "Genuine",
                    }
                    st.session_state.verification_done = True
                else:
                    img1_bytes = _img_to_bytes(final_img1)
                    img2_bytes = _img_to_bytes(final_img2)
                    files = {
                        "image1": ("face1.png", img1_bytes, "image/png"),
                        "image2": ("face2.png", img2_bytes, "image/png"),
                    }
                    response = requests.post(f"{backend_url}/verify", files=files, timeout=45)
                    if response.status_code == 200:
                        st.session_state.results = response.json()
                        st.session_state.verification_done = True
                    else:
                        st.error(f"❌ Backend error: {response.status_code} - {response.text}")
            except requests.exceptions.ConnectionError:
                st.error("❌ Cannot connect to backend. Check the URL in the sidebar.")
            except Exception as e:
                st.error(f"❌ Error during authentication: {str(e)}")
            else:
                if st.session_state.verification_done:
                    st.success("✅ Authentication completed successfully!")

# Step 3: Results
if st.session_state.verification_done and st.session_state.results:
    st.markdown("---")
    st.subheader("📊 Verification Results")

    results = st.session_state.results
    similarity = float(results.get("similarity_score", 0.0) or 0.0)
    liveness = float(results.get("liveness_score", 0.0) or 0.0)
    authenticity = str(results.get("authenticity", "Unknown"))

    m1, m2, m3 = st.columns(3)
    with m1:
        st.metric("Similarity Score", f"{similarity * 100:.2f}%")
        st.progress(max(0.0, min(1.0, similarity)))
    with m2:
        st.metric("Liveness Score", f"{liveness * 100:.2f}%")
        st.progress(max(0.0, min(1.0, liveness)))
    with m3:
        if authenticity.lower() == "genuine":
            st.success("✅ Genuine")
        else:
            st.error(f"🚨 {authenticity}")

    st.markdown("### 📷 Image Comparison")
    ic1, ic2 = st.columns(2)
    with ic1:
        st.image(st.session_state.images["img1"], caption="Face 1 (Reference)", use_container_width=True)
    with ic2:
        st.image(st.session_state.images["img2"], caption="Face 2 (Verification)", use_container_width=True)

    st.markdown("---")
    st.subheader("🧠 Step 3: Explain Decision (Optional)")

    if st.button("🧠 Explain Decision (Grad-CAM)", type="secondary", use_container_width=True):
        with st.spinner("🔄 Generating explanation... This may take a moment"):
            try:
                if use_demo:
                    st.info("Demo mode enabled — explanation heatmaps are not available.")
                else:
                    img1_bytes = _img_to_bytes(st.session_state.images["img1"])
                    img2_bytes = _img_to_bytes(st.session_state.images["img2"])
                    files = {
                        "image1": ("face1.png", img1_bytes, "image/png"),
                        "image2": ("face2.png", img2_bytes, "image/png"),
                    }
                    response = requests.post(f"{backend_url}/explain", files=files, timeout=60)
                    if response.status_code == 200:
                        explain_data = response.json()
                        st.success("✅ Explanation generated successfully!")
                        st.markdown("### 🔍 Grad-CAM Heatmap Visualization")
                        st.info("Red/yellow regions indicate areas the model focused on for decision-making.")

                        gc1, gc2 = st.columns(2)
                        with gc1:
                            if "gradcam1" in explain_data:
                                gradcam1_data = base64.b64decode(explain_data["gradcam1"])
                                gradcam1_img = Image.open(BytesIO(gradcam1_data))
                                st.image(gradcam1_img, caption="Face 1 - Grad-CAM Heatmap", use_container_width=True)
                        with gc2:
                            if "gradcam2" in explain_data:
                                gradcam2_data = base64.b64decode(explain_data["gradcam2"])
                                gradcam2_img = Image.open(BytesIO(gradcam2_data))
                                st.image(gradcam2_img, caption="Face 2 - Grad-CAM Heatmap", use_container_width=True)
                    else:
                        st.error(f"❌ Explanation error: {response.status_code} - {response.text}")
            except requests.exceptions.ConnectionError:
                st.error("❌ Cannot connect to backend for explanation. Check the URL in the sidebar.")
            except Exception as e:
                st.error(f"❌ Error generating explanation: {str(e)}")

# Footer
st.markdown("---")
st.markdown(
    """
    <div class='footer'>
      Made with ❤️ for ZenTej Season 3 @ CAIR IIT Mandi<br>
      <small>Powered by Advanced Deep Learning & Explainable AI</small>
    </div>
    """,
    unsafe_allow_html=True,
)
