// Bag.jsx
import BagItem from "../components/BagItem";
import BagSummary from "../components/BagSummary";
import { useSelector, useDispatch } from "react-redux";
import { useEffect } from "react";
import { bagActions } from "../store/bagSlice";
import { itemsActions } from "../store/ItemsSlice";

import {API_BASE_URL} from "../util.js";

const Bag = () => {
  const dispatch = useDispatch();
  const token = useSelector((s) => s.auth.token);
  const bagItems = useSelector((s) => s.bag);
  const items = useSelector((s) => s.items);

  useEffect(() => {
    if (!token) return;

    (async () => {
      // 1) hydrate bag ids
      const res = await fetch(`${API_BASE_URL}/bag/ids`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      const data = await res.json();
      if (res.ok) dispatch(bagActions.addInitialItems(data.ids || []));

      // 2) ensure catalog is loaded (so filter works)
      if (!items || items.length === 0) {
        const r2 = await fetch(`${API_BASE}/items`);
        const d2 = await r2.json();
        if (r2.ok) dispatch(itemsActions.addInitialItems(d2.items || []));
      }
    })();
  }, [token, dispatch]); // (items not in deps on purpose)

  const finalItems = items.filter((it) => bagItems.includes(it.id));

  return (
    <main>
      <div className="bag-page">
        <div className="bag-items-container">
          {finalItems.map((item) => (
            <BagItem key={item.id} item={item} />
          ))}
        </div>
        <BagSummary />
      </div>
    </main>
  );
};

export default Bag;


