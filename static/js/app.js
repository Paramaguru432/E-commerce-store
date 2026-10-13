(function () {
  'use strict';

  document.querySelectorAll('.message-close').forEach(function (button) {
    button.addEventListener('click', function () {
      var message = button.closest('.message');
      if (message) message.remove();
    });
  });

  var menuButton = document.querySelector('.menu-toggle');
  var nav = document.querySelector('.nav-links');
  if (menuButton && nav) {
    menuButton.addEventListener('click', function () {
      var isOpen = nav.classList.toggle('nav-open');
      menuButton.setAttribute('aria-expanded', String(isOpen));
      menuButton.setAttribute('aria-label', isOpen ? 'Close menu' : 'Open menu');
      menuButton.textContent = isOpen ? '×' : '☰';
    });
  }

  document.querySelectorAll('input[type="number"][max]').forEach(function (input) {
    input.addEventListener('change', function () {
      var max = Number(input.max);
      var min = input.min ? Number(input.min) : 0;
      var value = Number(input.value);
      if (Number.isFinite(max) && value > max) input.value = String(max);
      if (Number.isFinite(min) && value < min) input.value = String(min);
    });
  });
})();
