import { useDispatch, useSelector } from "react-redux";
import { bagActions } from "../store/bagSlice";
import { GrAddCircle } from "react-icons/gr";
import { AiFillDelete } from "react-icons/ai";
import { useNavigate } from "react-router-dom";
import { useState } from "react";

import {API_BASE_URL} from "../util.js";

const HomeItem = ({ item }) => {
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const token = useSelector((s) => s.auth.token);
  const bagItems = useSelector((s) => s.bag);
  const [busy, setBusy] = useState(false);

  const inBag = bagItems.includes(item.id);

  const handleAddToBag = async () => {
    if (!token) return navigate("/login");
    try {
      setBusy(true);
      await fetch(`${API_BASE_URL}/bag`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ product_id: item.id }),
      });
      dispatch(bagActions.addToBag(item.id));
    } finally {
      setBusy(false);
    }
  };

  const handleRemove = async () => {
    if (!token) return navigate("/login");
    try {
      setBusy(true);
      await fetch(`${API_BASE}/bag/${item.id}`, {
        method: "DELETE",
        headers: { Authorization: `Bearer ${token}` },
      });
      dispatch(bagActions.removeFromBag(item.id));
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="item-container">
      <img className="item-image" src={item.image} alt="item" />
      <div className="rating">
        {item.rating_stars} ⭐ | {item.rating_count}
      </div>
      <div className="company-name">{item.company}</div>
      <div className="item-name">{item.item_name}</div>
      <div className="price">
        <span className="current-price">Rs {item.current_price}</span>
        <span className="original-price">Rs {item.original_price}</span>
        <span className="discount">({item.discount_percentage}% OFF)</span>
      </div>

      {inBag ? (
        <button
          type="button"
          className="btn btn-add-bag btn-danger"
          onClick={handleRemove}
          disabled={busy}
        >
          <AiFillDelete /> {busy ? "Removing..." : "Remove"}
        </button>
      ) : (
        <button
          type="button"
          className="btn btn-add-bag btn-success"
          onClick={handleAddToBag}
          disabled={busy}
        >
          <GrAddCircle /> {busy ? "Adding..." : "Add to Bag"}
        </button>
      )}
    </div>
  );
};

export default HomeItem;

