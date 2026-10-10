import streamlit as st
import tempfile
from PIL import Image
from utils import *
from detector import *
from components.page_viewer import render_page_preview
from processors import process_selected_crop



# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Document Analyzer",
    page_icon="📑",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# ============================================================
# GLOBAL STYLE
# ============================================================

def set_app_style():

    st.markdown(
        """
        <style>

        .stApp {
            background: #000000;
        }

        .block-container {
            max-width: 1200px;
            padding-top: 2rem;
            padding-bottom: 3rem;
        }


        /* ====================================================
           HIDE STREAMLIT DEFAULT ELEMENTS
           ==================================================== */

        #MainMenu {
            visibility: hidden;
        }

        footer {
            visibility: hidden;
        }

        header {
            background: transparent !important;
        }


        /* ====================================================
           TYPOGRAPHY
           ==================================================== */

        h1,
        h2,
        h3,
        h4 {
            letter-spacing: -0.02em;
        }


        /* ====================================================
           UPLOAD
           ==================================================== */

        div[data-testid="stFileUploaderDropzone"] {

            background: #ffffff !important;

            border: 1.5px dashed #d1d5db !important;

            border-radius: 14px !important;

            transition:
                border-color 0.2s ease,
                background 0.2s ease;
        }

        div[data-testid="stFileUploaderDropzone"]:hover {

            border-color: #6366f1 !important;

            background: #fafaff !important;
        }


        /* ====================================================
           NATIVE BORDERED CONTAINERS
           ==================================================== */

        div[data-testid="stVerticalBlockBorderWrapper"] {

            border-radius: 16px !important;

            border-color: #e5e7eb !important;

            background: #ffffff !important;

            box-shadow:
                0 2px 8px rgba(15, 23, 42, 0.04);
        }

        div[data-testid="stVerticalBlockBorderWrapper"] > div {

            border-radius: 16px !important;
        }


        /* ====================================================
           PAGE NAVIGATION BUTTONS
           ==================================================== */

        div[data-testid="stButton"] button {

            border-radius: 10px !important;

            width: 38px !important;

            height: 38px !important;

            min-width: 38px !important;

            padding: 0 !important;

            border: 1px solid #e5e7eb !important;

            background: #ffffff !important;

            color: #374151 !important;

            font-size: 0.95rem;

            font-weight: 600;

            transition:
                background 0.15s ease,
                color 0.15s ease,
                border-color 0.15s ease,
                transform 0.15s ease;
        }

        div[data-testid="stButton"] button:hover:enabled {

            background: #111827 !important;

            color: #ffffff !important;

            border-color: #111827 !important;

            transform: translateY(-1px);
        }

        div[data-testid="stButton"] button:disabled {

            opacity: 0.3;
        }


        /* ====================================================
           REGION CAPTION
           ==================================================== */

        .region-caption {

            font-size: 0.72rem;

            color: #9ca3af;

            margin-top: 6px;

            text-align: center;
        }


        /* ====================================================
           RESULT TABS
           ==================================================== */

        button[data-baseweb="tab"] {

            font-size: 0.88rem !important;

            font-weight: 600 !important;

            color: #6b7280 !important;

            padding: 0.65rem 1rem !important;
        }

        button[data-baseweb="tab"][aria-selected="true"] {

            color: #4f46e5 !important;
        }

        div[data-baseweb="tab-highlight"] {

            background-color: #6366f1 !important;

            height: 2px !important;
        }


        /* ====================================================
           METRIC CARDS
           ==================================================== */

        div[data-testid="stMetric"] {

            background: #f9fafb;

            border: 1px solid #e5e7eb;

            border-radius: 12px;

            padding: 12px 14px;

            min-height: 90px;
        }

        div[data-testid="stMetricLabel"] {

            color: #6b7280 !important;

            font-size: 0.78rem !important;

            font-weight: 600 !important;
        }

        div[data-testid="stMetricValue"] {

            color: #111827 !important;

            font-size: 1.45rem !important;

            font-weight: 700 !important;
        }


        /* ====================================================
           ALERTS
           ==================================================== */

        div[data-testid="stAlert"] {

            border-radius: 12px;
        }


        /* ====================================================
           RESPONSIVE
           ==================================================== */

        @media (max-width: 768px) {

            .block-container {

                padding-left: 1rem;

                padding-right: 1rem;
            }

        }

        </style>
        """,
        unsafe_allow_html=True,
    )


set_app_style()


# ============================================================
# HEADER
# ============================================================

st.markdown(
    """

    <h1 style="
        text-align:center;
        margin-bottom:0.25rem;
        font-size:2.5rem;
        font-weight:700;
    ">

        Document Analyzer
    </h1>

    <p style="
        text-align:center;
        color:#6b7280;
        margin-top:0;
        font-size:1rem;
    ">
        Extract text, tables, and figures from PDFs or images using AI detection
    </p>

    <hr style="
        margin-top:1.5rem;
        margin-bottom:2rem;
        border:none;
        border-top:1px solid #e5e7eb;
    ">
    """,
    unsafe_allow_html=True
)


# ============================================================
# LABEL MAP
# ============================================================

label_map = {
    0: "text",
    1: "table",
    2: "figure"
}


# ============================================================
# HELPERS
# ============================================================

def render_region_grid(
    region_list,
    columns=3,
    max_px=420
):

    if not region_list:

        st.info(
            "Nothing found in this category."
        )

        return


    cols = st.columns(columns)


    for idx, region in enumerate(region_list):

        img = region["image"]

        w, h = img.size


        # Only shrink oversized crops.
        # Never upscale smaller images.

        if w > max_px:

            scale = max_px / w

            img = img.resize(
                (
                    max_px,
                    int(h * scale)
                )
            )


        with cols[idx % columns]:

            with st.container(
                border=True
            ):

                st.image(
                    img,
                    width="stretch"
                )

                st.markdown(
                    f"""
                    <div class="region-caption">
                        {w} × {h}px
                        &nbsp;·&nbsp;
                        Region {idx + 1}
                    </div>
                    """,
                    unsafe_allow_html=True
                )


# ============================================================
# UPLOAD SECTION
# ============================================================



st.caption(
    "Upload a PDF or image to analyze its text, tables, and figures."
)


uploaded_f = st.file_uploader(
    "Drop your PDF or image here",
    type=[
        "pdf",
        "png",
        "jpg",
        "jpeg"
    ]
)


# ============================================================
# PROCESSING
# ============================================================

if uploaded_f is not None:

    # ========================================================
    # SAVE TEMPORARY FILE
    # ========================================================

    with st.spinner(
        "Preparing file..."
    ):

        with tempfile.NamedTemporaryFile(
            delete=False
        ) as tmp_file:

            tmp_file.write(
                uploaded_f.read()
            )

            file_path = tmp_file.name


    # ========================================================
    # CONVERT FILE
    # ========================================================

    if uploaded_f.type == "application/pdf":

        with st.spinner(
            "Converting PDF to images..."
        ):

            page_images = convert_pdf_to_images(
                file_path
            )

    else:

        page_images = [
            Image.open(
                file_path
            ).convert("RGB")
        ]


    st.success(
        f"File processed successfully — "
        f"{len(page_images)} page(s) found."
    )


    # ========================================================
    # PAGE STATE
    # ========================================================

    if "page_idx" not in st.session_state:

        st.session_state.page_idx = 0


    # Clamp page index if a new file has fewer pages

    st.session_state.page_idx = max(
        0,
        min(
            st.session_state.page_idx,
            len(page_images) - 1
        )
    )


    # ========================================================
    # CURRENT PAGE
    # ========================================================

    i = st.session_state.page_idx

    image = page_images[i]


    # ========================================================
    # DETECTION
    # ========================================================

    with st.spinner(
        "Running detection model..."
    ):

        detections = detect_regions(
            image
        )
    # st.write("DETECTIONS:", detections)


    # ========================================================
    # PAGE PREVIEW + DETECTION RESULTS
    # ========================================================

    page_container = st.container(
        border=True
    )


    with page_container:

        left, right = st.columns(
            [1, 1.4]
        )


        # ====================================================
        # PAGE PREVIEW
        # ====================================================

        with left:

            st.markdown(
                    "<h4 style='color: white;'>Page Preview</h4>",
                    unsafe_allow_html=True
                )

            selected_index = render_page_preview(
                image=image,
                detections=detections,
                label_map=label_map,
                key=f"documnet_detection_viewer_{st.session_state.page_idx}"
            )
            
        with right:
            st.markdown(
                    "<h4 style='color: white;'>Selected Region</h4>",
                    unsafe_allow_html=True
                )
            if (selected_index is None
                or not detections
                or not (0 <= selected_index < len(detections))):
                st.info("Select a detected box in the page preview to inspect the regiona nd extract its content.")
                st.markdown("##### What you can do")
                st.markdown("""-**extract readable texts.
                            -Detect and display the table data.
                            -Inspect dimensions, aspect ratio and extract embedded text of the figures**""")
                
            else:
                selected_detection = detections [ selected_index ]
                x1, y1, x2, y2, conf, cls = selected_detection
                
                label = label_map.get(int(cls), f"class {int(cls)}")
                
                crop = image.crop((int(x1),int(y1), int(x2), int(y2)))
                st.caption(f"Region {selected_index + 1}."
                           f"{label.title()}")
                st.image(crop, width="stretch")
                
                st.write(f"**Class:** {label}")
                st.write(f"**Confidence:** {conf * 100:.1f}%")
                    
                st.write(f"**Region Coordinates:** " 
                         f"({x1:.1f}, {y1:.1f}) -> "
                         f"({x2:.1f}, {y2:.1f})")
                
                st.write(f"**Width:** {x2 - x1:.1f} px")
                st.write(f"**Height:** {y2 - y1:.1f} px")
                st.divider()
                
                st.markdown("##### Processing results")
                with st.spinner(f"Processing {label} region..."):
                    processing_output = process_selected_crop(crop, label)
                    
                if processing_output.get("error"):
                    st.error(processing_output["error"])
                    
                else:
                    result = processing_output["result"]
                    
                    if label == "text":
                        if result:
                            st.text_area("Extracted Text",
                                         value=result,
                                         height=200,
                                         key=f"ocr_{selected_index}_{st.session_state.page_idx}"
                                        )
                        else:
                            st.info("No text could be extarcted")
                            
                    elif label == "table":
                        if result:
                            for i, dataframe in enumerate(result, start=1):
                                st.markdown(f"**Extracted Table {i}**")
                                st.dataframe(dataframe,
                                             width="stretch",
                                             hide_index=True)
                        else:
                            st.warning("No table structure was detected.")
                            
                    
                    elif label == "figure":
                        if result:
                            st.write(f"**Dimensions:** {result['width']} x {result['height']} pixels")
                            
                            st.write(f"**Orientation:** {result['orientation']}")
                            st.write(f"**Aspect Ratio:** {result['aspect_ratio']}")
                            st.markdown("**Text found inside the figures**")
                            if result["embedded_text"]:
                                st.text_area("Embedded_text",
                                            value=result["embedded_text"],
                                            height=150,
                                            key=f"figure_text_{selected_index}_{st.session_state.page_idx}")
                            else:
                                st.info("No readable embedded text was found")
                        else:
                            st.info("No figure details could be extracted")
                        
                            

            # =================================================
            # PAGE NAVIGATION
            # =================================================

            if len(page_images) > 1:

                nav_l, nav_c, nav_r = st.columns(
                    [1, 4, 1]
                )


                # ---------------------------------------------
                # PREVIOUS PAGE
                # ---------------------------------------------

                with nav_l:

                    sub_l, sub_btn = st.columns(
                        [1, 1]
                    )

                    with sub_btn:

                        if st.button(
                            "◀",
                            key="prev_page",
                            disabled=(
                                st.session_state.page_idx == 0
                            )
                        ):

                            st.session_state.page_idx -= 1

                            st.rerun()


                # ---------------------------------------------
                # PAGE INDICATOR
                # ---------------------------------------------

                with nav_c:

                    st.markdown(
                        f"""
                        <div style="
                            text-align:center;
                            padding-top:4px;
                            font-weight:600;
                            font-size:0.95rem;
                            color:#374151;
                        ">
                            Page {st.session_state.page_idx + 1}
                            / {len(page_images)}
                        </div>
                        """,
                        unsafe_allow_html=True
                    )


                # ---------------------------------------------
                # NEXT PAGE
                # ---------------------------------------------

                with nav_r:

                    sub_btn, sub_r = st.columns(
                        [1, 1]
                    )

                    with sub_btn:

                        if st.button(
                            "▶",
                            key="next_page",
                            disabled=(
                                st.session_state.page_idx
                                == len(page_images) - 1
                            )
                        ):

                            st.session_state.page_idx += 1

                            st.rerun()


        # ====================================================
        # DETECTION RESULTS
        # ====================================================

        # with right:

        #     st.markdown(
        #         "#### Detection Results"
        #     )

        #     if not detections:

        #         st.warning(
        #             "No regions detected on this page."
        #         )

        #     else:

        #         regions = extract_detected_regions(
        #             image,
        #             detections,
        #             label_map
        #         )


        #         save_combined_regions(
        #             regions
        #         )


        #         text_regions = [
        #             r
        #             for r in regions
        #             if r["label"] == "text"
        #         ]


        #         table_regions = [
        #             r
        #             for r in regions
        #             if r["label"] == "table"
        #         ]


        #         figure_regions = [
        #             r
        #             for r in regions
        #             if r["label"] == "figure"
        #         ]


        #         # --------------------------------------------
        #         # DETECTED REGION TABS
        #         # --------------------------------------------

        #         if detections:

        #             tab1, tab2, tab3 = st.tabs(
        #                 [
        #                     f":material/article: Text ({len(text_regions)})",
        #                     f":material/table: Tables ({len(table_regions)})",
        #                     f":material/image: Figures ({len(figure_regions)})"
        #                 ]
        #             )


        #             # ========================================
        #             # TEXT
        #             # ========================================

        #             with tab1:

        #                 render_region_grid(
        #                     text_regions,
        #                     columns=3
        #                 )


        #             # ========================================
        #             # TABLES
        #             # ========================================

        #             with tab2:

        #                 render_region_grid(
        #                     table_regions,
        #                     columns=2
        #                 )


        #             # ========================================
        #             # FIGURES
        #             # ========================================

        #             with tab3:

        #                 render_region_grid(
        #                     figure_regions,
        #                     columns=3
        #                 )
