# Design and Development of a Website - [Hotel Booking System]


## 🛠️ Tech Stack
* **Backend:** Python (Flask)
* **Frontend:** HTML5, CSS3, JavaScript
* **Database:** MySQL

## ✅ Features Completed 
- **Project Structure:** Organized folder system (Routes, Static, Templates, Database).
- **Database Schema:** Initial database design and table structures.
- **Routing System:** Public routes for home and landing pages.
- **Static Assets:** Integration of CSS, JS, and high-quality images.
- **Template Inheritance:** Using a `base.html` for a consistent UI.

- **Secure Authentication System:**
    - Integrated **Signup, Login, and Logout** functionality.
    - Password security and session-based user tracking.
- **Password Recovery Workflow:**

- Secure Token Generation: Uses secrets.token_urlsafe to create cryptographically secure reset links.

- Timed Expiration: Implemented a 15-minute expiration window for reset tokens to enhance security.

- Rate Limiting: Protection against brute-force email spamming and API abuse.

- Password Strength Validation: Integrated server-side checks to ensure new passwords meet security complexity standards.

- **Custom Security Decorators:**
    - `@login_required`: Prevents unauthorized access to private routes by redirecting unauthenticated users to the login page.
    - `@admin_required`: Implements Role-Based Access Control (RBAC) to ensure only users with the 'admin' role can access sensitive management panels.
- **Role-Based Dashboards:**
    - **Admin Dashboard:** A restricted area for system administrators (`/admin/dashboard`).
    - **User Dashboard:** A personalized landing area for standard registered users (`/user/dashboard`).
- **Flash Messaging:** User-friendly alerts for login requirements and permission denials.


- **Profile Management System:**
    - **Unified Profile Section:** Dedicated profiles for both Admins and Users to manage personal information.
    - **Profile Customization:** Users can upload, update, and remove profile pictures.
    - **Information Management:** Edit forms to update display names, bios, and contact details.
    - **Dynamic Rendering:** Profile views that adapt based on the logged-in user's role (Admin vs. User).
    - **Secure File Handling:** Backend validation for image uploads to ensure only supported formats (PNG, JPG,JEPG,GIF) are saved.

- **Contact & Communication System:**

    - **Contact Form:** Secure form for user inquiries.

    - **Email Integration**: Automatic SMTP forwarding of user messages to the Admin's inbox.

    - **Confirmation UI:** Success/Error messaging for feedback on delivery status.


- **Advanced Search & Dynamic Pricing Engine:**

    - **Multi-Factor Filtering:** Search functionality by City, Room Type, and Guest Capacity.

    - **Seasonal Pricing Logic:** Automated price calculation that shifts between Peak and Off-Peak rates based on   stay dates.

    - **Internationalization (Currency Support):** Real-time price conversion fetching exchange rates and symbols ($, £, €, etc.) dynamically from the database.

    - **Availability Tracking:** Logic to calculate total stay cost based on nights and cross-reference room availability.

 ## 🛠️ 3. Technical Stack Update 
    Libraries: Datetime, JSON

- **Challenges:** Implementing the search engine required complex SQL joins across four tables while   simultaneously calculating seasonal price multipliers and currency conversions in Python. This was solved by creating helper functions for date math and optimizing the database query flow.


- **User Management System:**

    - **Full CRUD Lifecycle:** Integrated functionality to add, view, edit, and delete user accounts.

    - **Administrative Security:** Protected user management routes with nested @login_required and @admin_required decorators.

    - **Partial Updates:** Developed logic to update user profiles without requiring a password change (password is only re-hashed if a new one is provided).

    - **Account Status Control:** Admins can manually toggle user statuses and roles (admin vs. customer) directly from the dashboard.


- **Advanced Hotel Administration:**

    - **Relational Data Management:** Created an integrated dashboard view joining Cities, Hotels, and Room Types to provide a bird's-eye view of operations.

    - **Real-time Inventory Monitoring:** Implemented a sub-query system to calculate and display available room counts per hotel directly on the management panel.

    - **State Management:** Added the ability to toggle hotel visibility (is_active) and update seasonal pricing on-the-fly.

    - **Media Management:** Securely handles hotel image uploads and updates, including directory management for static assets


- **Dynamic Inventory Management:**

    - **Automated Status Sync:** Developed a synchronization engine that updates room availability in real-time based on confirmed bookings and current dates.

    - **Business Logic Safeguards:** Implemented validation logic to prevent administrative errors, such as manually overriding the status of an occupied room.

    - **Maintenance Protection:** Integrated logic to preserve 'Maintenance' states during automated inventory sweeps, ensuring guest safety and operational accuracy.


- **Reports and Analytics:**

    - **Financial Reporting:** Automated revenue tracking with custom date range filters for flexible period analysis.

    - **Customer Lifetime Value (CLV):** Implemented a VIP customer tracking system based on total spending, allowing for loyalty-based marketing insights.

    - **Visual Data Representation:** Integrated Chart.js to render interactive growth curves for revenue trends.

    - **Performance Metrics:** Created a profitability analysis tool to calculate net income per hotel based on custom margin logic.

    - **Export Capabilities:** Designed a print-ready CSS layout for professional PDF report generation directly from the browser.

- **Advanced Reservation Engine:**

    - **Transactional Integrity:** Utilizes ACID-compliant transactions to handle room allocations, ensuring data consistency during high-traffic periods.

    - **Collision-Resistant Logic:** Integrated a sub-query validation system to prevent double-booking by checking room availability against overlapping confirmed and pending dates.

    - **Smart Pricing & Revenue Management:** Seasonal Adjustments: Automatic Peak/Off-peak rate detection based on booking dates.

    - **Incentivized Booking:** Implemented a tiered "Early Bird" discount system (up to 30%) based on the advance booking window.

    - **Inventory Hold System:** Implemented a 15-minute temporary hold on rooms for "Pending" bookings to improve user conversion while protecting inventory.



- **Cancellation & Revenue Management**
    - **Policy-Driven Refunds:** Developed a dynamic calculation engine that determines refund eligibility and fee percentages based on a cancellation_policies database table and the lead time before check-in.

    - **IDOR Security Implementation:** Secured all cancellation and detail-fetching routes by validating record ownership (user_id check) before execution, preventing unauthorized data manipulation.

    - **Automated Inventory Restoration:** Implemented a relational update trigger that immediately marks a room as available when a guest cancels, maximizing hotel occupancy potential.

    - **RESTful Cancellation Preview:** Created an AJAX-ready endpoint that provides users with a transparent breakdown of fees and refunds before they confirm a cancellation.



- **Integrated Payment & Reservation Flow**
    - **Time-Limited Inventory Locking:** Implemented a strict 15-minute reservation window. Using expires_at logic, the system prevents "inventory hanging" by only allowing payments for active, non-expired sessions.

    - **ACID-Compliant Payment Processing:** Utilized database transactions (executeTransaction) to ensure that the payment record creation and the booking status update either both succeed or both fail, preventing data mismatches.

    - **UUID Transaction Tracking:** Integrated unique transaction IDs using uuid4 for every successful payment, simulating real-world payment gateway reconciliation (like Stripe or PayPal).

    - **Automated Booking Confirmation:** Successfully processed payments trigger an immediate state transition from pending to confirmed, automatically updating the hotel's room availability.

    - **Safety Checks:** Implemented server-side validation to ensure payments cannot be processed for already-paid, cancelled, or expired bookings.



 
