document.addEventListener("DOMContentLoaded", () => {
  const continueBtn = document.getElementById("continueBtn");
  const skipBtn = document.getElementById("skipBtn");

  continueBtn.addEventListener("click", () => {
    // Va a la prueba de cámara
    window.location.href = "/api/object_game/camera-test/";
  });

  skipBtn.addEventListener("click", () => {
    // Salta directamente al juego
    window.location.href = "/api/object_game/start/";
  });
});
