// 🎯 Toggle menú desplegable del usuario
document.addEventListener("DOMContentLoaded", () => {
  const btn = document.getElementById("userDropdownBtn");
  const menu = document.getElementById("userDropdownMenu");

  if (btn && menu) {
    btn.addEventListener("click", () => {
      menu.classList.toggle("show");
    });

    // Cerrar el menú si se hace clic fuera
    document.addEventListener("click", (e) => {
      if (!btn.contains(e.target) && !menu.contains(e.target)) {
        menu.classList.remove("show");
      }
    });
  }
});
