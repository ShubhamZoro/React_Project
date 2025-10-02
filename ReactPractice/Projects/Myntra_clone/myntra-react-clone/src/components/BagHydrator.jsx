// components/BagHydrator.jsx
import { useEffect } from "react";
import { useDispatch, useSelector } from "react-redux";
import { bagActions } from "../store/bagSlice";

import { API_BASE_URL } from "../util.js";

export default function BagHydrator() {
  const token = useSelector((s) => s.auth.token);
  const dispatch = useDispatch();

  useEffect(() => {
    if (!token) {
      dispatch(bagActions.clearBag());
      return;
    }
    (async () => {
      try {
        const res = await fetch(`${API_BASE_URL}/bag/ids`, {
          headers: { Authorization: `Bearer ${token}` },
        });
        const data = await res.json();
        if (res.ok) dispatch(bagActions.addInitialItems(data.ids || []));
      } catch {}
    })();
  }, [token, dispatch]);

  return null;
}
