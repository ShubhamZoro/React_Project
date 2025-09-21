import {configureStore} from "@reduxjs/toolkit";
import itemsSlice from "./itemsSlice.js";
import fetchStatusSlice from "./fetchStatusSlice.js";
import bagSlice from "./bagSlice.js";
import authSlice from "./authSlice.js";
const myntraStore = configureStore({
  reducer: {
    items: itemsSlice.reducer,
    fetchStatus: fetchStatusSlice.reducer,
    bag: bagSlice.reducer,
    auth: authSlice.reducer
  }
});

export default myntraStore;
