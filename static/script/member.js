const signinButton = document.querySelector('.menu__item--container--user');
const signoutButton = document.querySelector('.menu__item--container--signout');
const signInDialog = document.getElementById('signInDialog');
const signUpDialog = document.getElementById('signUpDialog');
const closeButtons = document.querySelectorAll('.close');
const navBookingBtn = document.querySelector('.menu__item--container--booking');
const dateInput = document.getElementById('date');
const token = localStorage.getItem("token");

signinButton.style.display = "none";

const today = new Date().toISOString().split('T')[0];
dateInput.value = today;

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
      return true;
    } else {
      localStorage.removeItem("token");
      updateUI(false);
      return false;
    }
  } else {
    updateUI(false);
    return false;
  }
}

async function handleBookingRedirect() {
  if (await checkUserInfo()) {
    window.location.href = "/booking";
  } else {
    signInDialog.showModal();
  }
}

async function formBooking(event) {
  event.preventDefault();
  if (!await checkUserInfo()) {
    signInDialog.showModal();
    return;
  }
  const attractionId = window.location.pathname.split("/").pop();
  const date = document.getElementById("date").value;
  const time = document.querySelector('input[name="time"]:checked').value;
  const price = document.getElementById("price").value;

  if (!date || !time || !price) return;

  const response = await fetch('/api/booking', {
    method: "POST",
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
    body: JSON.stringify({ attractionId, date, time, price })
  });
  const result = await response.json();
  window.location.href = "/booking"; 
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
    location.reload(); 
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
  window.location.reload();
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
navBookingBtn.addEventListener('click', handleBookingRedirect);