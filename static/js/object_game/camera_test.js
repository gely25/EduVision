document.addEventListener("DOMContentLoaded", () => {
  const video = document.getElementById("preview");
  const continueBtn = document.getElementById("continueBtn");
  const skipBtn = document.getElementById("skipBtn");
  const statusText = document.getElementById("cameraStatus");

  let camaraLista = false;

  // Estado inicial: botón desactivado
  continueBtn.disabled = true;
  continueBtn.style.opacity = "0.6";
  continueBtn.style.cursor = "not-allowed";
  statusText.textContent = "⚠️ Esperando acceso a cámara...";

  async function iniciarCamara() {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: true });
      video.srcObject = stream;
      camaraLista = true;

      // ✅ Actualizar interfaz
      statusText.textContent = "✅ Cámara detectada correctamente";
      statusText.style.color = "#16a34a"; // verde
      continueBtn.disabled = false;
      continueBtn.style.opacity = "1";
      continueBtn.style.cursor = "pointer";

    } catch (err) {
      camaraLista = false;
      console.error("Error de cámara:", err);

      // ⚠️ Mostrar mensaje visual, sin usar alert
      statusText.textContent = "❌ No se pudo acceder a la cámara. Verifica los permisos en tu navegador.";
      statusText.style.color = "#dc2626"; // rojo

      continueBtn.disabled = true;
      continueBtn.style.opacity = "0.6";
      continueBtn.style.cursor = "not-allowed";
    }
  }

  iniciarCamara();

  continueBtn.addEventListener("click", () => {
    if (!camaraLista) {
      alert("La cámara no está lista. Actívala para continuar 📷");
      return;
    }
    window.location.href = "/api/object_game/start/";
  });

  skipBtn.addEventListener("click", () => {
    window.location.href = "/api/object_game/start/";
  });
});
