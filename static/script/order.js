const orderButton = document.getElementById('submit-button');
const warningPhone = document.querySelector('input[name="booking--input--mobile"]');

const APP_ID = 159809;
const APP_KEY = 'app_eIeipEZLKk2Daoj0t9ukVA6nRG8cVDqfzoLmoyIWa6CUBIFXC9PRdicCW17v';

if (warningPhone) {
  warningPhone.addEventListener("input", () => {
    warningPhone.style.boxShadow = "none";
  });
}

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
      warningPhone.style.boxShadow = "0 0 5px 2px #337788";
      return; 
    } else {
      warningPhone.style.boxShadow = "none";
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


// function validateCardFields() {
//   const status = TPDirect.card.getTappayFieldsStatus();
//   const numberFrame = document.querySelector('#booking--ccnumber iframe');
//   const expFrame = document.querySelector('#booking--ccexp iframe');
//   const ccvFrame = document.querySelector('#booking--cccvv iframe');

//   // 預設清除所有陰影
//   numberFrame.style.boxShadow = "none";
//   expFrame.style.boxShadow = "none";
//   ccvFrame.style.boxShadow = "none";

//   // 如果欄位不合法，加上綠色陰影
//   if (status.status.number !== 0) {
//     numberFrame.style.boxShadow = "0 0 5px 2px #337788";
//   }
//   if (status.status.expirationDate !== 0) {
//     expFrame.style.boxShadow = "0 0 5px 2px #337788";
//   }
//   if (status.status.ccv !== 0) {
//     ccvFrame.style.boxShadow = "0 0 5px 2px #337788";
//   }
//   return status.canGetPrime;  // 回傳是否可以送出 getPrime
// }


// orderButton.addEventListener('click', function () {
//   const isValid = validateCardFields();  // 檢查信用卡欄位
//   if (!isValid) {
//     return;  // 不合法就停止流程
//   }
//   TPDirect.card.getPrime(async (result) => {
//     if (result.status !== 0) {
//       return;
//     }
//     const contactName = document.getElementById("booking--input--username").value;
//     const contactEmail = document.getElementById("booking--input--email").value;
//     const contactPhone = document.getElementById("booking--input--mobile").value;
//     if (!contactName || !contactEmail || !contactPhone) {
//       warningPhone.style.boxShadow = "0 0 5px 2px #337788";
//       return; 
//     } else {
//       warningPhone.style.boxShadow = "none";
//     }
//     const prime = result.card.prime;

//     const booking = await fetch("/api/booking", { 
//       method: "GET",
//       headers: {
//         "Authorization": `Bearer ${token}`,
//         "Content-Type": "application/json"
//       }
//     });
//     const bookingRes = await booking.json();

//     const orderBody = {
//       prime: prime,
//       order: {
//         price: bookingRes.data.price,
//         trip: {
//           attraction: {
//             id: bookingRes.data.attraction.id,
//             name: bookingRes.data.attraction.name,
//             address: bookingRes.data.attraction.address,
//             image: bookingRes.data.attraction.image
//           },
//           date: bookingRes.data.date,
//           time: bookingRes.data.time
//         },
//         contact: {
//           name: contactName,
//           email: contactEmail,
//           phone: contactPhone
//         }
//       }
//     };
//     const order = await fetch("/api/orders", {
//       method: "POST",
//       headers: {
//         "Authorization": `Bearer ${token}`,
//         "Content-Type": "application/json"
//       },
//       body: JSON.stringify(orderBody)
//     });
//     const orderRes = await order.json();
//     window.location.href = `/thankyou?number=${orderRes.data.number}`;
//   });
// });