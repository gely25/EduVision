document.addEventListener("DOMContentLoaded", () => {
  const frameImg = document.getElementById("tm-frame");
  const instruccion = document.getElementById("instruccion");
  const feedback = document.getElementById("feedback");
  const scoreDisplay = document.getElementById("score");
  const finishBtn = document.getElementById("finishBtn");
  const startCameraBtn = document.getElementById("startCameraBtn");
  const nextBtn = document.getElementById("nextBtn");
  const cameraInactive = document.getElementById("cameraInactive");
  const statusBadge = document.getElementById("statusBadge");
  const statusText = document.getElementById("statusText");

  let score = 0;
  let idx = 0;
  let jugando = false;
  let cameraActive = false;
  const total = Array.isArray(palabrasJuego) ? palabrasJuego.length : 0;
  const puntosPorAcierto = 10;

  let frameInterval = null;
  let detectInterval = null;

  // =====================================================
  // 1️⃣ Inicializa instrucción
  // =====================================================
  if (total === 0) {
    instruccion.textContent = "No hay palabras para jugar 😅";
    feedback.textContent = "Vuelve a /api/object_game/start/ para cargar palabras.";
    startCameraBtn.style.display = "none";
    return;
  }

  instruccion.textContent = `📚 Muéstrame un ${palabrasJuego[idx]} 🧠`;

  // =====================================================
  // 2️⃣ Activar cámara manualmente
  // =====================================================
  startCameraBtn.addEventListener("click", async () => {
    try {
      const res = await fetch("/api/vision/tm/start/");
      if (!res.ok) throw new Error("No se pudo iniciar la cámara");

      cameraActive = true;
      jugando = true;

      // Mostrar cámara
      cameraInactive.style.display = "none";
      frameImg.style.display = "block";
      statusBadge.style.display = "flex";
      statusBadge.classList.add("active");
      statusText.textContent = "En vivo";

      // Inicia intervalos
      frameInterval = setInterval(actualizarFrame, 800);
      detectInterval = setInterval(verificarDeteccion, 1500);

      // Verificación si no llega imagen
      setTimeout(() => {
        if (!frameImg.src || frameImg.src === "") {
          alert("⚠️ No se detectó la cámara. Permite el acceso y recarga la página.");
        }
      }, 4000);

    } catch (error) {
      console.error("❌ Error al iniciar cámara:", error);
      alert("No se pudo acceder a la cámara 😢");
    }
  });

  // =====================================================
  // 3️⃣ Actualizar frame del servidor
  // =====================================================
  function actualizarFrame() {
    if (!cameraActive) return;

    fetch("/api/vision/tm/frame/")
      .then(res => res.json())
      .then(data => {
        const frame = data.frame || data.image;
        if (frame) {
          frameImg.src = frame.startsWith("data:")
            ? frame
            : `data:image/jpeg;base64,${frame}`;
        }
      })
      .catch(() => {});
  }

  // =====================================================
  // 4️⃣ Verificar detección
  // =====================================================
  function verificarDeteccion() {
    if (!jugando || !cameraActive) return;

    fetch("/api/object_game/detect/")
      .then(res => res.json())
      .then(data => {
        if (data && data.label) procesarEtiqueta(data.label);
      })
      .catch(() => {});
  }

  // =====================================================
  // 5️⃣ Procesar etiqueta detectada
  // =====================================================
  function procesarEtiqueta(label) {
    const esperado = String(palabrasJuego[idx]).toLowerCase().trim();
    const detectado = String(label).toLowerCase().trim();

    if (!esperado) return;

    if (detectado !== "no reconocido" && detectado.includes(esperado)) {
      score += puntosPorAcierto;
      scoreDisplay.textContent = score;
      feedback.innerHTML = `✅ ¡Correcto! Era <strong>${esperado}</strong>`;
      feedback.style.color = "#10b981";

      detenerCamaraTemporal();

      idx++;
      if (idx >= total) {
        terminarJuego();
      } else {
        instruccion.textContent = `📚 Muéstrame un ${palabrasJuego[idx]} 🧠`;
        nextBtn.style.display = "inline-block";
      }

    } else if (detectado !== "no reconocido") {
      feedback.innerHTML = `❌ Mostraste "<strong>${detectado}</strong>". Intenta otra vez.`;
      feedback.style.color = "#f87171";
    } else {
      feedback.innerHTML = "⏳ Aún no reconozco el objeto…";
      feedback.style.color = "#e0e7ff";
    }
  }

  // =====================================================
  // 6️⃣ Detener cámara temporalmente tras acierto
  // =====================================================
  async function detenerCamaraTemporal() {
    try {
      await fetch("/api/vision/tm/stop/");
    } catch (e) {
      console.warn("⚠️ No se pudo detener la cámara temporalmente");
    }

    cameraActive = false;
    clearInterval(frameInterval);
    clearInterval(detectInterval);

    frameImg.style.display = "none";
    statusBadge.style.display = "none";
    cameraInactive.style.display = "flex";
    cameraInactive.querySelector("p").textContent = "Presiona 'Activar cámara' cuando estés listo para el siguiente objeto 📷";
  }

  // =====================================================
  // 7️⃣ Siguiente objeto
  // =====================================================
  nextBtn.addEventListener("click", () => {
    nextBtn.style.display = "none";
    feedback.textContent = "";
    cameraInactive.querySelector("p").textContent = "Activa tu cámara para mostrar el siguiente objeto 📚";
  });

  // =====================================================
  // 8️⃣ Terminar partida
  // =====================================================
  function terminarJuego() {
    jugando = false;
    cameraActive = false;
    clearInterval(frameInterval);
    clearInterval(detectInterval);

    instruccion.textContent = "🏁 ¡Has terminado!";
    feedback.innerHTML = `Tu puntaje final es <strong>${score}</strong> de ${total * puntosPorAcierto}`;
    finishBtn.style.display = "inline-block";
    nextBtn.style.display = "none";
  }

  // =====================================================
  // 9️⃣ Botón para finalizar
  // =====================================================
  finishBtn.addEventListener("click", async () => {
    try {
      await fetch("/api/vision/tm/stop/");
    } catch (_) {}
    window.location.href = "/api/object_game/result/";
  });
});
