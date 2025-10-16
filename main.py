# import streamlit as st
# import requests
# from PIL import Image
# from io import BytesIO
# import base64
# import os

# # Page configuration
# # Get the directory of the current script
# current_dir = os.path.dirname(os.path.abspath(__file__))
# logo_path = os.path.join(current_dir, "logo.png")

# st.set_page_config(
#     page_title="Deepfake-Proof eKYC System",
#     page_icon=logo_path if os.path.exists(logo_path) else "🛡️",
#     layout="wide"
# )

# # Custom CSS for better styling
# st.markdown("""
#     <style>
#     .main-header {
#         text-align: center;
#         color: #1f77b4;
#         font-size: 2.5rem;
#         font-weight: bold;
#         margin-bottom: 2rem;
#         display: flex;
#         align-items: center;
#         justify-content: center;
#         gap: 1rem;
#     }
#     .header-logo {
#         width: 60px;
#         height: 60px;
#         object-fit: contain;
#     }
#     .footer {
#         text-align: center;
#         margin-top: 3rem;
#         padding: 1rem;
#         color: #666;
#     }
#     </style>
# """, unsafe_allow_html=True)

# # Header with logo
# # Center the logo and title
# col1, col2, col3 = st.columns([2, 3, 2])
# with col2:
#     # Display small logo centered
#     if os.path.exists(logo_path):
#         logo_img = Image.open(logo_path)
#         # Create columns to center the logo
#         logo_col1, logo_col2, logo_col3 = st.columns([1, 1, 1])
#         with logo_col2:
#             st.image(logo_img, width=50)
#     st.markdown("<h2 style='text-align: center; color: #1f77b4; font-size: 2.5rem; font-weight: bold; margin-top: 0.5rem;'>Deepfake-Proof eKYC System</h2>", unsafe_allow_html=True)

# st.markdown("---")

# # Flask Backend URL (modify if your backend is hosted elsewhere)
# FLASK_BACKEND_URL = "http://localhost:5000"

# # Initialize session state for storing results
# if 'verification_done' not in st.session_state:
#     st.session_state.verification_done = False
# if 'results' not in st.session_state:
#     st.session_state.results = None
# if 'images' not in st.session_state:
#     st.session_state.images = {'img1': None, 'img2': None}

# # Helper function to get the final image (prioritize camera over upload)
# def get_final_image(upload_img, cam_img):
#     if cam_img is not None:
#         return Image.open(cam_img)
#     elif upload_img is not None:
#         return Image.open(upload_img)
#     return None

# # Input Section
# st.subheader("📸 Step 1: Provide Two Face Images")
# col1, col2 = st.columns(2)

# with col1:
#     st.markdown("### Face 1: Reference Image (ID Proof)")
#     img1_upload = st.file_uploader("Upload Face 1", type=["jpg", "png", "jpeg"], key="upload1")
#     img1_cam = st.camera_input("Or Capture Face 1", key="cam1")
    
#     final_img1 = get_final_image(img1_upload, img1_cam)
#     if final_img1:
#         st.image(final_img1, caption="Selected Face 1", use_container_width=True)

# with col2:
#     st.markdown("### Face 2: Live Verification (Selfie)")
#     img2_upload = st.file_uploader("Upload Face 2", type=["jpg", "png", "jpeg"], key="upload2")
#     img2_cam = st.camera_input("Or Capture Face 2", key="cam2")
    
#     final_img2 = get_final_image(img2_upload, img2_cam)
#     if final_img2:
#         st.image(final_img2, caption="Selected Face 2", use_container_width=True)

# st.markdown("---")

# # Authentication Button
# st.subheader("🔐 Step 2: Authenticate")

# if st.button("🔍 Authenticate", type="primary", use_container_width=True):
#     # Validate inputs
#     if not final_img1 or not final_img2:
#         st.warning("⚠️ Please provide both images before authentication.")
#     else:
#         # Store images in session state
#         st.session_state.images['img1'] = final_img1
#         st.session_state.images['img2'] = final_img2
        
#         with st.spinner("🔄 Authenticating... Please wait"):
#             try:
#                 # Convert images to bytes for sending to Flask
#                 img1_bytes = BytesIO()
#                 final_img1.save(img1_bytes, format='PNG')
#                 img1_bytes.seek(0)
                
#                 img2_bytes = BytesIO()
#                 final_img2.save(img2_bytes, format='PNG')
#                 img2_bytes.seek(0)
                
#                 # Prepare files for POST request
#                 files = {
#                     'image1': ('face1.png', img1_bytes, 'image/png'),
#                     'image2': ('face2.png', img2_bytes, 'image/png')
#                 }
                
#                 # Send request to Flask backend
#                 response = requests.post(f"{FLASK_BACKEND_URL}/verify", files=files, timeout=30)
                
#                 if response.status_code == 200:
#                     results = response.json()
#                     st.session_state.results = results
#                     st.session_state.verification_done = True
#                     st.success("✅ Authentication completed successfully!")
#                 else:
#                     st.error(f"❌ Backend error: {response.status_code} - {response.text}")
                    
#             except requests.exceptions.ConnectionError:
#                 st.error("❌ Cannot connect to Flask backend. Make sure it's running on http://localhost:5000")
#             except Exception as e:
#                 st.error(f"❌ Error during authentication: {str(e)}")

# # Results Display Section
# if st.session_state.verification_done and st.session_state.results:
#     st.markdown("---")
#     st.subheader("📊 Verification Results")
    
#     results = st.session_state.results
    
#     # Display metrics in columns
#     metric_col1, metric_col2, metric_col3 = st.columns(3)
    
#     with metric_col1:
#         similarity = results.get('similarity_score', 0)
#         st.metric("Similarity Score", f"{similarity * 100:.2f}%")
#         st.progress(similarity)
    
#     with metric_col2:
#         liveness = results.get('liveness_score', 0)
#         st.metric("Liveness Score", f"{liveness * 100:.2f}%")
#         st.progress(liveness)
    
#     with metric_col3:
#         authenticity = results.get('authenticity', 'Unknown')
#         if authenticity.lower() == "genuine":
#             st.success(f"✅ **{authenticity}**")
#         else:
#             st.error(f"🚨 **{authenticity}**")
    
#     # Display images side by side
#     st.markdown("### 📷 Image Comparison")
#     img_col1, img_col2 = st.columns(2)
    
#     with img_col1:
#         st.image(st.session_state.images['img1'], caption="Face 1 (Reference)", use_container_width=True)
    
#     with img_col2:
#         st.image(st.session_state.images['img2'], caption="Face 2 (Verification)", use_container_width=True)
    
#     st.markdown("---")
    
#     # Explainability Section
#     st.subheader("🧠 Step 3: Explain Decision (Optional)")
    
#     if st.button("🧠 Explain Decision (Grad-CAM)", type="secondary", use_container_width=True):
#         with st.spinner("🔄 Generating explanation... This may take a moment"):
#             try:
#                 # Prepare images again for explanation request
#                 img1_bytes = BytesIO()
#                 st.session_state.images['img1'].save(img1_bytes, format='PNG')
#                 img1_bytes.seek(0)
                
#                 img2_bytes = BytesIO()
#                 st.session_state.images['img2'].save(img2_bytes, format='PNG')
#                 img2_bytes.seek(0)
                
#                 files = {
#                     'image1': ('face1.png', img1_bytes, 'image/png'),
#                     'image2': ('face2.png', img2_bytes, 'image/png')
#                 }
                
#                 # Send request to explain endpoint
#                 response = requests.post(f"{FLASK_BACKEND_URL}/explain", files=files, timeout=60)
                
#                 if response.status_code == 200:
#                     explain_data = response.json()
                    
#                     st.success("✅ Explanation generated successfully!")
#                     st.markdown("### 🔍 Grad-CAM Heatmap Visualization")
#                     st.info("Red/yellow regions indicate areas the model focused on for decision-making.")
                    
#                     gradcam_col1, gradcam_col2 = st.columns(2)
                    
#                     # Decode base64 images (assuming backend returns base64 encoded images)
#                     with gradcam_col1:
#                         if 'gradcam1' in explain_data:
#                             gradcam1_data = base64.b64decode(explain_data['gradcam1'])
#                             gradcam1_img = Image.open(BytesIO(gradcam1_data))
#                             st.image(gradcam1_img, caption="Face 1 - Grad-CAM Heatmap", use_container_width=True)
                    
#                     with gradcam_col2:
#                         if 'gradcam2' in explain_data:
#                             gradcam2_data = base64.b64decode(explain_data['gradcam2'])
#                             gradcam2_img = Image.open(BytesIO(gradcam2_data))
#                             st.image(gradcam2_img, caption="Face 2 - Grad-CAM Heatmap", use_container_width=True)
#                 else:
#                     st.error(f"❌ Explanation error: {response.status_code} - {response.text}")
                    
#             except requests.exceptions.ConnectionError:
#                 st.error("❌ Cannot connect to Flask backend for explanation.")
#             except Exception as e:
#                 st.error(f"❌ Error generating explanation: {str(e)}")

# # Footer
# st.markdown("---")
# st.markdown("""
#     <div class='footer'>
#         Made with ❤️ for ZenTej Season 3 @ CAIR IIT Mandi<br>
#         <small>Powered by Advanced Deep Learning & Explainable AI</small>
#     </div>
# """, unsafe_allow_html=True)




import streamlit as st
import requests
from PIL import Image
from io import BytesIO
import base64
import os

# Page configuration
st.set_page_config(
    page_title="Deepfake-Proof eKYC System",
    page_icon="🛡️",
    layout="wide"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main-header {
        text-align: center;
        color: #FF6B35;
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 1rem;
    }
    .footer {
        text-align: center;
        margin-top: 3rem;
        padding: 1rem;
        color: #666;
    }
    </style>
""", unsafe_allow_html=True)

# Header with centered logo
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    # Display logo if exists
    logo_path = "logo.png"
    if os.path.exists(logo_path):
        try:
            logo_img = Image.open(logo_path)
            # Create centered logo
            logo_col1, logo_col2, logo_col3 = st.columns([1, 1, 1])
            with logo_col2:
                st.image(logo_img, width=80)
        except:
            pass
    
    # Title
    st.markdown("<h2 class='main-header'>Deepfake-Proof eKYC System</h2>", unsafe_allow_html=True)
st.markdown("---")

# Flask Backend URL (modify if your backend is hosted elsewhere)
FLASK_BACKEND_URL = "http://localhost:5000"

# Initialize session state for storing results
if 'verification_done' not in st.session_state:
    st.session_state.verification_done = False
if 'results' not in st.session_state:
    st.session_state.results = None
if 'images' not in st.session_state:
    st.session_state.images = {'img1': None, 'img2': None}

# Helper function to get the final image (prioritize camera over upload)
def get_final_image(upload_img, cam_img):
    if cam_img is not None:
        return Image.open(cam_img)
    elif upload_img is not None:
        return Image.open(upload_img)
    return None

# Input Section
st.subheader("📸 Step 1: Provide Two Face Images")
col1, col2 = st.columns(2)

with col1:
    st.markdown("### Face 1: Reference Image (ID Proof)")
    img1_upload = st.file_uploader("Upload Face 1", type=["jpg", "png", "jpeg"], key="upload1")
    img1_cam = st.camera_input("Or Capture Face 1", key="cam1")
    
    final_img1 = get_final_image(img1_upload, img1_cam)
    if final_img1:
        st.image(final_img1, caption="Selected Face 1", use_container_width=True)

with col2:
    st.markdown("### Face 2: Live Verification (Selfie)")
    img2_upload = st.file_uploader("Upload Face 2", type=["jpg", "png", "jpeg"], key="upload2")
    img2_cam = st.camera_input("Or Capture Face 2", key="cam2")
    
    final_img2 = get_final_image(img2_upload, img2_cam)
    if final_img2:
        st.image(final_img2, caption="Selected Face 2", use_container_width=True)

st.markdown("---")

# Authentication Button
st.subheader("🔐 Step 2: Authenticate")

if st.button("🔍 Authenticate", type="primary", use_container_width=True):
    # Validate inputs
    if not final_img1 or not final_img2:
        st.warning("⚠️ Please provide both images before authentication.")
    else:
        # Store images in session state
        st.session_state.images['img1'] = final_img1
        st.session_state.images['img2'] = final_img2
        
        with st.spinner("🔄 Authenticating... Please wait"):
            try:
                # Convert images to bytes for sending to Flask
                img1_bytes = BytesIO()
                final_img1.save(img1_bytes, format='PNG')
                img1_bytes.seek(0)
                
                img2_bytes = BytesIO()
                final_img2.save(img2_bytes, format='PNG')
                img2_bytes.seek(0)
                
                # Prepare files for POST request
                files = {
                    'image1': ('face1.png', img1_bytes, 'image/png'),
                    'image2': ('face2.png', img2_bytes, 'image/png')
                }
                
                # Send request to Flask backend
                response = requests.post(f"{FLASK_BACKEND_URL}/verify", files=files, timeout=30)
                
                if response.status_code == 200:
                    results = response.json()
                    st.session_state.results = results
                    st.session_state.verification_done = True
                    st.success("✅ Authentication completed successfully!")
                else:
                    st.error(f"❌ Backend error: {response.status_code} - {response.text}")
                    
            except requests.exceptions.ConnectionError:
                st.error("❌ Cannot connect to Flask backend. Make sure it's running on http://localhost:5000")
            except Exception as e:
                st.error(f"❌ Error during authentication: {str(e)}")

# Results Display Section
if st.session_state.verification_done and st.session_state.results:
    st.markdown("---")
    st.subheader("📊 Verification Results")
    
    results = st.session_state.results
    
    # Display metrics in columns
    metric_col1, metric_col2, metric_col3 = st.columns(3)
    
    with metric_col1:
        similarity = results.get('similarity_score', 0)
        st.metric("Similarity Score", f"{similarity * 100:.2f}%")
        st.progress(similarity)
    
    with metric_col2:
        liveness = results.get('liveness_score', 0)
        st.metric("Liveness Score", f"{liveness * 100:.2f}%")
        st.progress(liveness)
    
    with metric_col3:
        authenticity = results.get('authenticity', 'Unknown')
        if authenticity.lower() == "genuine":
            st.success(f"✅ **{authenticity}**")
        else:
            st.error(f"🚨 **{authenticity}**")
    
    # Display images side by side
    st.markdown("### 📷 Image Comparison")
    img_col1, img_col2 = st.columns(2)
    
    with img_col1:
        st.image(st.session_state.images['img1'], caption="Face 1 (Reference)", use_container_width=True)
    
    with img_col2:
        st.image(st.session_state.images['img2'], caption="Face 2 (Verification)", use_container_width=True)
    
    st.markdown("---")
    
    # Explainability Section
    st.subheader("🧠 Step 3: Explain Decision (Optional)")
    
    if st.button("🧠 Explain Decision (Grad-CAM)", type="secondary", use_container_width=True):
        with st.spinner("🔄 Generating explanation... This may take a moment"):
            try:
                # Prepare images again for explanation request
                img1_bytes = BytesIO()
                st.session_state.images['img1'].save(img1_bytes, format='PNG')
                img1_bytes.seek(0)
                
                img2_bytes = BytesIO()
                st.session_state.images['img2'].save(img2_bytes, format='PNG')
                img2_bytes.seek(0)
                
                files = {
                    'image1': ('face1.png', img1_bytes, 'image/png'),
                    'image2': ('face2.png', img2_bytes, 'image/png')
                }
                
                # Send request to explain endpoint
                response = requests.post(f"{FLASK_BACKEND_URL}/explain", files=files, timeout=60)
                
                if response.status_code == 200:
                    explain_data = response.json()
                    
                    st.success("✅ Explanation generated successfully!")
                    st.markdown("### 🔍 Grad-CAM Heatmap Visualization")
                    st.info("Red/yellow regions indicate areas the model focused on for decision-making.")
                    
                    gradcam_col1, gradcam_col2 = st.columns(2)
                    
                    # Decode base64 images (assuming backend returns base64 encoded images)
                    with gradcam_col1:
                        if 'gradcam1' in explain_data:
                            gradcam1_data = base64.b64decode(explain_data['gradcam1'])
                            gradcam1_img = Image.open(BytesIO(gradcam1_data))
                            st.image(gradcam1_img, caption="Face 1 - Grad-CAM Heatmap", use_container_width=True)
                    
                    with gradcam_col2:
                        if 'gradcam2' in explain_data:
                            gradcam2_data = base64.b64decode(explain_data['gradcam2'])
                            gradcam2_img = Image.open(BytesIO(gradcam2_data))
                            st.image(gradcam2_img, caption="Face 2 - Grad-CAM Heatmap", use_container_width=True)
                else:
                    st.error(f"❌ Explanation error: {response.status_code} - {response.text}")
                    
            except requests.exceptions.ConnectionError:
                st.error("❌ Cannot connect to Flask backend for explanation.")
            except Exception as e:
                st.error(f"❌ Error generating explanation: {str(e)}")

# Footer
st.markdown("---")
st.markdown("""
    <div class='footer'>
        Made with ❤️ for ZenTej Season 3 @ CAIR IIT Mandi<br>
        <small>Powered by Advanced Deep Learning & Explainable AI</small>
    </div>
""", unsafe_allow_html=True)



