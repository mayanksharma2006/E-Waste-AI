const AI_API_URL =
  "https://e-waste-ai.onrender.com";


let cameraStream = null;
let selectedFile = null;
let previewUrl = null;


/*
|--------------------------------------------------------------------------
| Elements
|--------------------------------------------------------------------------
*/

const imageInput =
  document.getElementById(
    "imageInput"
  );

const uploadButton =
  document.getElementById(
    "uploadButton"
  );

const cameraButton =
  document.getElementById(
    "cameraButton"
  );

const cameraWrapper =
  document.getElementById(
    "cameraWrapper"
  );

const camera =
  document.getElementById(
    "camera"
  );

const canvas =
  document.getElementById(
    "canvas"
  );

const captureButton =
  document.getElementById(
    "captureButton"
  );

const stopCameraButton =
  document.getElementById(
    "stopCameraButton"
  );

const previewWrapper =
  document.getElementById(
    "previewWrapper"
  );

const preview =
  document.getElementById(
    "preview"
  );

const removeImageButton =
  document.getElementById(
    "removeImageButton"
  );

const analyzeButton =
  document.getElementById(
    "analyzeButton"
  );

const status =
  document.getElementById(
    "status"
  );

const results =
  document.getElementById(
    "results"
  );

const componentList =
  document.getElementById(
    "componentList"
  );

const annotatedSection =
  document.getElementById(
    "annotatedSection"
  );

const annotatedImage =
  document.getElementById(
    "annotatedImage"
  );


/*
|--------------------------------------------------------------------------
| Upload
|--------------------------------------------------------------------------
*/

uploadButton.addEventListener(
  "click",
  () => {
    imageInput.click();
  }
);


imageInput.addEventListener(
  "change",
  () => {

    const file =
      imageInput.files?.[0];

    if (!file) {
      return;
    }

    if (
      !file.type.startsWith(
        "image/"
      )
    ) {
      setStatus(
        "Please select a valid image."
      );

      return;
    }

    setSelectedFile(file);

  }
);


/*
|--------------------------------------------------------------------------
| Camera
|--------------------------------------------------------------------------
*/

cameraButton.addEventListener(
  "click",
  startCamera
);


captureButton.addEventListener(
  "click",
  captureImage
);


stopCameraButton.addEventListener(
  "click",
  stopCamera
);


async function startCamera() {

  try {

    setStatus(
      "Starting camera..."
    );

    const stream =
      await navigator.mediaDevices.getUserMedia(
        {
          video: {
            facingMode: {
              ideal: "environment",
            },
          },

          audio: false,
        }
      );

    cameraStream = stream;

    camera.srcObject =
      stream;

    cameraWrapper.hidden =
      false;

    await camera.play();

    setStatus(
      "Camera ready. Capture your e-waste."
    );

  } catch (error) {

    console.error(
      "Camera error:",
      error
    );

    setStatus(
      "Camera error: " +
        error.message
    );

  }

}


/*
|--------------------------------------------------------------------------
| Capture
|--------------------------------------------------------------------------
*/

function captureImage() {

  if (!cameraStream) {

    setStatus(
      "Start the camera first."
    );

    return;
  }

  const width =
    camera.videoWidth;

  const height =
    camera.videoHeight;

  if (!width || !height) {

    setStatus(
      "Camera is not ready yet."
    );

    return;
  }

  canvas.width =
    width;

  canvas.height =
    height;

  const context =
    canvas.getContext(
      "2d"
    );

  context.drawImage(
    camera,
    0,
    0,
    width,
    height
  );

  canvas.toBlob(
    (blob) => {

      if (!blob) {

        setStatus(
          "Unable to capture image."
        );

        return;
      }

      const file =
        new File(
          [blob],
          "camera_capture.jpg",
          {
            type: "image/jpeg",
          }
        );

      setSelectedFile(
        file
      );

      stopCamera();

      setStatus(
        "Photo captured. Ready for analysis."
      );

    },
    "image/jpeg",
    0.9
  );

}


/*
|--------------------------------------------------------------------------
| Stop camera
|--------------------------------------------------------------------------
*/

function stopCamera() {

  if (cameraStream) {

    cameraStream
      .getTracks()
      .forEach(
        (track) => {
          track.stop();
        }
      );

    cameraStream = null;
  }

  camera.srcObject =
    null;

  cameraWrapper.hidden =
    true;

}


/*
|--------------------------------------------------------------------------
| Set selected file
|--------------------------------------------------------------------------
*/

function setSelectedFile(
  file
) {

  selectedFile =
    file;

  if (previewUrl) {

    URL.revokeObjectURL(
      previewUrl
    );

  }

  previewUrl =
    URL.createObjectURL(
      file
    );

  preview.src =
    previewUrl;

  previewWrapper.hidden =
    false;

  analyzeButton.disabled =
    false;

  results.hidden =
    true;

  annotatedSection.hidden =
    true;

  setStatus(
    "Image selected. Ready for analysis."
  );

}


/*
|--------------------------------------------------------------------------
| Remove image
|--------------------------------------------------------------------------
*/

removeImageButton.addEventListener(
  "click",
  clearImage
);


function clearImage() {

  if (previewUrl) {

    URL.revokeObjectURL(
      previewUrl
    );

    previewUrl =
      null;
  }

  selectedFile =
    null;

  imageInput.value =
    "";

  preview.src =
    "";

  previewWrapper.hidden =
    true;

  analyzeButton.disabled =
    true;

  results.hidden =
    true;

  annotatedSection.hidden =
    true;

  setStatus(
    ""
  );

}


/*
|--------------------------------------------------------------------------
| Analyze
|--------------------------------------------------------------------------
*/

analyzeButton.addEventListener(
  "click",
  analyzeImage
);


async function analyzeImage() {

  if (!selectedFile) {

    setStatus(
      "Please select an image first."
    );

    return;
  }

  analyzeButton.disabled =
    true;

  analyzeButton.innerHTML =
    "⏳ Analyzing...";

  setStatus(
    "Uploading image and running AI..."
  );

  const formData =
    new FormData();

  formData.append(
    "file",
    selectedFile
  );

  try {

    const response =
      await fetch(
        `${AI_API_URL}/analyze`,
        {
          method: "POST",
          body: formData,
        }
      );

    if (!response.ok) {

      const errorText =
        await response.text();

      console.error(
        "AI backend error:",
        errorText
      );

      throw new Error(
        `Backend returned HTTP ${response.status}`
      );

    }

    const data =
      await response.json();

    console.log(
      "AI response:",
      data
    );

    displayResults(
      data
    );

    setStatus(
      "Analysis completed successfully."
    );

  } catch (error) {

    console.error(
      "Analysis error:",
      error
    );

    setStatus(
      "ERROR: " +
        error.message
    );

  } finally {

    analyzeButton.disabled =
      false;

    analyzeButton.innerHTML =
      "🔍 Analyze Image";

  }

}


/*
|--------------------------------------------------------------------------
| Display results
|--------------------------------------------------------------------------
*/

function displayResults(
  data
) {

  results.hidden =
    false;


  /*
   * Summary
   */

  document.getElementById(
    "totalComponents"
  ).innerText =
    data.total_components ??
    0;


  document.getElementById(
    "reusable"
  ).innerText =
    data.grouping?.reusable ??
    0;


  document.getElementById(
    "recyclable"
  ).innerText =
    data.grouping?.recyclable ??
    0;


  document.getElementById(
    "metalBearing"
  ).innerText =
    data.grouping?.metal_bearing ??
    0;


  /*
   * Components
   */

  componentList.innerHTML =
    "";


  const components =
    data.components || [];


  if (
    components.length === 0
  ) {

    componentList.innerHTML = `
      <div class="component-card">
        <div class="component-name">
          No components detected
        </div>
      </div>
    `;

  }


  components.forEach(
    (component) => {

      const card =
        document.createElement(
          "div"
        );

      card.className =
        "component-card";


      const name =
        escapeHTML(
          component.name ||
            "Unknown"
        );


      card.innerHTML = `

        <div class="component-name">
          ${name.toUpperCase()}
        </div>

        <div class="component-row">
          <span>
            Quantity
          </span>

          <span>
            ${component.quantity ?? 0}
          </span>
        </div>

        <div class="component-row">
          <span>
            Category
          </span>

          <span>
            ${escapeHTML(
              component.category ||
                "Unknown"
            )}
          </span>
        </div>

        <div class="component-row">
          <span>
            Reuse
          </span>

          <span>
            ${escapeHTML(
              component.reuse ||
                "Unknown"
            )}
          </span>
        </div>

        <div class="component-row">
          <span>
            Material
          </span>

          <span>
            ${escapeHTML(
              component.material ||
                "Unknown"
            )}
          </span>
        </div>

        <div class="component-row">
          <span>
            Metal
          </span>

          <span>
            ${escapeHTML(
              component.metal ||
                "Unknown"
            )}
          </span>
        </div>

        <div class="component-row">
          <span>
            Estimated value
          </span>

          <span>
            ₹${component.min_value ?? 0}
            -
            ₹${component.max_value ?? 0}
          </span>
        </div>

      `;

      componentList.appendChild(
        card
      );

    }
  );


  /*
   * Estimated price
   */

  const minValue =
    Number(
      data.total_min_value ??
        0
    );

  const maxValue =
    Number(
      data.total_max_value ??
        0
    );


  document.getElementById(
    "estimatedPrice"
  ).innerText =
    `₹${minValue.toFixed(2)} - ₹${maxValue.toFixed(2)}`;


  /*
   * Annotated image
   */

  if (
    data.annotated_image
  ) {

    annotatedImage.src =
      `${AI_API_URL}${data.annotated_image}`;

    annotatedSection.hidden =
      false;

  } else {

    annotatedSection.hidden =
      true;

  }


  /*
   * Scroll
   */

  setTimeout(
    () => {

      results.scrollIntoView({
        behavior: "smooth",
        block: "start",
      });

    },
    100
  );

}


/*
|--------------------------------------------------------------------------
| Scrap calculator
|--------------------------------------------------------------------------
*/

document
  .getElementById(
    "calculateButton"
  )
  .addEventListener(
    "click",
    calculateScrapValue
  );


function calculateScrapValue() {

  const weight =
    Number(
      document.getElementById(
        "pcbWeight"
      ).value
    );

  const rate =
    Number(
      document.getElementById(
        "pcbRate"
      ).value
    );


  if (
    weight <= 0 ||
    rate <= 0
  ) {

    document.getElementById(
      "scrapValue"
    ).innerText =
      "Enter valid weight and rate.";

    return;
  }


  const weightKg =
    weight / 1000;


  const totalValue =
    weightKg * rate;


  document.getElementById(
    "scrapValue"
  ).innerText =
    `₹${totalValue.toFixed(2)}`;

}


/*
|--------------------------------------------------------------------------
| Status
|--------------------------------------------------------------------------
*/

function setStatus(
  message
) {

  if (!message) {

    status.hidden =
      true;

    status.innerText =
      "";

    return;
  }

  status.hidden =
    false;

  status.innerText =
    message;

}


/*
|--------------------------------------------------------------------------
| HTML escape
|--------------------------------------------------------------------------
*/

function escapeHTML(
  value
) {

  const div =
    document.createElement(
      "div"
    );

  div.innerText =
    String(value);

  return div.innerHTML;

}


/*
|--------------------------------------------------------------------------
| Cleanup
|--------------------------------------------------------------------------
*/

window.addEventListener(
  "beforeunload",
  () => {

    stopCamera();

    if (previewUrl) {

      URL.revokeObjectURL(
        previewUrl
      );

    }

  }
);