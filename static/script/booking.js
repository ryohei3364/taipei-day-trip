const greeting = document.querySelector('.booking--greeting');
const container = document.querySelector('.booking--container');
const allDividers = document.querySelectorAll('.booking--divider');
const allWrappers = document.querySelectorAll('.booking--wrapper');
const usernameText = document.getElementById('booking--username');
const usernameInput = document.getElementById('booking--input--username');
const imageUrl = document.getElementById('booking--image');
const nameText = document.getElementById('booking--name');
const dateText = document.getElementById('booking--date');
const timeText = document.getElementById('booking--time');
const priceText = document.getElementById('booking--price');
const addressText = document.getElementById('booking--address');
const emailText = document.getElementById('booking--input--email');
const sumText = document.getElementById('booking--sum');
const deleteButton = document.getElementById('deleteButton');

deleteButton.addEventListener('click', async () => {
  const response = await fetch("/api/booking", { 
    method: "DELETE",
    headers: {
      "Authorization": `Bearer ${token}`,
      "Content-Type": "application/json"
    }
  });
  const result = await response.json();
  location.reload();
});

async function renderBooking() {
  const token = localStorage.getItem("token");
  if (token) {
    const [userResponse, bookingResponse] = await Promise.all([
      fetch("/api/user/auth", {
        method: "GET",
        headers: {
          "Authorization": `Bearer ${token}`,
          "Content-Type": "application/json"
        }
      }),
      fetch("/api/booking", {
        method: "GET",
        headers: {
          "Authorization": `Bearer ${token}`,
          "Content-Type": "application/json"
        }
      })
    ]);
    const user = await userResponse.json();
    const result = await bookingResponse.json();
    // console.log(user.data)
    // console.log(result.data.attraction)

    if (user.data.name) {
      usernameText.textContent = user.data.name;
      usernameInput.value = user.data.name;
      emailText.value = user.data.email;
    } 
    if (result.data && result.data.attraction) {
      imageUrl.style.backgroundImage = `url(${result.data.attraction.image})`;
      nameText.textContent = result.data.attraction.name;
      addressText.textContent = result.data.attraction.address;
      dateText.textContent = result.data.date;
      timeText.textContent = result.data.time;
      priceText.textContent = result.data.price;
      sumText.textContent = result.data.price; 
    } else {
      container.innerHTML="";

      allDividers.forEach(divider => divider.remove());
      for (let i = 1; i < allWrappers.length; i++) {
        allWrappers[i].remove();
      }
      const notice = document.createElement('div');
      notice.classList.add('booking--notice');
      notice.textContent = "目前沒有任何待預訂的行程";    
      greeting.appendChild(notice);
    }
  } else {
    window.location.href = "/"; 
  }
}      

renderBooking();