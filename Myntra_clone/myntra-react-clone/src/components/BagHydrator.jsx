// components/BagHydrator.jsx
import { useEffect } from "react";
import { useDispatch, useSelector } from "react-redux";
import { bagActions } from "../store/bagSlice";

const API_BASE = "http://localhost:8080";

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
        const res = await fetch(`${API_BASE}/bag/ids`, {
          headers: { Authorization: `Bearer ${token}` },
        });
        const data = await res.json();
        if (res.ok) dispatch(bagActions.addInitialItems(data.ids || []));
      } catch {}
    })();
  }, [token, dispatch]);

  return null;
}
