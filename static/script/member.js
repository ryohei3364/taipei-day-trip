const signinButton = document.querySelector('.menu__item--container--user');
const signoutButton = document.querySelector('.menu__item--container--signout');
const signInDialog = document.getElementById('signInDialog');
const signUpDialog = document.getElementById('signUpDialog');
const closeButtons = document.querySelectorAll('.close');
const token = localStorage.getItem("token");

function updateUI(token) {
  signinButton.style.display = token ? "none" : "block";
  signoutButton.style.display = token ? "block" : "none";
}

async function checkUserInfo() {
  if (token) {
    const response = await fetch("/api/user/auth", { 
      method: "GET",
      headers: {
        "Authorization": `Bearer ${token}`,
        "Content-Type": "application/json"
      }
    });
    const user = await response.json();
    if (user) {
      updateUI(true);
    } else {
      localStorage.removeItem("token");
      updateUI(false);
    }
  }
}

async function login(event) {
  event.preventDefault();
  const email = document.getElementById("email").value;
  const password = document.getElementById("password").value;

  const response = await fetch('/api/user/auth', {
    method: "PUT",
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({ email, password })
  });

  const result = await response.json();
  if (response.ok) {
    localStorage.setItem("token", result.token);
    document.getElementById("message").textContent = result.message;
    updateUI(true);
    signInDialog.close();
  } else {
    document.getElementById("message").textContent = result.message;
  }
}

async function signUp(event) {
  event.preventDefault();
  const name = document.getElementById("signUp_name").value;
  const email = document.getElementById("signUp_email").value;
  const password = document.getElementById("signUp_password").value;

  const response = await fetch('/api/user', {
    method: "POST",
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({ name, email, password })
  });

  const result = await response.json();
  if (response.ok) {
    document.getElementById("signUp_message").textContent = result.message;
  } else {
    document.getElementById("signUp_message").textContent = result.message;
  }
}

signoutButton.addEventListener("click", () => {
  localStorage.removeItem("token");
  updateUI(false);
});

signinButton.addEventListener("click", () => {
  signUpDialog.close();
  signInDialog.showModal();
});

function switchToSignUp() {
  signInDialog.close();
  signUpDialog.showModal();
}

function switchToSignIn() {
  signUpDialog.close();
  signInDialog.showModal();
}

closeButtons.forEach((btn) => {
  btn.addEventListener("click", (event) => {
    event.target.closest("dialog").close();
  });
});

updateUI(token);
checkUserInfo();