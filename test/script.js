const API_ENDPOINT = "http://127.0.0.1:8000";
const form = document.getElementById("form");
const loading = document.getElementById("loading");
const complete = document.getElementById("complete");
const closeBtn = document.getElementById("result-close");
const resultBox = document.getElementById("result");
const error = document.getElementById("error");

const stateBox = {
  loading,
  complete,
  error,
};

const toggleBox = (type, visible) => {
  if (!["loading", "complete", "error"].includes(type)) return;
  const box =
    type === "loading" ? loading : type === "complete" ? complete : error;
  box.setAttribute("data-show", visible ? "true" : "false");
};

const isEn = location.pathname.includes("/en.html");

form.addEventListener("submit", (e) => {
  e.preventDefault();
  resultBox.textContent = "";
  error.innerHTML = "";
  toggleBox("error", false);
  toggleBox("loading", true);
  const formData = new FormData(form);

  // dev
  for (var value of formData.values()) {
    console.log(value);
  }

  fetch(`${API_ENDPOINT}/${isEn ? "en" : "ja"}`, {
    method: "POST",
    body: formData,
  })
    .then((res) => {
      console.log("res", res);
      if (!res.ok) {
        let message = "Failed. Please try again.";
        if (res.status === 400) {
          message = isEn
            ? "Detected non safe input."
            : "不適切な入力を検知しました";
        }
        throw new Error(message);
      }
      return res;
    })
    .then((data) => data.blob())
    .then((blob) => URL.createObjectURL(blob))
    .then((url) => {
      const img = new Image();
      img.src = url;
      resultBox.appendChild(img);
      toggleBox("complete", true);
    })
    .catch((err) => {
      error.innerHTML = err;
      toggleBox("error", true);
      setTimeout(() => {
        toggleBox("error", false);
      }, 3000);
    })
    .finally(() => {
      toggleBox("loading", false);
    });
});

closeBtn.addEventListener("click", () => {
  toggleBox("complete", false);
});
complete.addEventListener("click", () => {
  toggleBox("complete", false);
});
error.addEventListener("click", () => {
  toggleBox("error", false);
  error.innerHTML = "";
});
