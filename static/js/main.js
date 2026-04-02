/**
 * main.js — Client-side interactivity for the Object Detection app.
 *
 * Responsibilities:
 *  1. Validate that a file is selected before form submission.
 *  2. Show a loading spinner on the submit button while inference runs.
 *  3. Show a live image preview when the user picks a file.
 *  4. Support drag-and-drop file selection on the drop zone.
 */

(function () {
  "use strict";

  // ── Element references ───────────────────────────────────────────────────────
  const form      = document.getElementById("upload-form");
  const input     = document.getElementById("image-input");
  const dropZone  = document.getElementById("drop-zone");
  const submitBtn = document.getElementById("submit-btn");
  const btnText   = document.getElementById("btn-text");
  const btnLoading = document.getElementById("btn-loading");
  const previewContainer = document.getElementById("preview-container");
  const previewImg = document.getElementById("preview-img");
  const previewName = document.getElementById("preview-name");

  // Only run on pages that have the upload form
  if (!form) return;

  // ── 1. Client-side validation & loading spinner ──────────────────────────────
  form.addEventListener("submit", function (event) {
    // Guard: ensure a file has been chosen
    if (!input || !input.files || input.files.length === 0) {
      event.preventDefault();
      showAlert("Please select an image before submitting.");
      return;
    }

    // Guard: check file extension (mirrors server-side allow-list)
    const filename = input.files[0].name.toLowerCase();
    const allowed  = [".png", ".jpg", ".jpeg"];
    const valid    = allowed.some(ext => filename.endsWith(ext));

    if (!valid) {
      event.preventDefault();
      showAlert("Invalid file type. Please choose a PNG, JPG, or JPEG image.");
      return;
    }

    // All good — show the loading state
    showLoading();
  });

  // ── 2. Image preview on file selection ───────────────────────────────────────
  if (input) {
    input.addEventListener("change", function () {
      handleFile(this.files[0]);
    });
  }

  // ── 3. Drag-and-drop support ─────────────────────────────────────────────────
  if (dropZone) {
    // Keyboard "click" support for accessibility (Enter / Space)
    dropZone.addEventListener("keydown", function (e) {
      if (e.key === "Enter" || e.key === " ") {
        e.preventDefault();
        input && input.click();
      }
    });

    // Visual feedback when dragging over the zone
    ["dragover", "dragenter"].forEach(eventName => {
      dropZone.addEventListener(eventName, function (e) {
        e.preventDefault();
        e.stopPropagation();
        dropZone.classList.add("drop-zone--active");
      });
    });

    ["dragleave", "dragend", "drop"].forEach(eventName => {
      dropZone.addEventListener(eventName, function (e) {
        e.preventDefault();
        e.stopPropagation();
        dropZone.classList.remove("drop-zone--active");
      });
    });

    // Handle the actual file drop
    dropZone.addEventListener("drop", function (e) {
      const files = e.dataTransfer && e.dataTransfer.files;
      if (files && files.length > 0) {
        // Transfer the file to the real input so the form picks it up
        try {
          const dataTransfer = new DataTransfer();
          dataTransfer.items.add(files[0]);
          input.files = dataTransfer.files;
        } catch (_) {
          // Fallback — some older browsers don't support DataTransfer()
          // The preview won't update but the file will still be transferred via dataTransfer
        }
        handleFile(files[0]);
      }
    });
  }

  // ── Helper: display an image preview ─────────────────────────────────────────
  function handleFile(file) {
    if (!file || !previewContainer || !previewImg || !previewName) return;

    // Only preview image files
    if (!file.type.startsWith("image/")) return;

    const reader = new FileReader();
    reader.onload = function (e) {
      previewImg.src = e.target.result;
      previewImg.alt = "Preview of " + file.name;
      previewName.textContent = file.name;
      previewContainer.hidden = false;
    };
    reader.readAsDataURL(file);
  }

  // ── Helper: switch the button to its loading state ───────────────────────────
  function showLoading() {
    if (!submitBtn || !btnText || !btnLoading) return;
    btnText.hidden    = true;
    btnLoading.hidden = false;
    submitBtn.disabled = true;
    submitBtn.setAttribute("aria-busy", "true");
  }

  // ── Helper: show a styled alert (falls back to native alert) ─────────────────
  function showAlert(message) {
    // Try to find or create an inline alert element near the form
    let alertEl = document.getElementById("js-alert");
    if (!alertEl) {
      alertEl = document.createElement("div");
      alertEl.id = "js-alert";
      alertEl.style.cssText = [
        "margin-bottom: 1rem",
        "padding: 0.75rem 1.25rem",
        "border-radius: 8px",
        "background: rgba(248,113,113,0.1)",
        "border: 1px solid rgba(248,113,113,0.3)",
        "color: #fca5a5",
        "font-size: 0.875rem",
        "font-weight: 500",
        "display: flex",
        "align-items: center",
        "gap: 0.5rem",
        "animation: fade-in 0.25s ease",
      ].join("; ");
      alertEl.setAttribute("role", "alert");
      alertEl.setAttribute("aria-live", "assertive");
      form.prepend(alertEl);
    }

    alertEl.textContent = "⚠ " + message;

    // Auto-dismiss after 4 seconds
    setTimeout(function () {
      if (alertEl && alertEl.parentNode) {
        alertEl.parentNode.removeChild(alertEl);
      }
    }, 4000);
  }
})();
