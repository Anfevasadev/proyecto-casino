/*
  This page handles user authentication: login and registration.

  Steps to implement:
    1. Import React hooks useState.
    2. Import useNavigate from react-router-dom to navigate after login.
    3. Import axios for HTTP requests.
    4. Create state variables for:
       - name: the full name of the user when registering.
       - username: the username.
       - password: the password.
       - isRegistering: a boolean indicating whether the user is registering
         or logging in.
       - error: to store any error messages from the API.
    5. Define two async functions:
       - handleRegister: sends a POST request to '/api/v1/auth/register' with
         { name, username, password }. On success, either navigate to login
         or automatically log the user in.
       - handleLogin: sends a POST request to '/api/v1/auth/login' with
         { username, password }. On success, navigate to '/casinos'.
    6. Create a form with inputs for name (only show when isRegistering is true),
       username, and password. Bind each input to its respective state variable.
    7. Add a submit button that calls handleRegister or handleLogin depending on
       the mode.
    8. Provide a link or button that toggles between login and register modes.
    9. Display error messages if the API returns an error (e.g., invalid credentials).
    10. Use Tailwind CSS classes for styling the form and inputs.

  Again, leave these instructions as comments only; do not implement the code here.
*/

// TODO: implement Login page according to the instructions above.
