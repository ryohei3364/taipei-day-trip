let currentIndex = 0;

const slideshowDiv = document.querySelector('.picture__slideshow');
const pictureDiv = document.querySelector('.picture');
const profileDiv = document.querySelector('.profile__info'); 
const inforsDiv = document.querySelector('.infors');
const leftArrow = document.getElementById('leftArrow');
const rightArrow = document.getElementById('rightArrow');

document.addEventListener("DOMContentLoaded", async function () {
  let id = window.location.pathname.split("/").pop();
  if (id) {
    const attractionData = await getAttraction(id);
    if (attractionData) {
      renderInfo(attractionData);
      renderDots(attractionData.images);
      updatePrice();
    }
  }
});

async function getAttraction(id) {
  try {
    let response = await fetch(`/api/attraction/${id}`);
    let rawData = await response.json();
    if (!rawData.data) throw new Error("API 回傳錯誤");
    return rawData.data;
  } catch (error) {
    return null;
  }
}

async function renderInfo(attractionData) {
  let { name, category, description, address, mrt, transport, images } = attractionData;
  
  slideshowDiv.innerHTML = "";
  profileDiv.innerHTML = "";
  inforsDiv.innerHTML = "";

  slideshowDiv.style.backgroundImage = `url(${images[0]})`;
  slideshowDiv.style.backgroundSize = "cover";
  slideshowDiv.style.backgroundPosition = "center";

  pictureDiv.appendChild(slideshowDiv);

  let nameH3 = document.createElement("h3");
  nameH3.textContent = name;

  let categorySpan = document.createElement("span");
  categorySpan.textContent = `${category} at ${mrt}`

  profileDiv.appendChild(nameH3);
  profileDiv.appendChild(categorySpan);

  let descriptionSpan = document.createElement("span");
  descriptionSpan.textContent = description;

  let addressTitle = document.createElement("p");
  let addressSpan = document.createElement("span");
  addressTitle.textContent = "景點地址：";
  addressTitle.style.fontWeight = "600";
  addressSpan.textContent = address;

  let transportTitle = document.createElement("p");
  let transportSpan = document.createElement("span");
  transportTitle.textContent = "交通方式：";
  transportTitle.style.fontWeight = "600";
  transportSpan.textContent = transport;

  inforsDiv.appendChild(descriptionSpan);
  inforsDiv.appendChild(addressTitle);
  inforsDiv.appendChild(addressSpan);
  inforsDiv.appendChild(transportTitle);
  inforsDiv.appendChild(transportSpan);
}

async function renderDots(images) {
  const dotsContainer = document.createElement("div");
  dotsContainer.classList.add("picture__dot");
  pictureDiv.appendChild(dotsContainer);
  
  dotsContainer.innerHTML = "";

  for (let i = 0; i < images.length; i++) {
    let dotSpan = document.createElement("span");
    dotSpan.classList.add("dot");

    dotSpan.addEventListener('click', () => {
      currentIndex = i;
      changeImage(images[i]);
      updateDots();
    });
    dotsContainer.appendChild(dotSpan);
  }
  rightArrow.addEventListener("click", () => changeSlide(1, images));
  leftArrow.addEventListener("click", () => changeSlide(-1, images));

  currentIndex = 0;
  changeImage(images[currentIndex]);
  updateDots();
}

async function changeImage(imageUrl) {
  let newImage = new Image();
  newImage.onload = () => {
    slideshowDiv.style.backgroundImage = `url(${imageUrl})`;
  };
  newImage.src = imageUrl; 
}

async function changeSlide(direction, images) {
  currentIndex = (currentIndex + direction + images.length) % images.length;
  changeImage(images[currentIndex]);
  updateDots();
}

async function updateDots() {
  const dots = document.querySelectorAll('.dot');
  dots.forEach((dot, index) => {
    if (index === currentIndex) {
      dot.style.backgroundColor = "#757575"; 
      dot.style.border = "solid 1px white";
    } else {
      dot.style.backgroundColor = "";    
      dot.style.border = "";    
    }
  });
}

function updatePrice() {
  const morning = document.querySelector('input[value="morning"]').checked;
  const priceInput = document.getElementById("price");
  const priceText = document.getElementById("money");

  if (morning) {
    priceInput.value = 2000;
    priceText.textContent = "新台幣 2000 元";
  } else {
    priceInput.value = 2500;
    priceText.textContent = "新台幣 2500 元";
  }
}