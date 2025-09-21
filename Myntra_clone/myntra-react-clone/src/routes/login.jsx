import React, { useRef } from "react";
import { useNavigate } from "react-router-dom";
import { useDispatch } from "react-redux";
import { authStatusActions } from "../store/authSlice";
import {API_BASE_URL} from "../util.js";
function Login() {
  const navigate = useNavigate();
  const dispatch = useDispatch();
  const emailRef = useRef(null);
  const passwordRef = useRef(null);
  async function login(e) {
    e.preventDefault();
    const useremail = (emailRef.current.value || "").trim();
    const password = passwordRef.current.value || "";

    if (!useremail || !password) {
      alert("Email and Password are required");
      return;
    }

    try {
      const res = await fetch(`${API_BASE_URL}/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ useremail, password }),
      });
      const data = await res.json().catch(() => ({}));
      if (!res.ok) throw new Error(data.detail || "Login failed");
      dispatch(
        authStatusActions.setCredentials({
          token: data.access_token,
          user: data.user,
        })
      );
      navigate("/");
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
            onSubmit={login}
          >
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
              Sign In
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}

export default Login;

