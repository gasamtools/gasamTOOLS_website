// script.js
document.addEventListener('DOMContentLoaded', function () {
  const togglePasswords = document.querySelectorAll('.toggle-password');
  //const password = document.querySelector('#floatingPassword');

  togglePasswords.forEach(togglePassword => {
      togglePassword.addEventListener('click', function () {
        // Assuming you also need to get the related password input field
        const password = this.previousElementSibling;
        const type = password.getAttribute('type') === 'password' ? 'text' : 'password';
        password.setAttribute('type', type);
        this.querySelector('i').classList.toggle('fa-eye');
        this.querySelector('i').classList.toggle('fa-eye-slash');
      });
    });
});

document.getElementById('gasam-footer-year').textContent = new Date().getFullYear();

function validatePassword() {
  const password = document.getElementById("floatingPassword");
  const confirmPassword = document.getElementById("floatingRepeatPassword");

  if (password.value !== confirmPassword.value) {
    confirmPassword.setCustomValidity("Passwords do not match");
  } else {
    confirmPassword.setCustomValidity("");
  }
}