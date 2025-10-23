document.addEventListener("DOMContentLoaded", () => {
  const continueBtn = document.getElementById("continueBtn");
  const skipBtn = document.getElementById("skipIntro");

  continueBtn.addEventListener("click", () => {
    window.location.href = "/api/object_game/instructions/";
  });

  skipBtn.addEventListener("click", () => {
    window.location.href = "/api/object_game/start/";
  });
});
