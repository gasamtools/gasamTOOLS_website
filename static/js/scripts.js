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

document.addEventListener("DOMContentLoaded", function() {
    document.getElementById('gasam-footer-year').textContent = new Date().getFullYear();
});

function validatePassword(password1, password2) {
  const password = document.getElementById(password1);
  const confirmPassword = document.getElementById(password2);

  if (password.value !== confirmPassword.value) {
    confirmPassword.setCustomValidity("Passwords do not match");
  } else {
    confirmPassword.setCustomValidity("");
  }
}

document.addEventListener("DOMContentLoaded", () => {
    const element = document.querySelector('#gasamProfileSaveChangesBttn');
    if (element) {
        document.getElementById('gasamProfileSaveChangesBttn').addEventListener('click', function(event) {
            event.preventDefault(); // Prevent the form from submitting the traditional way
            var csrfToken = $('meta[name="csrf-token"]').attr('content');

            name_val = $('#gasamProfileUserName').val();
            const password = $('#profilePassword').get(0);
            const password_val = $('#profilePassword').val();

            if (!password_val) {
                password.setCustomValidity("Field is empty");
                password.reportValidity(); // Display the validation message
            } else {

                const formObject = {
                    'js_function': 'profile_page',
                    'user_password': password_val,
                    'user_name': name_val
                };

                fetch(GASAM_profile_js_URL, {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json' ,
                        'X-CSRFToken': csrfToken  // Include the CSRF token in the headers
                    },
                    body: JSON.stringify(formObject)
                })
                .then(response => response.json())
                .then(data => {
                    if (!data['correct_password']) {
                        password.setCustomValidity("Wrong password");
                        password.reportValidity(); // Display the validation message
                    } else {
                        var modalElement = document.getElementById('exampleModal');
                        var modal = bootstrap.Modal.getInstance(modalElement);
                        modal.hide();
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                });
            }
        });
    }
});