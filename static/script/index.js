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
  attractionsDiv.innerHTML = '';
  loadAttractions();
}

async function getAttractions(page, keyword){
  let url = `/api/attractions?page=${page}`;
  if (keyword) url += `&keyword=${encodeURIComponent(keyword)}`;
  
  let response = await fetch(url);
  let rawData = await response.json();

  let nextPage = rawData?.nextPage;
  let data = rawData.data.map(({ id, name, category, mrt, images }) => ({
    id, name, category, mrt, image: images[0]
  }));
  return { nextPage, data };
}

async function loadAttractions() {
  isLoading = true;
  let { nextPage, data } = await getAttractions(page, keyword);
  
  for (let i = 0; i < data.length; i++) {
    let attractionDiv = document.createElement("div");
    attractionDiv.classList.add("attractions__card");
  
    attractionDiv.style.backgroundImage = `url(${data[i].image})`;
    attractionDiv.style.backgroundSize = "cover";
    attractionDiv.style.backgroundPosition = "center";

    attractionDiv.addEventListener("click", () => {
      // window.location.href = `/attraction/${data[i].id}`;
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


window.onload = function () {
  loadAttractions();
  getMrts();
};