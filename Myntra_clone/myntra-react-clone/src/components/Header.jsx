import { BsFillPersonFill } from "react-icons/bs";
import { FaFaceGrinHearts, FaBagShopping } from "react-icons/fa6";
import { Link, useNavigate } from "react-router-dom";
import { useSelector, useDispatch } from "react-redux";
import { authStatusActions } from "../store/authSlice";
import { bagActions } from "../store/bagSlice";
import { useRef } from "react";
import { fetchStatusActions } from "../store/fetchStatusSlice";
import { itemsActions } from "../store/ItemsSlice";
import {API_BASE_URL} from "../util.js";

const Header = () => {
  const bag = useSelector((store) => store.bag);
  const { user, token } = useSelector((store) => store.auth);
  const search = useRef();
  const dispatch = useDispatch();
  const navigate = useNavigate();

  const handleLogout = (e) => {
    e.preventDefault();
    dispatch(authStatusActions.logout());
    dispatch(bagActions.clearBag());
    navigate("/login");
  };

  let currentSearchController = null;

  const handleLogoClick = async (e) => {

    try {
      dispatch(fetchStatusActions.markFetchingStarted());

      const res = await fetch(`${API_BASE_URL}/items`);
      if (!res.ok) throw new Error(`Failed to load items (${res.status})`);

      const data = await res.json();
      const items = Array.isArray(data?.items) ? data.items : [];

      // Replace the catalog with the full list
      dispatch(itemsActions.addInitialItems(items));

      // clear the search input visually
      if (search.current) search.current.value = "";
    } catch (err) {
      console.error("Load all items error:", err);
    } finally {
      dispatch(fetchStatusActions.markFetchingFinished());
    }
  };

  const handleSearch = async (e) => {
    if (e.key !== "Enter") return;

    const q = search.current?.value?.trim() ?? "";
    if (!q) return;

    // cancel any previous search
    if (currentSearchController) currentSearchController.abort();
    currentSearchController = new AbortController();

    // normalize base url (remove trailing slash if any)
    const API_BASE = import.meta.env?.VITE_API_BASE_URL;

    try {
      dispatch(fetchStatusActions.markFetchingStarted());

      const res = await fetch(
        `${API_BASE}/search/items?q=${encodeURIComponent(q)}`,
        { signal: currentSearchController.signal }
      );

      if (!res.ok) {
        const text = await res.text().catch(() => "");
        throw new Error(text || `Search failed with ${res.status}`);
      }

      const data = await res.json();

      // backend returns: { items: [...] }
      const items = Array.isArray(data?.items) ? data.items : [];
      dispatch(itemsActions.addInitialItems(items));
    } catch (err) {
      if (err.name !== "AbortError") {
        console.error("Search error:", err);
      }
    } finally {
      // ALWAYS stop spinner, success or error
      dispatch(fetchStatusActions.markFetchingFinished());
      currentSearchController = null;
    }
  };

  return (
    <header>
      <div className="logo_container">
        <Link to="/" onClick={handleLogoClick}>
          <img
            className="myntra_home"
            src="images/myntra_logo.webp"
            alt="Myntra Home"
          />
        </Link>
        {user ? user.username : ""}
      </div>

      <nav className="nav_bar">
        <a href="#">Men</a>
        <a href="#">Women</a>
        <a href="#">Kids</a>
        <a href="#">Home & Living</a>
        <a href="#">Beauty</a>
        <a href="#">
          Studio <sup>New</sup>
        </a>
      </nav>

      <div className="search_bar">
        <span className="material-symbols-outlined search_icon">search</span>
        <input
          className="search_input"
          placeholder="Search for products, brands and more"
          ref={search}
          onKeyDown={handleSearch}
        />
      </div>

      <div className="action_bar">
        <div className="action_container">
          <BsFillPersonFill />
          <div className="dropdown">
            <span className="action_name dropbtn">
              {user ? user.username : "Profile"}
            </span>
            <div className="dropdown-content">
              {!token ? (
                <>
                  <Link to="/login">Login</Link>
                  <Link to="/register">Register</Link>
                </>
              ) : (
                <>
                  <span
                    style={{
                      padding: "8px 12px",
                      display: "block",
                      opacity: 0.7,
                    }}
                  >
                    Signed in as {user?.email || user?.username}
                  </span>
                  <a href="#" onClick={handleLogout}>
                    Logout
                  </a>
                </>
              )}
            </div>
          </div>
        </div>

        <div className="action_container">
          <FaFaceGrinHearts />
          <span className="action_name">Wishlist</span>
        </div>

        <Link className="action_container" to="/bag">
          <FaBagShopping />
          <span className="action_name">Bag</span>
          <span className="bag-item-count">{bag.length}</span>
        </Link>
      </div>
    </header>
  );
};

export default Header;


