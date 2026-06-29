import streamlit as st
import tempfile
from PIL import Image
from utils import *
from detector import *

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Document Analyzer",
    page_icon="📑",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ---------------- BACKGROUND & GLOBAL STYLE ----------------
def set_app_style():
    """
    CSS-only mesh-gradient background: large soft color blobs
    on a dark slate base, with a frosted-glass card on top.
    No image asset needed, and the blur keeps it from ever
    competing with the documents/tables/figures on display.
    """
    st.markdown(
        """
        <style>
        .stApp {
            background-color: #0f1424;
            background-image:
                radial-gradient(circle at 12% 18%, rgba(99,102,241,0.55) 0%, transparent 38%),
                radial-gradient(circle at 85% 12%, rgba(45,212,191,0.45) 0%, transparent 40%),
                radial-gradient(circle at 75% 80%, rgba(244,114,182,0.35) 0%, transparent 42%),
                radial-gradient(circle at 15% 85%, rgba(251,191,36,0.30) 0%, transparent 40%),
                linear-gradient(160deg, #0f1424 0%, #161b2e 100%);
            background-attachment: fixed;
        }

        .block-container {
            padding-top: 2rem;
            padding-bottom: 3rem;
            background-color: rgba(255,255,255,0.88);
            backdrop-filter: blur(18px);
            -webkit-backdrop-filter: blur(18px);
            border: 1px solid rgba(255,255,255,0.6);
            border-radius: 20px;
            max-width: 1200px;
            box-shadow: 0 20px 60px rgba(15,23,42,0.35);
        }

        h1, h2, h3 {
            color: #1f2937;
        }

        .region-caption {
            font-size: 0.78rem;
            color: #6b7280;
            margin-top: 6px;
            text-align: center;
        }

        /* ---- Native bordered container used to wrap each page's results ---- */
        div[data-testid="stVerticalBlockBorderWrapper"] > div {
            border-radius: 14px !important;
            box-shadow: 0 1px 4px rgba(0,0,0,0.05);
            margin-bottom: 14px;
        }

        /* ---- Small stat pills ---- */
        .stat-pill {
            display: inline-block;
            background: #f3f4f6;
            color: #374151;
            border-radius: 999px;
            padding: 4px 14px;
            font-size: 0.85rem;
            margin-right: 8px;
        }

        div[data-testid="stFileUploaderDropzone"] {
            border-radius: 12px;
        }

        /* ---- Page navigator (arrow buttons + indicator) ---- */
        .page-nav-wrap {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 18px;
            margin: 0;
            height: 100%;
            padding-top: 4px;
        }
        .page-nav-indicator {
            background: #1f2937;
            color: #ffffff;
            border-radius: 999px;
            padding: 8px 22px;
            font-weight: 600;
            font-size: 0.95rem;
            min-width: 110px;
            text-align: center;
            letter-spacing: 0.02em;
        }
        div[data-testid="stButton"] button {
            border-radius: 50% !important;
            width: 38px !important;
            height: 38px !important;
            min-width: 38px !important;
            padding: 0 !important;
            font-size: 1rem;
            font-weight: 700;
            border: 1px solid #d1d5db !important;
            background: #ffffff !important;
            color: #1f2937 !important;
            box-shadow: 0 1px 2px rgba(0,0,0,0.06);
            transition: all 0.15s ease;
        }
        div[data-testid="stButton"] button:hover:enabled {
            background: #1f2937 !important;
            color: #ffffff !important;
            border-color: #1f2937 !important;
        }
        div[data-testid="stButton"] button:disabled {
            opacity: 0.3;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

set_app_style()

# ---------------- HEADER ----------------
st.markdown(
    """
    <h1 style='text-align:center; margin-bottom:0.2rem;'>📑 Document Analyzer</h1>
    <p style='text-align:center; color:gray; margin-top:0;'>
    Extract text, tables, and figures from PDFs or images using AI detection
    </p>
    <hr>
    """,
    unsafe_allow_html=True
)

# ---------------- LABEL MAP ----------------
label_map = {0: "text", 1: "table", 2: "figure"}

# ---------------- HELPERS ----------------
def render_region_grid(region_list, columns=3, max_px=420):
    """
    Render cropped regions in a responsive grid without upscaling
    small crops or distorting their aspect ratio.
    """
    if not region_list:
        st.info("Nothing found in this category.")
        return

    cols = st.columns(columns)
    for idx, region in enumerate(region_list):
        img = region["image"]
        w, h = img.size

        # Only shrink oversized crops — never stretch small ones up.
        if w > max_px:
            scale = max_px / w
            img = img.resize((max_px, int(h * scale)))

        with cols[idx % columns]:
            with st.container(border=True):
                st.image(img)
                st.markdown(
                    f'<div class="region-caption">{w}×{h}px · region {idx + 1}</div>',
                    unsafe_allow_html=True
                )


def render_page_preview(image, max_px=900):
    """Show the full page at a sane, non-blurry resolution."""
    w, h = image.size
    if w > max_px:
        scale = max_px / w
        image = image.resize((max_px, int(h * scale)))
    st.image(image)


# ---------------- UPLOAD SECTION ----------------
st.markdown("### 📤 Upload Document")

uploaded_f = st.file_uploader(
    "Drop your PDF or image here",
    type=["pdf", "png", "jpg", "jpeg"]
)

# ---------------- PROCESSING ----------------
if uploaded_f is not None:

    with st.spinner("Preparing file..."):
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            tmp_file.write(uploaded_f.read())
            file_path = tmp_file.name

    if uploaded_f.type == "application/pdf":
        st.info("Converting PDF to images...")
        page_images = convert_pdf_to_images(file_path)
    else:
        page_images = [Image.open(file_path).convert("RGB")]

    st.success(f"File processed successfully — {len(page_images)} page(s) found.")

    # ---- Page navigator: left/right arrows + indicator pill ----
    if "page_idx" not in st.session_state:
        st.session_state.page_idx = 0

    # Clamp in case a new, shorter file was uploaded
    st.session_state.page_idx = max(0, min(st.session_state.page_idx, len(page_images) - 1))

    if len(page_images) > 1:
        nav_l, nav_c, nav_r = st.columns([1, 4, 1])
        with nav_l:
            sub_l, sub_btn = st.columns([1, 1])
            with sub_btn:
                if st.button("◀", key="prev_page", disabled=(st.session_state.page_idx == 0)):
                    st.session_state.page_idx -= 1
        with nav_c:
            st.markdown(
                f"""
                <div class="page-nav-wrap">
                    <span class="page-nav-indicator">Page {st.session_state.page_idx + 1} of {len(page_images)}</span>
                </div>
                """,
                unsafe_allow_html=True
            )
        with nav_r:
            sub_btn, sub_r = st.columns([1, 1])
            with sub_btn:
                if st.button("▶", key="next_page", disabled=(st.session_state.page_idx == len(page_images) - 1)):
                    st.session_state.page_idx += 1

    i = st.session_state.page_idx
    image = page_images[i]

    page_container = st.container(border=True)
    with page_container:
        left, right = st.columns([1, 1.4])
        with left:
            render_page_preview(image)

        with st.spinner("Running detection model..."):
            detections = detect_regions(image)

        if not detections:
            with right:
                st.warning("No regions detected on this page.")
        else:
            regions = extract_detected_regions(image, detections, label_map)
            save_combined_regions(regions)

            text_regions = [r for r in regions if r["label"] == "text"]
            table_regions = [r for r in regions if r["label"] == "table"]
            figure_regions = [r for r in regions if r["label"] == "figure"]

            with right:
                st.markdown("#### Summary")
                st.markdown(
                    f"""
                    <span class="stat-pill">📝 {len(text_regions)} text</span>
                    <span class="stat-pill">📊 {len(table_regions)} tables</span>
                    <span class="stat-pill">🖼️ {len(figure_regions)} figures</span>
                    """,
                    unsafe_allow_html=True
                )

            st.markdown("### 🔍 Detection Results")
            tab1, tab2, tab3 = st.tabs([
                f"📝 Text ({len(text_regions)})",
                f"📊 Tables ({len(table_regions)})",
                f"🖼️ Figures ({len(figure_regions)})",
            ])

            with tab1:
                render_region_grid(text_regions, columns=3)
            with tab2:
                render_region_grid(table_regions, columns=2)
            with tab3:
                render_region_grid(figure_regions, columns=3)