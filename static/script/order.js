const orderButton = document.getElementById('submit-button');
const APP_ID = 159809;
const APP_KEY = 'app_eIeipEZLKk2Daoj0t9ukVA6nRG8cVDqfzoLmoyIWa6CUBIFXC9PRdicCW17v';

TPDirect.setupSDK(APP_ID, APP_KEY, 'sandbox');

TPDirect.card.setup({
  fields: {
    number: {
      element: '#booking--ccnumber',
      placeholder: '**** **** **** ****'
    },
    expirationDate: {
      element: '#booking--ccexp',
      placeholder: 'MM / YY'
    },
    ccv: {
      element: '#booking--cccvv',
      placeholder: 'CVV'
    }
  },
  styles: {
    'input': {
      'color': '#333',
      'font-size': '16px',
      'height': '38px',
    },
    '.valid': {
      'color': 'green'
    },
    '.invalid': {
      'color': 'red'
    },
    '@media screen and (max-width: 400px)': {
      'input': {
          'color': 'orange'
      }
    }      
  },
  isMaskCreditCardNumber: true,
  maskCreditCardNumberRange: {
    beginIndex: 6,
    endIndex: 11
  }
});

orderButton.addEventListener('click', function () {
  TPDirect.card.getPrime(async (result) => {
    if (result.status !== 0) {
      return;
    }
    const contactName = document.getElementById("booking--input--username").value;
    const contactEmail = document.getElementById("booking--input--email").value;
    const contactPhone = document.getElementById("booking--input--mobile").value;
    if (!contactName || !contactEmail || !contactPhone) {
      return;
    }
    const prime = result.card.prime;

    const booking = await fetch("/api/booking", { 
      method: "GET",
      headers: {
        "Authorization": `Bearer ${token}`,
        "Content-Type": "application/json"
      }
    });
    const bookingRes = await booking.json();

    const orderBody = {
      prime: prime,
      order: {
        price: bookingRes.data.price,
        trip: {
          attraction: {
            id: bookingRes.data.attraction.id,
            name: bookingRes.data.attraction.name,
            address: bookingRes.data.attraction.address,
            image: bookingRes.data.attraction.image
          },
          date: bookingRes.data.date,
          time: bookingRes.data.time
        },
        contact: {
          name: contactName,
          email: contactEmail,
          phone: contactPhone
        }
      }
    };
    const order = await fetch("/api/orders", {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${token}`,
        "Content-Type": "application/json"
      },
      body: JSON.stringify(orderBody)
    });
    const orderRes = await order.json();
    window.location.href = `/thankyou?number=${orderRes.data.number}`;
  });
});
