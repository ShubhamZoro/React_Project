import { useSelector, useDispatch } from "react-redux";
import { useState } from "react";
import { bagActions } from "../store/bagSlice"; 
import {API_BASE_URL} from "../util.js";

const BagSummary = () => {
  const dispatch = useDispatch();
  const [orderConfirmed, setOrderConfirmed] = useState(false);

  const bagItemIds = useSelector((state) => state.bag);
  const items = useSelector((state) => state.items);
  const token = useSelector((state) => state.auth.token); 
  const finalItems = items.filter((item) => bagItemIds.includes(item.id));

  const CONVENIENCE_FEES = 99;
  const totalItem = bagItemIds.length;
  const totalMRP = finalItems.reduce((sum, i) => sum + i.original_price, 0);
  const totalDiscount = finalItems.reduce(
    (sum, i) => sum + (i.original_price - i.current_price),
    0
  );
  const finalPayment = totalMRP - totalDiscount + CONVENIENCE_FEES;

  const handlePlaceOrder = async () => {
    try {
      for (const item of finalItems) {
        await fetch(`${API_BASE_URL}/bag/${item.id}`, {
          method: "DELETE",
          headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "application/json",
          },
        });
        dispatch(bagActions.removeFromBag(item.id));
      }

      setOrderConfirmed(true);
      setTimeout(() => setOrderConfirmed(false), 2000);
    } catch (err) {
      console.error(err);
      alert("Failed to place order. Please try again.");
    }
  };

  return (
    <div className="bag-summary">
      {orderConfirmed && (
        <div className="order-confirm-msg">✅ Order Confirmed!</div>
      )}

      <div className="bag-details-container">
        <div className="price-header">PRICE DETAILS ({totalItem} Items)</div>
        <div className="price-item">
          <span className="price-item-tag">Total MRP</span>
          <span className="price-item-value">₹{totalMRP}</span>
        </div>
        <div className="price-item">
          <span className="price-item-tag">Discount on MRP</span>
          <span className="price-item-value priceDetail-base-discount">
            -₹{totalDiscount}
          </span>
        </div>
        <div className="price-item">
          <span className="price-item-tag">Convenience Fee</span>
          <span className="price-item-value">₹99</span>
        </div>
        <hr />
        <div className="price-footer">
          <span className="price-item-tag">Total Amount</span>
          <span className="price-item-value">₹{finalPayment}</span>
        </div>
      </div>

      <button className="btn-place-order" onClick={handlePlaceOrder}>
        <div className="css-xjhrni">PLACE ORDER</div>
      </button>
    </div>
  );
};

export default BagSummary;
