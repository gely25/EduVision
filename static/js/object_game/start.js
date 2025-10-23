document.addEventListener("DOMContentLoaded", () => {
  const btnStart = document.getElementById("btnStart");

  btnStart.addEventListener("click", () => {
    // Redirigir al juego real (detección)
    window.location.href = "/api/vision/live/";
  });
});
