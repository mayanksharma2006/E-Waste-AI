let cameraStream = null;
let capturedBlob = null;

const imageInput = document.getElementById("imageInput");
const preview = document.getElementById("preview");
const camera = document.getElementById("camera");
const canvas = document.getElementById("canvas");


// ================================
// UPLOAD IMAGE
// ================================

imageInput.addEventListener("change", function () {

    const file = this.files[0];

    if (!file) {
        return;
    }

    capturedBlob = null;

    preview.src = URL.createObjectURL(file);
    preview.style.display = "block";

    setStatus("Image selected. Ready for analysis.");

});


// ================================
// START CAMERA
// ================================

async function startCamera() {

    try {

        cameraStream = await navigator.mediaDevices.getUserMedia({
            video: {
                facingMode: "environment"
            },
            audio: false
        });

        camera.srcObject = cameraStream;
        camera.style.display = "block";

        document.getElementById("captureButton").disabled = false;
        document.getElementById("stopCameraButton").disabled = false;
        document.getElementById("startCameraButton").disabled = true;

        setStatus("Camera started.");

    } catch (error) {

        console.error(error);

        setStatus(
            "Camera error: " + error.message
        );

    }

}


// ================================
// CAPTURE IMAGE
// ================================

function captureImage() {

    if (!cameraStream) {

        setStatus("Start the camera first.");

        return;
    }

    const width = camera.videoWidth;
    const height = camera.videoHeight;

    if (!width || !height) {

        setStatus("Camera is not ready.");

        return;
    }

    canvas.width = width;
    canvas.height = height;

    const context = canvas.getContext("2d");

    context.drawImage(
        camera,
        0,
        0,
        width,
        height
    );

    canvas.toBlob(function (blob) {

        capturedBlob = blob;

        preview.src = URL.createObjectURL(blob);
        preview.style.display = "block";

        setStatus(
            "Photo captured. Click Analyze Image."
        );

    }, "image/jpeg", 0.95);

}


// ================================
// STOP CAMERA
// ================================

function stopCamera() {

    if (cameraStream) {

        cameraStream.getTracks().forEach(
            function (track) {
                track.stop();
            }
        );

        cameraStream = null;
    }

    camera.srcObject = null;
    camera.style.display = "none";

    document.getElementById("captureButton").disabled = true;
    document.getElementById("stopCameraButton").disabled = true;
    document.getElementById("startCameraButton").disabled = false;

    setStatus("Camera stopped.");

}


// ================================
// ANALYZE IMAGE
// ================================

async function analyzeImage() {

    let file = null;


    // Uploaded file
    if (imageInput.files.length > 0) {

        file = imageInput.files[0];

    }


    // Camera image
    else if (capturedBlob) {

        file = new File(
            [capturedBlob],
            "camera_capture.jpg",
            {
                type: "image/jpeg"
            }
        );

    }


    // Nothing selected
    else {

        setStatus(
            "Please upload an image or capture one first."
        );

        return;
    }


    const button =
        document.getElementById("analyzeButton");

    button.disabled = true;
    button.innerText = "⏳ Analyzing...";

    setStatus(
        "Uploading image and running AI..."
    );


    const formData = new FormData();

    formData.append("file", file);


    try {

        const response = await fetch(
            "https://e-waste-ai.onrender.com/analyze",
            {
                method: "POST",
                body: formData
            }
        );


        if (!response.ok) {

            const errorText =
                await response.text();

            console.error(
                "Backend error:",
                errorText
            );

            throw new Error(
                "Backend returned HTTP " +
                response.status
            );
        }


        const data =
            await response.json();


        console.log(
            "AI RESPONSE:",
            data
        );


        displayResults(data);

        setStatus(
            "Analysis completed successfully!"
        );


    } catch (error) {

        console.error(
            "Analysis error:",
            error
        );

        setStatus(
            "ERROR: " + error.message
        );

    } finally {

        button.disabled = false;
        button.innerText = "🔍 Analyze Image";

    }

}


// ================================
// DISPLAY RESULTS
// ================================

function displayResults(data) {

    const results =
        document.getElementById("results");

    results.classList.remove("hidden");


    document.getElementById(
        "totalComponents"
    ).innerText =
        data.total_components ?? 0;


    document.getElementById(
        "reusable"
    ).innerText =
        data.grouping?.reusable ?? 0;


    document.getElementById(
        "recyclable"
    ).innerText =
        data.grouping?.recyclable ?? 0;


    document.getElementById(
        "metalBearing"
    ).innerText =
        data.grouping?.metal_bearing ?? 0;


    const componentList =
        document.getElementById("componentList");

    componentList.innerHTML = "";


    const components =
        data.components || [];


    if (components.length === 0) {

        componentList.innerHTML =
            "<p>No components detected.</p>";

    }


    components.forEach(function (component) {

        const card =
            document.createElement("div");

        card.className =
            "component-card";


        card.innerHTML = `

            <h4>
                ${escapeHTML(
                    component.name || "Unknown"
                ).toUpperCase()}
            </h4>

            <p>
                <strong>Quantity:</strong>
                ${component.quantity ?? 0}
            </p>

            <p>
                <strong>Category:</strong>
                ${escapeHTML(
                    component.category || "Unknown"
                )}
            </p>

            <p>
                <strong>Reuse:</strong>
                ${escapeHTML(
                    component.reuse || "Unknown"
                )}
            </p>

            <p>
                <strong>Material:</strong>
                ${escapeHTML(
                    component.material || "Unknown"
                )}
            </p>

            <p>
                <strong>Metal:</strong>
                ${escapeHTML(
                    component.metal || "Unknown"
                )}
            </p>

            <p>
                <strong>Estimated Value:</strong>
                ₹${component.min_value ?? 0}
                -
                ₹${component.max_value ?? 0}
            </p>

        `;

        componentList.appendChild(card);

    });


    const minValue =
        data.total_min_value ?? 0;

    const maxValue =
        data.total_max_value ?? 0;


    document.getElementById(
        "estimatedPrice"
    ).innerText =
        `₹${Number(minValue).toFixed(2)} - ₹${Number(maxValue).toFixed(2)}`;


    const annotatedImage =
        document.getElementById("annotatedImage");


    if (data.annotated_image) {

        annotatedImage.src =
            "https://e-waste-ai.onrender.com" +
            data.annotated_image;

        annotatedImage.style.display =
            "block";
    }


    results.scrollIntoView({
        behavior: "smooth"
    });

}


// ================================
// STATUS MESSAGE
// ================================

function setStatus(message) {

    document.getElementById(
        "status"
    ).innerText = message;

}


// ================================
// HTML ESCAPE
// ================================

function escapeHTML(value) {

    const div =
        document.createElement("div");

    div.innerText =
        String(value);

    return div.innerHTML;

}

// ================================
// SCRAP VALUE CALCULATOR
// ================================

function calculateScrapValue() {

    const weight =
        Number(
            document.getElementById("pcbWeight").value
        );

    const rate =
        Number(
            document.getElementById("pcbRate").value
        );

    if (weight <= 0 || rate <= 0) {

        document.getElementById(
            "scrapValue"
        ).innerText = "Enter valid weight and rate.";

        return;
    }

    // grams → kilograms
    const weightKg = weight / 1000;

    const totalValue =
        weightKg * rate;

    document.getElementById(
        "scrapValue"
    ).innerText =
        `₹${totalValue.toFixed(2)}`;

}
