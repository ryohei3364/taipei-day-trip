const signinButton = document.querySelector('.menu__item--container--user');
const signoutButton = document.querySelector('.menu__item--container--signout');
const signInDialog = document.getElementById('signInDialog');
const signUpDialog = document.getElementById('signUpDialog');
const closeButtons = document.querySelectorAll('.close');
const dateInput = document.getElementById('date');
const navBookingBtn = document.querySelector('.menu__item--container--booking');

signinButton.style.display = "none";

if (dateInput) {
  const today = new Date().toISOString().split('T')[0];
  dateInput.value = today;
}

function updateUI(token) {
  signinButton.style.display = token ? "none" : "block";
  signoutButton.style.display = token ? "block" : "none";
}

async function checkUserInfo() {
  const token = localStorage.getItem("token");
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
      console.log(user);
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
  // 首先檢查用戶是否已經登入
  if (!await checkUserInfo()) {
    signInDialog.showModal();
    return;
  }
  const attractionId = window.location.pathname.split("/").pop();
  const date = document.getElementById("date").value;
  const time = document.querySelector('input[name="time"]:checked').value;
  const price = document.getElementById("price").value;
  console.log(attractionId, date, time, price)

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
  console.log(result);
}

navBookingBtn.addEventListener('click', handleBookingRedirect);

// // 原本 GET 獲取表單寫法
// async function booking(event) {
//   event.preventDefault();
//   const date = document.getElementById("date").value;
//   const time = document.querySelector('input[name="time"]:checked').value;
//   const price = document.getElementById("price").value;
//   const attractionId = window.location.pathname.split("/").pop();
//   console.log(date, time, price, attractionId)

//   // GET method 無法加上body
//   const response = await fetch(`/api/booking?date=${date}&time=${time}&price=${price}&attractionId=${attractionId}`, {
//     method: "GET",
//     headers: {
//       'Content-Type': 'application/json',
//       'Authorization': `Bearer ${token}`,
//     },
//   });
//   const result = await response.json();
//   console.log(result)
// }

// // 在表單提交前檢查用戶狀態
// async function checkUserAndSubmit(event) {
//   event.preventDefault();  // 阻止表單的默認提交行為
//   const isUserAuthenticated = await checkUserInfo();

//   if (isUserAuthenticated) {
//     // 如果用戶已經登入，允許提交表單
//     document.getElementById("profile__booking--form").submit();
//   } else {
//     // 如果用戶未登入，顯示提示並阻止表單提交
//     signInDialog.showModal();  // 顯示登入對話框
//   }
// }

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

// updateUI(token);
checkUserInfo();