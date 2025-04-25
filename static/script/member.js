const ordersContainer = document.getElementById('orders-container');
const signoutButton = document.querySelector('.menu__item--container--signout');
const usernameText = document.getElementById('member--username');
const paidText = document.getElementById('paid-count');
const unpaidText = document.getElementById('unpaid-count');

signoutButton.addEventListener("click", () => {
  localStorage.removeItem("token");
  window.location.href = "/";
  updateUI(false);
});

async function renderOrders() {
  const token = localStorage.getItem("token");
  if (token) {
    const [userResponse, orderResponse] = await Promise.all([
      fetch("/api/user/auth", {
        method: "GET",
        headers: {
          "Authorization": `Bearer ${token}`,
          "Content-Type": "application/json"
        }
      }),
      fetch("/api/orders", {
        method: "GET",
        headers: {
          "Authorization": `Bearer ${token}`,
          "Content-Type": "application/json"
        }
      })
    ]);
    const userRes = await userResponse.json();
    const ordersRes = await orderResponse.json();

    if (userRes?.data) {
      usernameText.textContent = userRes.data.name;
    } 
    if (ordersRes?.data) {
      paidText.textContent = ordersRes.order_paid;
      unpaidText.textContent = ordersRes.order_unpaid;
      paidText.style.color = 'green';
      unpaidText.style.color = 'red';
      
      ordersRes.data.forEach(order => {
        const statusClass = order.status === 0 ? 'paid' : 'unpaid';
        const statusText = order.status === 0 ? '已付款' : '未付款';

        const card = document.createElement("div");
        card.classList.add("order-card");

        const header = document.createElement("div");
        header.classList.add("order-header");

        const left = document.createElement("div");

        const numberSpan = document.createElement("span");
        numberSpan.classList.add("order-number");
        numberSpan.textContent = `訂單編號：${order.orderNumber}`;

        const dateSpan = document.createElement("span");
        dateSpan.classList.add("order-date");
        dateSpan.textContent = order.date;

        left.appendChild(numberSpan);
        left.appendChild(dateSpan);

        const statusSpan = document.createElement("span");
        statusSpan.classList.add("order-status", statusClass);
        statusSpan.textContent = statusText;

        header.appendChild(left);
        header.appendChild(statusSpan);

        const body = document.createElement("div");
        body.classList.add("order-body");

        const info = document.createElement("div");
        info.classList.add("order-info");

        const timeP = document.createElement("p");
        timeP.textContent = `時間：${order.time}`;

        const contactNameP = document.createElement("p");
        contactNameP.textContent = `聯絡人：${order.contactName}`;

        const emailP = document.createElement("p");
        emailP.textContent = `Email：${order.contactEmail}`;

        const phoneP = document.createElement("p");
        phoneP.textContent = `電話：${order.contactPhone}`;

        const createdP = document.createElement("p");
        createdP.textContent = `建立時間：${new Date(order.orderTime).toLocaleString()}`;

        info.append(timeP, contactNameP, emailP, phoneP, createdP);
        body.appendChild(info);

        card.appendChild(header);
        card.appendChild(body);

        ordersContainer.appendChild(card);
      });
    }
  }
}  
renderOrders();