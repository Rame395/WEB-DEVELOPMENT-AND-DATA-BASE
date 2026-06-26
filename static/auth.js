const container = document.querySelector('.container1');
const registerBtn = document.querySelector('.register-btn');
const loginBtn = document.querySelector('.login-btn');
const loginForm = document.querySelector('.form-box.login');
const registerForm = document.querySelector('.form-box.register');


registerBtn.addEventListener('click', () => {
    container.classList.add('active');
    loginForm.style.display = 'none';
    registerForm.style.display = 'flex';
});

loginBtn.addEventListener('click', () => {
    container.classList.remove('active');
    registerForm.style.display = 'none';
    loginForm.style.display = 'flex';
});

// ================== AUTH.JS ==================
document.addEventListener("DOMContentLoaded", () => {

  // ---------- Toggle password visibility ----------
  document.querySelectorAll(".toggle-password").forEach(icon => {
    icon.addEventListener("click", () => {
      const input = icon.previousElementSibling;
      if (input.type === "password") {
        input.type = "text";
        icon.classList.replace("fa-eye", "fa-eye-slash");
      } else {
        input.type = "password";
        icon.classList.replace("fa-eye-slash", "fa-eye");
      }
    });
  });

  // ---------- Form container toggle ----------
  const container = document.querySelector('.container1');
  const registerBtn = document.querySelector('.register-btn');
  const loginBtn = document.querySelector('.login-btn');
  const loginFormBox = document.querySelector('.form-box.login');
  const registerFormBox = document.querySelector('.form-box.register');

  registerBtn.addEventListener('click', () => {
    container.classList.add('active');
    loginFormBox.style.display = 'none';
    registerFormBox.style.display = 'flex';
  });

 



  // ---------- REGISTER FORM ----------
  const registerForm = document.getElementById("demo-form");
  const registerPwdInput = registerForm.querySelector("input[name='password2']");
  const registerConfirmInput = registerForm.querySelector("input[name='confirmPassword']");
  const pwdBar = document.getElementById("pwdBar");
  const pwdHint = document.getElementById("pwdHint");

  // ---------- PASSWORD STRENGTH LIVE ----------
  if (registerPwdInput) {
    registerPwdInput.addEventListener("input", () => {
      const val = registerPwdInput.value;
      let strength = 0;

      if (val.length >= 8) strength++;
      if (/[A-Za-z]/.test(val)) strength++;
      if (/\d/.test(val)) strength++;
      if (/[^A-Za-z0-9]/.test(val)) strength++;

      const percent = strength * 25;
      pwdBar.style.width = percent + "%";

      if (strength <= 1) {
        pwdBar.className = "progress-bar bg-danger";
        pwdHint.textContent = "Weak password";
        registerPwdInput.classList.add("is-invalid");
        registerPwdInput.classList.remove("is-valid");
      } else if (strength === 2) {
        pwdBar.className = "progress-bar bg-warning";
        pwdHint.textContent = "Medium password";
        registerPwdInput.classList.add("is-invalid");
        registerPwdInput.classList.remove("is-valid");
      } else {
        pwdBar.className = "progress-bar bg-success";
        pwdHint.textContent = "Strong password";
        registerPwdInput.classList.add("is-valid");
        registerPwdInput.classList.remove("is-invalid");
      }
    });
  }



  // ---------- DEVICE INFO ----------
  document.querySelectorAll('input[name="device_info"]').forEach(el => el.value = navigator.userAgent);

  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(pos => {
      document.getElementById('user_lat').value = pos.coords.latitude;
      document.getElementById('user_lon').value = pos.coords.longitude;
    });
  }

});




 