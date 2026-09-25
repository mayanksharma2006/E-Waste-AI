from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from ultralytics import YOLO

import sys
import os
import shutil
import uuid

from PIL import Image


# ============================================================
# PROJECT PATH
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

# Add project root to Python path
sys.path.append(BASE_DIR)


# ============================================================
# PROJECT DATABASES
# ============================================================

from component_database import COMPONENT_DATABASE
from price_database import PRICE_DATABASE
from grouping import get_groups


# ============================================================
# E-WASTE AI BACKEND
# ============================================================

app = FastAPI(
    title="E-Waste AI",
    description="PCB and electronic waste detection API"
)


# ============================================================
# RESULTS FOLDER
# ============================================================

RESULTS_FOLDER = os.path.join(
    BASE_DIR,
    "results"
)

os.makedirs(
    RESULTS_FOLDER,
    exist_ok=True
)


# ============================================================
# SERVE RESULT IMAGES
# ============================================================

app.mount(
    "/results",
    StaticFiles(directory=RESULTS_FOLDER),
    name="results"
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

MODEL_PATH = os.path.join(
    BASE_DIR,
    "runs",
    "detect",
    "results",
    "pcb_first_model",
    "weights",
    "best.pt"
)

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

    if not extension:
        extension = ".jpg"


    original_filename = (
        "original_"
        + str(uuid.uuid4())
        + extension
    )


    image_path = os.path.join(
        RESULTS_FOLDER,
        original_filename
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


    print(
        "Uploaded image saved:",
        image_path
    )


    # --------------------------------------------------------
    # YOLO DETECTION
    # --------------------------------------------------------

    print("Analyzing image...")

    results = model.predict(
        source=image_path,
        conf=0.35,
        imgsz=256,
        max_det=50,
        save=False,
        verbose=False,
        device="cpu"
    )

    result = results[0]


    # --------------------------------------------------------
    # SAVE ANNOTATED IMAGE
    # --------------------------------------------------------

    annotated_filename = (
        "annotated_"
        + str(uuid.uuid4())
        + ".jpg"
    )


    annotated_path = os.path.join(
        RESULTS_FOLDER,
        annotated_filename
    )


    annotated_image = result.plot()


    Image.fromarray(
        annotated_image
    ).save(
        annotated_path
    )


    print(
        "Annotated image saved:",
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


        # Original uploaded image
        "uploaded_image":
            "/results/"
            + original_filename,


        # YOLO annotated image
        "annotated_image":
            "/results/"
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


    # ========================================================
    # DO NOT DELETE THE FILES
    # ========================================================
    #
    # Both images remain inside:
    #
    # E_WASTE_AI/results/
    #
    # ========================================================


    print(
        "Analysis completed!"
    )


    return response