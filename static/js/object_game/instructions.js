document.addEventListener("DOMContentLoaded", () => {
  const continueBtn = document.getElementById("continueBtn");
  const skipBtn = document.getElementById("skipBtn");

  // Continuar → va a la siguiente etapa (3/5)
  continueBtn.addEventListener("click", () => {
    window.location.href = "/api/object_game/rules/";
  });

  // Saltar → va directo al inicio del juego
  skipBtn.addEventListener("click", () => {
    window.location.href = "/api/object_game/start/";
  });
});
