let page = 0;
let keyword = null;
let observer = null;
let isLoading = false;

const attractionsDiv = document.querySelector('.attractions');
const listcontainerDiv = document.querySelector('.list__container');
const searchBox = document.getElementById('searchBox');
const searchIcon = document.getElementById('searchIcon');
const leftScroll = document.getElementById('leftScroll');
const rightScroll = document.getElementById('rightScroll');

searchIcon.addEventListener('click', getSearch)
searchBox.addEventListener('keydown', (event) => {
  if (event.key === 'Enter') {
    event.preventDefault();
    isLoading = false; 
    getSearch();
  }
});

function getSearch() {
  let searchKeyword = searchBox.value.trim();
  page = 0;
  keyword = searchKeyword;

  // 淡出舊資料
  attractionsDiv.classList.add("fade-out");

  setTimeout(() => {
    attractionsDiv.innerHTML = '';
    isLoading = false;
    loadAttractions();
    attractionsDiv.classList.remove("fade-out");
  }, 300); // 等淡出動畫結束再載入新資料
}

async function getAttractions(page, keyword){
  let url = `/api/attractions?page=${page}`;
  if (keyword) url += `&keyword=${encodeURIComponent(keyword)}`;
  
  let response = await fetch(url);
  let rawData = await response.json();

  let nextPage = rawData?.nextPage;
  let data = rawData.data;
  return { nextPage, data };
}

async function loadAttractions() {
  isLoading = true;
  // 🟡 顯示骨架畫面
  showSkeletons(6); // 可根據螢幕寬度顯示幾個

  // await new Promise(resolve => setTimeout(resolve, 10000)); // 模擬延遲
  let { nextPage, data } = await getAttractions(page, keyword);

  // 🔴 移除骨架畫面
  removeSkeletons();
  
  for (let i = 0; i < data.length; i++) {
    let attractionDiv = document.createElement("div");
    attractionDiv.classList.add("attractions__card");
    attractionDiv.id = `attraction-${data[i].id}`;
  
    attractionDiv.style.backgroundImage = `url(${data[i].images})`;
    attractionDiv.style.backgroundSize = "cover";
    attractionDiv.style.backgroundPosition = "center";

    attractionDiv.addEventListener("click", () => {
      window.location.assign(`/attraction/${data[i].id}`);
    });
  
    let nameDiv = document.createElement("div");
    nameDiv.classList.add("attractions__card--overlay--name");
    nameDiv.textContent = data[i].name;
  
    let mrtDiv = document.createElement("div");
    mrtDiv.classList.add("attractions__card--info--mrt");
    mrtDiv.textContent = data[i].mrt;
  
    let categoryDiv = document.createElement("div");
    categoryDiv.classList.add("attractions__card--info--category");
    categoryDiv.textContent = data[i].category;
  
    let overlayDiv = document.createElement("div");
    overlayDiv.classList.add("attractions__card--overlay");
    overlayDiv.appendChild(nameDiv);
  
    let infoDiv = document.createElement("div");
    infoDiv.classList.add("attractions__card--info");
    infoDiv.appendChild(mrtDiv);
    infoDiv.appendChild(categoryDiv);
  
    attractionDiv.appendChild(overlayDiv);
    attractionDiv.appendChild(infoDiv);

    attractionsDiv.appendChild(attractionDiv);
  }
  page = nextPage;
  isLoading = false;

  if (page !== null) observeLastCard();
}

function showSkeletons(count) {
  for (let i = 0; i < count; i++) {
    const skeleton = document.createElement("div");
    skeleton.classList.add("skeleton-card");
    skeleton.classList.add("skeleton-temp"); // 加這個方便移除
    attractionsDiv.appendChild(skeleton);
  }
}

function removeSkeletons() {
  const skeletons = document.querySelectorAll(".skeleton-temp");
  skeletons.forEach(s => s.remove());
}

function observeLastCard() {
  let allCards = document.querySelectorAll(".attractions__card");
  if (!allCards.length || isLoading) return;

  let lastCard = allCards[allCards.length - 1];
  if (observer) observer.disconnect();
  
  let options = {
    root: null,
    rootMargin: "0px",
    threshold: 1.0,
  };
  observer = new IntersectionObserver(entries => {
    if (entries[0].isIntersecting && !isLoading) {
      observer.unobserve(lastCard);
      loadAttractions();
    }
  }, options);
  observer.observe(lastCard);
}

async function getMrts(){
  let url = "/api/mrts";
  let response = await fetch(url);
  let rawData = await response.json();

  for (let station of rawData.data) { 
    const stationsDiv = document.createElement('div');
    stationsDiv.classList.add('list__container--station');
    stationsDiv.textContent = station;
    listcontainerDiv.appendChild(stationsDiv);
  }
  const listStationDiv = document.querySelectorAll('.list__container--station');
  for (let i=0;i<listStationDiv.length;i++){
    let stationDiv = listStationDiv[i];
    stationDiv.addEventListener('click', ()=>{
      keyword = stationDiv.textContent;
      searchBox.value = keyword;
      attractionsDiv.innerHTML = '';
      isLoading = false; 
      getSearch();
    });
  }
}

function loadMrts(station) {
  const stationsDiv = document.createElement('div');
  stationsDiv.classList.add('list__container--station');
  stationsDiv.textContent = station;
  listcontainerDiv.appendChild(stationsDiv);
}

leftScroll.addEventListener('click', () => {
  listcontainerDiv.scrollBy({ left: -30, behavior: 'smooth' });
});
rightScroll.addEventListener('click', () => {
  listcontainerDiv.scrollBy({ left: 30, behavior: 'smooth' });
});

loadAttractions();
getMrts();