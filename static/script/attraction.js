  const model = {
    data: null,
    init: async function() {
      const id = window.location.pathname.split("/").pop();
      const response = await fetch(`/api/attraction/${id}`);
      const responseJson = await response.json();
      this.data = responseJson.data;
    },
  };

  const view = {
    slideshowDiv: document.querySelector('.picture__slideshow'),
    pictureDiv: document.querySelector('.picture'),
    profileDiv: document.querySelector('.profile__info'),
    inforsDiv: document.querySelector('.infors'),
    morning: document.querySelector('input[value="morning"]').checked,
    priceInput: document.getElementById("price"),
    priceText: document.getElementById("money"),
    titleElement: document.querySelector('.title'),
    categoryElement: document.querySelector('.category'),
    dateInput: document.getElementById('date'),

    render: function(data, onClick) {
      this.slideshowDiv.style.backgroundImage = `url(${data.images[0]})`;
      this.slideshowDiv.style.backgroundSize = "cover";
      this.slideshowDiv.style.backgroundPosition = "center";
      
      this.titleElement.textContent = data.name;
      this.categoryElement.textContent = `${data.category} at ${data.mrt}`;

      this.inforsDiv.appendChild(this.createTextElement("span", data.description));
      this.inforsDiv.appendChild(this.createLabeledText("景點地址：", data.address));
      this.inforsDiv.appendChild(this.createLabeledText("交通方式：", data.transport));

      this.renderDot(data.images, onClick);
    },
    createTextElement: function(tag, text) {
      const el = document.createElement(tag);
      el.textContent = text;
      return el;
    },
    createLabeledText: function(label, text) {
      const container = document.createElement("div");

      const title = document.createElement("p");
      title.textContent = label;
      title.style.fontWeight = "600";

      const content = document.createElement("span");
      content.textContent = text;

      container.appendChild(title);
      container.appendChild(content);
      return container;
    },
    createDot: function(currentIndex, onClick){
      const dotSpan = document.createElement("span");
      dotSpan.classList.add("dot");
      dotSpan.addEventListener("click", () => onClick(currentIndex));
      return dotSpan;
    },
    renderDot: function(data, onClick) {
      this.dotsContainer = document.createElement("div");
      this.dotsContainer.classList.add("picture__dot");
      this.pictureDiv.appendChild(this.dotsContainer);

      this.dotsContainer.innerHTML = "";

      data.forEach((_, i) => {
        const dot = this.createDot(i, onClick);
        this.dotsContainer.appendChild(dot);
      });
    },
    changeImage: function(imageUrl) {
      this.slideshowDiv.style.backgroundImage = `url(${imageUrl})`;
    },
    updateDot: function(currentIndex) {
      const dots = this.dotsContainer.querySelectorAll(".dot");
      dots.forEach((dot, index) => {
        dot.classList.toggle("active", index === currentIndex);
        if (index === currentIndex) {
          dot.style.backgroundColor = "#757575";
          dot.style.border = "solid 1px white";
        } else {
          dot.style.backgroundColor = "";
          dot.style.border = "";
        }
      });
    },
    selectedTime: function () {
      return document.querySelector('input[name="time"]:checked').value === "morning";
    },
    updatePrice: function(){
      const isMorning = this.selectedTime();
      if (isMorning) {
        this.priceInput.value = 2000;
        this.priceText.textContent = "新台幣 2000 元";
      } else {
        this.priceInput.value = 2500;
        this.priceText.textContent = "新台幣 2500 元";
      }
    },
    setMinDate: function() {
      if (this.dateInput) {
        const today = new Date();
        const yyyy = today.getFullYear();
        const mm = String(today.getMonth() + 1).padStart(2, '0');
        const dd = String(today.getDate()).padStart(2, '0');
        this.dateInput.min = `${yyyy}-${mm}-${dd}`;
      }
    },
  };

  const controller = {
    leftArrow: document.getElementById('leftArrow'),
    rightArrow: document.getElementById('rightArrow'),
    currentIndex: 0,

    init: async function() {
      await model.init();
      view.render(model.data, this.dotClick.bind(this));
      view.setMinDate();
      this.arrowClick();
      view.updateDot(this.currentIndex);
      view.updatePrice();
      this.selectTimeChange();
    },
    dotClick: function(currentIndex) {
      this.currentIndex = currentIndex;
      view.changeImage(model.data.images[this.currentIndex]);
      view.updateDot(this.currentIndex);
    },
    arrowClick: function() {
      this.rightArrow.addEventListener("click", () => this.changeSlide(model.data.images, 1));
      this.leftArrow.addEventListener("click", () => this.changeSlide(model.data.images, -1));
    },
    selectTimeChange: function() {
      document.querySelectorAll('input[name="time"]').forEach(radio => {
        radio.addEventListener("change", () => view.updatePrice());
      });
    }
  };

  controller.init();