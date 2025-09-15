import {createSlice} from "@reduxjs/toolkit";

const bagSlice = createSlice({
  name: 'bag',
  initialState: [],
  reducers: {
    addInitialItems: (state, action) => {
      // replace with ids from server
      return Array.from(new Set(action.payload || []));
    },
    addToBag: (state, action) => {
      state.push(action.payload);
    },
    removeFromBag: (state, action) => {
      return state.filter(itemId => itemId !== action.payload);
    },
    clearBag: () => [],
  }
});

export const bagActions = bagSlice.actions;

export default bagSlice;