
Markdown


# Functional Requirements: Design Gallery Android App (Fast-Tracked)

---

## 1. User Management & Authentication

* **FR-1.1: User Registration:**
    * The system SHALL allow new users to register with a unique username and password.
    * The system SHALL store a hashed version of the user's password using bcrypt.
    * Upon registration, the user's `is_admin` status SHALL default to `0` (false) and `is_approved` status SHALL default to `0` (false).
    * The system SHALL prevent registration with an already existing username.
    * The system SHALL provide feedback to the user regarding registration success or failure (e.g., "Registration successful! Please wait for admin approval." or "Username already taken.").

* **FR-1.2: User Login:**
    * The system SHALL allow registered users to log in with their username and password.
    * The system SHALL verify the provided password against the stored hash.
    * The system SHALL only allow login if the user's `is_approved` status is `1` (true).
    * Upon successful login, the system SHALL issue a JSON Web Token (JWT) containing `userId`, `username`, and `isAdmin` status.
    * The system SHALL securely store the JWT on the client-side (Android app).
    * The system SHALL provide feedback for invalid credentials or unapproved users.

* **FR-1.3: User Authorization:**
    * The system SHALL protect specific API endpoints (e.g., design creation, user approval, design management APIs) by requiring a valid JWT in the `Authorization` header.
    * The system SHALL verify the authenticity and expiry of the JWT for protected routes.
    * For admin-only endpoints, the system SHALL further verify that the authenticated user's `isAdmin` status (from the JWT payload) is `1` (true).
    * The system SHALL return a `401 Unauthorized` response for missing or invalid tokens.
    * The system SHALL return a `403 Forbidden` response for unauthorized access to admin-only functions by non-admin users.

* **FR-1.4: User Approval (Admin Functionality):**
    * The system SHALL provide an admin-only interface (within the Android app) to view all registered users.
    * The system SHALL display each user's username and current `is_approved` status.
    * Admins SHALL be able to approve or disapprove users by updating their `is_approved` status in the database.
    * The system SHALL update the `is_approved` status in the D1 `users` table based on admin action.

* **FR-1.5: Secure Session Management:**
    * The Android app SHALL use the securely stored JWT for all authenticated API requests.
    * The Android app SHALL check for an existing JWT on launch to determine if a user is already logged in and navigate accordingly (to gallery or login screen).
    * The Android app SHALL provide a mechanism to log out, which SHALL remove the stored JWT.

---

## 2. Design Gallery Management

* **FR-2.1: Design Creation (Admin Functionality):**
    * The system SHALL allow authenticated admin users to add new design entries.
    * Design entries SHALL include `designname`, `style`, `colour`, `short_description`, `long_description`, `categories`, and `cloudflare_image_id`.
    * The system SHALL store this metadata in the D1 `designs` table.

* **FR-2.2: Design Listing & Viewing:**
    * The system SHALL allow authenticated users (any logged-in user) to fetch and view a list of designs.
    * Each design returned SHALL include its metadata and generated Cloudflare Image URLs (thumbnail, medium, original) based on `cloudflare_image_id`.
    * The system SHALL support pagination for design listings (`limit`, `offset` query parameters).
    * The system SHALL support filtering designs by `style`, `colour`, and `categories` via query parameters.
    * The system SHALL support searching designs by a query `q` across `designname`, `short_description`, `long_description`, `style`, `colour`, and `categories` using a case-insensitive SQL `LIKE` operator.

* **FR-2.3: Single Design Detail:**
    * The system SHALL allow authenticated users to fetch and view the complete details of a single design by its `id`.
    * The returned design details SHALL include all metadata and generated Cloudflare Image URLs.
    * The system SHALL return a `404 Not Found` if the specified design `id` does not exist.

* **FR-2.4: Image Upload Pre-signing:**
    * The system SHALL provide an API endpoint (`/api/upload-url`) that generates a direct upload URL for Cloudflare Images.
    * This endpoint SHALL optionally be protected by admin authorization to ensure only authorized entities can initiate image uploads.
    * The generated URL SHALL allow for direct image upload to Cloudflare Images.

* **FR-2.5: Bulk Image & Metadata Upload (Admin Tool):**
    * The system SHALL support an external (non-app) Python script for bulk uploading images and their corresponding metadata.
    * The script SHALL read design metadata from a CSV file.
    * For each design, the script SHALL:
        * Call the `upload-url` Worker API to get a signed upload URL.
        * Upload the local image file to the received upload URL.
        * Call the `admin/designs` Worker API (with admin JWT) to save the design metadata and the `cloudflare_image_id` received from the image upload.
    * The script SHALL include robust error handling and progress reporting.

---

## 3. Android Application Features

* **FR-3.1: Core Gallery Display:**
    * The Android app SHALL display designs in a performant grid or list view (utilizing `FlatList` or `FlashList`).
    * Designs SHALL be fetched from the backend and replace any dummy data.
    * Image display SHALL use `react-native-fast-image` for optimized loading and caching.
    * The app SHALL implement lazy loading/pagination to load more designs as the user scrolls towards the end of the list.

* **FR-3.2: Design Detail View:**
    * Tapping on a design in the gallery SHALL navigate to a dedicated detail screen.
    * The detail screen SHALL display all associated metadata (`designname`, `style`, `colour`, `short_description`, `long_description`, `categories`) and the original quality image.

* **FR-3.3: Search & Filtering UI:**
    * The Android app SHALL include a search bar to allow users to search for designs by keywords.
    * The search functionality SHALL debounce user input to avoid excessive API calls.
    * The Android app SHALL provide UI elements (e.g., dropdowns, buttons) to filter designs by `style`, `colour`, and `categories`.
    * Search and filter functionalities SHALL be combinable.

* **FR-3.4: Screenshot Prevention:**
    * The Android app SHALL implement mechanisms (e.g., using `react-native-prevent-screenshot`) to prevent users from taking screenshots of design content within the main gallery and detail screens.
    * The app SHALL disable or remove any template features that might allow saving, downloading, or sharing of images to prevent unauthorized content distribution.

* **FR-3.5: User Interface Adaptation:**
    * The Android app's UI elements (login, registration, gallery, detail, admin screens) SHALL be adapted from the chosen Envato React Native template, ensuring consistency with the template's design language.

* **FR-3.6: Offline Access (Future Consideration/Stretch Goal):**
    * The app MAY cache recently viewed designs or gallery listings to provide limited offline access or faster loading times. (Not explicitly in the 3-day plan, but good to note for future iterations).

---

## 4. Technical & Performance Requirements

* **TR-4.1: Backend Technology Stack:**
    * Backend APIs SHALL be implemented using Cloudflare Workers (Hono framework).
    * Database SHALL be Cloudflare D1.
    * Image storage and delivery SHALL be Cloudflare Images.

* **TR-4.2: Frontend Technology Stack:**
    * Frontend SHALL be developed using React Native, based on an Envato template.
    * Key libraries include `axios` for API calls, `react-native-fast-image` for optimized image display, `react-native-keychain` for secure token storage, and `react-navigation` for navigation.

* **TR-4.3: Scalability:**
    * The chosen Cloudflare backend (Workers, D1, Images) SHALL provide inherent scalability to handle a large number of users and design assets.

* **TR-4.4: Security:**
    * All API communication SHALL be over HTTPS.
    * Passwords SHALL be stored as bcrypt hashes.
    * Session management SHALL utilize JWTs.
    * Sensitive data (JWTs) SHALL be stored securely on the client device using platform-specific secure storage.

* **TR-4.5: Performance:**
    * The Android app SHALL ensure smooth scrolling and responsive UI, especially when dealing with a large number of images (1000+ designs).
    * Image loading SHALL be optimized to minimize data usage and loading times.

---

Do these functional requirements align with your vision for the Design Gallery Android App?


