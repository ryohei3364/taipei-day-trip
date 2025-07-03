# Taipei Day Trip - e-commerce website
Taipei Day Trip is an e-commerce website that offers travel itinerary booking and integrated payment services.

### Demo: https://taipei.booktrend.online
### Test Account: 
<div style="width: 300px;">

| Account | Password |
|--------|----------|
| test@test   | test |

</div>

![taipei trip logo](<public/taipei.jpg>)

# Main Feature
### JWT and Bearer Token Mechanism for Member System
After sign-in, the backend issues a signed JWT stored in localStorage. The frontend includes the token in Authorization headers for API calls and updates user status accordingly. Passwords are hashed using bcrypt.

➤ Technologies Used: PyJWT, bcrypt, Bearer Token

![member gif](<public/member.gif>)

### Auto-Loading Attractions on Scroll with Pagination
The system automatically loads more attraction data as users scroll, using the nextPage value from the API. It continues fetching until nextPage becomes null, with scroll detection handled via IntersectionObserver.

➤ Technologies Used: IntersectionObserver

![laoding gif](<public/loading.gif>)

### Keyword-based Search Functionality
This feature supports searches by MRT station name and provides fuzzy matching based on the description content.

➤ Technologies Used: MySQL

![search gif](<public/search.gif>)

### Travel Itinerary Booking and Cancellation Features
Implements a fully authenticated booking system with create, retrieve, and delete booking APIs. Users can reserve one trip at a time, view or delete bookings on the /booking page, and are redirected based on their sign-in status.

➤ Technologies Used: CRUD, MySQL

![booking gif](<public/booking.gif>)

### Online Payment Integration with TapPay
Supports credit card payment via TapPay’s SDK and Pay by Prime API. Upon order submission, the system processes payment, updates order status in the database, and redirects users to a thank-you page with the order number.

➤ Technologies Used: TapPay

![order gif](<public/order.gif>)

<!-- # Artictecture
![multilingual gif](<public/web_structure.png>)

# Database Schema
![schema gif](<public/database.png>) -->

# Contact
- 錢芝萍 Chih Pin Chien
- Email: ryohei3364@gmail.com