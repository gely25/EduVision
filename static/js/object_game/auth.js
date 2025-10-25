// ========================================
// ANIMACIÓN DEL OSITO/PERSONAJE - EduVision
// ========================================

document.addEventListener('DOMContentLoaded', function() {
  const passwordInputs = document.querySelectorAll('input[type="password"]');
  const bearEyes = document.querySelector('.bear-eyes');
  const bearHands = document.querySelectorAll('.bear-hand');
  
  if (!bearEyes || bearHands.length === 0) {
    console.warn('Elementos del personaje no encontrados');
    return;
  }

  // Función para cubrir los ojos
  function coverEyes() {
    bearEyes.classList.add('closed');
    bearHands.forEach(hand => hand.classList.add('cover'));
  }

  // Función para destapar los ojos
  function uncoverEyes() {
    bearEyes.classList.remove('closed');
    bearHands.forEach(hand => hand.classList.remove('cover'));
  }

  // Eventos para campos de contraseña
  passwordInputs.forEach(input => {
    // Al hacer foco, cubre los ojos
    input.addEventListener('focus', coverEyes);
    
    // Al salir del campo, solo destapa si está vacío
    input.addEventListener('blur', function() {
      if (!this.value) {
        uncoverEyes();
      }
    });

    // Mientras escribe
    input.addEventListener('input', function() {
      if (this.value.length > 0) {
        coverEyes();
      } else {
        uncoverEyes();
      }
    });
  });

  // Verificar si ya hay valores al cargar (por ejemplo, autocompletado)
  passwordInputs.forEach(input => {
    if (input.value && input.value.length > 0) {
      coverEyes();
    }
  });
});