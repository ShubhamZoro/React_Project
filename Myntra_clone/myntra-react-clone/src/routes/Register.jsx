import React, { useRef } from "react";
import { useNavigate } from "react-router-dom";

function Register() {
  const navigate = useNavigate();
  const API_BASE = "http://localhost:8080";

  const usernameRef = useRef(null);
  const emailRef = useRef(null);
  const passwordRef = useRef(null);

  async function register(e) {
    e.preventDefault();

    const username = (usernameRef.current?.value || "").trim();
    const email = (emailRef.current?.value || "").trim();
    const passwordVal = passwordRef.current?.value || "";

    if (!username || !email || !passwordVal) {
      alert("Username, Email and Password are required");
      return;
    }

    try {
      const res = await fetch(`${API_BASE}/register`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        // If your backend only needs username+password, it's fine to send email; it will be ignored.
        body: JSON.stringify({ username, password: passwordVal, email }),
      });
      const data = await res.json().catch(() => ({}));

      if (res.status === 409) {
        alert("That username already exists. Try another or log in.");
        return;
      }
      if (!res.ok) throw new Error(data.detail || "Registration failed");

      alert("Registration successful");
      navigate("/login");
    } catch (err) {
      alert(err.message || "Something went wrong");
    }
  }

  return (
    <div className="container">
      <div
        className="row justify-content-center align-items-center"
        style={{ minHeight: "calc(100vh - 140px)" }}
      >
        <div className="col-12 col-sm-8 col-md-6 col-lg-4">
          <form
            className="bg-white p-4 rounded-3 border shadow-sm"
            onSubmit={register}
          >
            <div className="mb-3">
              <label className="form-label">Username</label>
              <input
                type="text"
                className="form-control"
                placeholder="Username"
                ref={usernameRef}
              />
            </div>

            <div className="mb-3">
              <label className="form-label">Email</label>
              <input
                type="text"
                className="form-control"
                placeholder="Email"
                ref={emailRef}
              />
            </div>

            <div className="mb-3">
              <label className="form-label">Password</label>
              <input
                type="password"
                className="form-control"
                placeholder="Enter Password"
                ref={passwordRef}
              />
            </div>

            <button type="submit" className="btn btn-success w-100">
              Sign Up
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}

export default Register;
