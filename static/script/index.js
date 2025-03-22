let page = 0;
let keyword = null;
let observer = null;

const attractionsDiv = document.querySelector('.attractions');
const listcontainerDiv = document.querySelector('.list__container');
const searchBox = document.getElementById('searchBox');
const searchIcon = document.getElementById('searchIcon');

function getSearch() {
  let searchKeyword = searchBox.value.trim();
  console.log(searchKeyword);
  page = 0;
  keyword = searchKeyword;
  attractionsDiv.innerHTML = '';
  loadAttractions();
}

searchIcon.addEventListener('click', getSearch)
searchBox.addEventListener('keydown', (event) => {
  if (event.key === 'Enter') {
    event.preventDefault(); 
    getSearch();
  }
});

async function getAttractions(page, keyword){
  let url = `/api/attractions?page=${page}`;

  if (keyword) {
    url += `&keyword=${encodeURIComponent(keyword)}`;
  }
  let response = await fetch(url, { method: "GET" });
  let rawData = await response.json();

  let nextPage = rawData.nextPage;
  let spotsName = [];
  let spotsCategory = [];
  let spotsMrt = [];
  let spotsImage = [];

  for(let i=0;i<rawData.data.length;i++){
    spotsName.push(rawData.data[i].name);
    spotsCategory.push(rawData.data[i].category);
    spotsMrt.push(rawData.data[i].mrt);
    spotsImage.push(rawData.data[i].images);
  }
  return { nextPage, data:{ spotsName, spotsCategory, spotsMrt, spotsImage }};
}

async function loadAttractions() {
  if (page === null) return;

  let { nextPage, data } = await getAttractions(page, keyword);

  for (let i = 0; i < data.spotsName.length; i++) {
    let attractionDiv = document.createElement("div");
    attractionDiv.classList.add("attractions__card");

    attractionDiv.style.backgroundImage = `url(${data.spotsImage[i][0]})`;
    attractionDiv.style.backgroundSize = "cover";
    attractionDiv.style.backgroundPosition = "center";

    let nameDiv = document.createElement("div");
    nameDiv.classList.add("attractions__card--overlay--name");
    nameDiv.textContent = data.spotsName[i];

    let mrtDiv = document.createElement("div");
    mrtDiv.classList.add("attractions__card--info--mrt");
    mrtDiv.textContent = data.spotsMrt[i];

    let categoryDiv = document.createElement("div");
    categoryDiv.classList.add("attractions__card--info--category");
    categoryDiv.textContent = data.spotsCategory[i];

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
  observeLastCard();
}

async function observeLastCard() {
  let allCards = document.querySelectorAll(".attractions__card");
  if (allCards.length === 0) return;

  let lastCard = allCards[allCards.length - 1];
  if (observer) {
    observer.disconnect();
  }
  let options = {
    root: null,
    rootMargin: "0px",
    threshold: 1.0,
  };
  observer = new IntersectionObserver(entries => {
    if (entries[0].isIntersecting) {
      observer.unobserve(lastCard);
      loadAttractions();
      
      setTimeout(() => {
        observeLastCard();
      }, 500);
    }
  }, options);
  observer.observe(lastCard);
}

async function getMrts(){
  let url = "/api/mrts";
  let response = await fetch(url, { method: "GET" });
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
      page = 0;
      keyword = stationDiv.textContent;
      searchBox.value = stationDiv.textContent;
      attractionsDiv.innerHTML = '';
      loadAttractions(); 
    });
  }
}

function loadMrts(station) {
  const stationsDiv = document.createElement('div');
  stationsDiv.classList.add('list__container--station');
  stationsDiv.textContent = station;
  listcontainerDiv.appendChild(stationsDiv);
}

function scrollClick(container, scrollDistance) {
  container.scrollBy({ left: scrollDistance, behavior: 'smooth' });
}

const leftScroll = document.getElementById('leftScroll');
const rightScroll = document.getElementById('rightScroll');

leftScroll.addEventListener('click', ()=>scrollClick(listcontainerDiv, -30));
rightScroll.addEventListener('click', ()=>scrollClick(listcontainerDiv, 30));


window.onload = function () {
  loadAttractions();
  getMrts();
};