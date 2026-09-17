from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from ultralytics import YOLO

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from component_database import COMPONENT_DATABASE
from price_database import PRICE_DATABASE
from grouping import get_groups

import os
import shutil
import uuid

from PIL import Image


# ============================================================
# E-WASTE AI BACKEND
# ============================================================

app = FastAPI(
    title="E-Waste AI",
    description="PCB and electronic waste detection API"
)


# ============================================================
# FOLDERS
# ============================================================

UPLOAD_FOLDER = "uploads"
ANNOTATED_FOLDER = "annotated"

os.makedirs(
    UPLOAD_FOLDER,
    exist_ok=True
)

os.makedirs(
    ANNOTATED_FOLDER,
    exist_ok=True
)


# ============================================================
# SERVE ANNOTATED IMAGES
# ============================================================

app.mount(
    "/annotated",
    StaticFiles(directory=ANNOTATED_FOLDER),
    name="annotated"
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# LOAD YOLO MODEL
# ============================================================

MODEL_PATH = "../runs/detect/results/pcb_first_model/weights/best.pt"

print("Loading YOLO model...")

model = YOLO(MODEL_PATH)

print("YOLO model loaded successfully!")


# ============================================================
# HOME
# ============================================================

@app.get("/")
def home():

    return {
        "status": "online",
        "message": "E-Waste AI backend is running"
    }


# ============================================================
# ANALYZE IMAGE
# ============================================================

@app.post("/analyze")
async def analyze_image(
    file: UploadFile = File(...)
):

    # --------------------------------------------------------
    # Generate unique filename
    # --------------------------------------------------------

    extension = os.path.splitext(
        file.filename
    )[1]

    filename = (
        str(uuid.uuid4()) + extension
    )

    image_path = os.path.join(
        UPLOAD_FOLDER,
        filename
    )


    # --------------------------------------------------------
    # Save uploaded image
    # --------------------------------------------------------

    with open(
        image_path,
        "wb"
    ) as buffer:

        shutil.copyfileobj(
            file.file,
            buffer
        )


    # --------------------------------------------------------
    # YOLO DETECTION
    # --------------------------------------------------------

    print("Analyzing image...")

    results = model.predict(
        source=image_path,
        conf=0.25,
        imgsz=640,
        max_det=500,
        save=False
    )

    result = results[0]


    # --------------------------------------------------------
    # SAVE ANNOTATED IMAGE
    # --------------------------------------------------------

    annotated_filename = (
        str(uuid.uuid4()) + ".jpg"
    )

    annotated_path = os.path.join(
        ANNOTATED_FOLDER,
        annotated_filename
    )

    annotated_image = result.plot()

    Image.fromarray(
        annotated_image
    ).save(
        annotated_path
    )


    # --------------------------------------------------------
    # COMPONENT COUNTING
    # --------------------------------------------------------

    component_counts = {}


    for box in result.boxes:

        class_id = int(
            box.cls[0]
        )

        component_name = model.names[
            class_id
        ]

        if component_name not in component_counts:

            component_counts[
                component_name
            ] = 0

        component_counts[
            component_name
        ] += 1


    # --------------------------------------------------------
    # GROUP COUNTS
    # --------------------------------------------------------

    group_counts = {

        "reusable": 0,

        "recyclable": 0,

        "pure_waste": 0,

        "metal_bearing": 0

    }


    # --------------------------------------------------------
    # TOTAL PRICE
    # --------------------------------------------------------

    total_min_value = 0

    total_max_value = 0


    # --------------------------------------------------------
    # COMPONENT DETAILS
    # --------------------------------------------------------

    components = []


    for component, count in sorted(
        component_counts.items()
    ):

        info = COMPONENT_DATABASE.get(
            component
        )

        price = PRICE_DATABASE.get(
            component
        )


        # ----------------------------------------------------
        # Groups
        # ----------------------------------------------------

        groups = get_groups(
            component
        )

        for group in groups:

            if group in group_counts:

                group_counts[
                    group
                ] += count


        # ----------------------------------------------------
        # Price
        # ----------------------------------------------------

        min_value = 0

        max_value = 0


        if price:

            min_value = (
                count *
                price["min_price"]
            )

            max_value = (
                count *
                price["max_price"]
            )

            total_min_value += (
                min_value
            )

            total_max_value += (
                max_value
            )


        # ----------------------------------------------------
        # Component result
        # ----------------------------------------------------

        components.append({

            "name":
                component,

            "quantity":
                count,

            "category":
                info["category"]
                if info
                else "Unknown",

            "reuse":
                info["reuse"]
                if info
                else "Unknown",

            "material":
                info["material"]
                if info
                else "Unknown",

            "metal":
                info["metal"]
                if info
                else "Unknown",

            "groups":
                groups,

            "min_value":
                min_value,

            "max_value":
                max_value

        })


    # ========================================================
    # RESPONSE
    # ========================================================

    response = {

        "success":
            True,

        "total_components":
            sum(
                component_counts.values()
            ),

        "components":
            components,

        "groups":
            group_counts,

        "total_min_value":
            round(
                total_min_value,
                2
            ),

        "total_max_value":
            round(
                total_max_value,
                2
            ),

        "annotated_image":
            "/annotated/"
            + annotated_filename,

        "estimated_value": {

            "minimum":
                round(
                    total_min_value,
                    2
                ),

            "maximum":
                round(
                    total_max_value,
                    2
                )

        }

    }


    # --------------------------------------------------------
    # Remove temporary uploaded image
    # --------------------------------------------------------

    try:

        os.remove(
            image_path
        )

    except:

        pass


    print(
        "Analysis completed!"
    )

    return response