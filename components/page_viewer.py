
import streamlit as st
import streamlit.components.v2 as components
import base64
import html as html_utils
from io import BytesIO


# --------------------------------------------------------
# COMPONENT CSS (REGISTERED ONCE)
# --------------------------------------------------------

VIEWER_CSS = """
.viewer {
    width: 100%;
    display: flex;
    justify-content: center;
    overflow: auto;
}

svg {
    display: block;
    max-width: 100%;
    height: auto;
}

.detection-box {
    fill: transparent;
    stroke: blue;
    stroke-width: 4;
    cursor: pointer;
}

.detection-box:hover {
    fill: rgba(0, 0, 255, 0.12);
    stroke-width: 6;
}

.detection-label {
    fill: white;
    stroke: blue;
    stroke-width: 6px;
    paint-order: stroke;
    font-family: sans-serif;
    font-size: 16px;
    font-weight: bold;
    pointer-events: none;
}

.detection-box.selected {
    fill: rgba(0, 0, 255, 0.2);
    stroke-width: 7;
}
"""


# --------------------------------------------------------
# COMPONENT JAVASCRIPT (REGISTERED ONCE)
# --------------------------------------------------------

VIEWER_JS = """
export default function(component) {
    const { parentElement, setStateValue, data } = component;

    const viewer = parentElement.querySelector(".viewer");

    if (!viewer) return;

    // Update the viewer with the current image and detections.
    viewer.innerHTML = data.content;

    const boxes = viewer.querySelectorAll(".detection-box");

    boxes.forEach((box) => {
        box.onclick = () => {
            const index = Number(
                box.getAttribute("data-index")
            );

            setStateValue("selected", index);

            boxes.forEach((item) => {
                item.classList.remove("selected");
            });

            box.classList.add("selected");
        };
    });
}
"""


# --------------------------------------------------------
# REGISTER COMPONENT ONCE AT MODULE LEVEL
# --------------------------------------------------------

viewer = components.component(
    "document_detection_viewer",
    html='<div class="viewer"></div>',
    css=VIEWER_CSS,
    js=VIEWER_JS
)


# --------------------------------------------------------
# RENDER PAGE PREVIEW
# --------------------------------------------------------

def render_page_preview(
    image,
    detections=None,
    label_map=None,
    max_px=900,
    key="page_viewer"
):

    if label_map is None:
        label_map = {}

    # ----------------------------------------------------
    # RESIZE IMAGE
    # ----------------------------------------------------

    original_w, original_h = image.size

    scale = 1.0

    if original_w > max_px:
        scale = max_px / original_w

    display_w = int(original_w * scale)
    display_h = int(original_h * scale)

    display_image = image.resize(
        (display_w, display_h)
    )

    # ----------------------------------------------------
    # CONVERT IMAGE TO BASE64
    # ----------------------------------------------------

    buffer = BytesIO()

    display_image.save(
        buffer,
        format="PNG"
    )

    image_base64 = base64.b64encode(
        buffer.getvalue()
    ).decode("utf-8")

    # ----------------------------------------------------
    # PREPARE DETECTIONS
    # ----------------------------------------------------

    boxes = []

    if detections:

        for index, detection in enumerate(detections):

            x1, y1, x2, y2, conf, cls = detection

            x1 *= scale
            y1 *= scale
            x2 *= scale
            y2 *= scale

            label = label_map.get(
                int(cls),
                f"class {int(cls)}"
            )

            # Escape labels before inserting into HTML.
            label = html_utils.escape(str(label))

            boxes.append({
                "index": index,
                "x1": x1,
                "y1": y1,
                "x2": x2,
                "y2": y2,
                "label": label,
                "confidence": float(conf)
            })

    # ----------------------------------------------------
    # SVG BOXES
    # ----------------------------------------------------

    svg_boxes = ""

    for box in boxes:

        svg_boxes += f"""
        <rect
            x="{box['x1']}"
            y="{box['y1']}"
            width="{box['x2'] - box['x1']}"
            height="{box['y2'] - box['y1']}"
            data-index="{box['index']}"
            class="detection-box"
        />

        <text
            x="{box['x1'] + 5}"
            y="{max(18, box['y1'] - 5)}"
            data-index="{box['index']}"
            class="detection-label"
        >
            {box['index'] + 1}: {box['label']}
            {box['confidence'] * 100:.1f}%
        </text>
        """

    # ----------------------------------------------------
    # DYNAMIC HTML CONTENT
    # ----------------------------------------------------

    html_content = f"""
    <svg
        width="{display_w}"
        height="{display_h}"
        viewBox="0 0 {display_w} {display_h}"
    >
        <image
            href="data:image/png;base64,{image_base64}"
            width="{display_w}"
            height="{display_h}"
        />

        {svg_boxes}

    </svg>
    """

    # ----------------------------------------------------
    # MOUNT COMPONENT INSTANCE
    # ----------------------------------------------------

    result = viewer(
        key=key,
        data={"content": html_content},
        default={"selected": None},
        on_selected_change=lambda: None
    )

    # ----------------------------------------------------
    # RETURN SELECTED DETECTION
    # ----------------------------------------------------

    if result.selected is not None:
        return int(result.selected)

    return None
