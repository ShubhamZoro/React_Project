import { createContext } from "react";
import { useState, useReducer } from "react";
export const TodoItemsContext = createContext({
  todos: [],
  addtodo: () => {},
  deletetodo: () => {},
});

function todoItemsReducer(currTodoItems, action) {
  let newTodoItems = currTodoItems;
  if (action.type === "NEW_ITEM") {
    newTodoItems = [
      ...currTodoItems,
      { name: action.payload.itemName, date: action.payload.itemDueDate },
    ];
  } else if (action.type === "DELETE_ITEM") {
    newTodoItems = currTodoItems.filter(
      (item, index) => index !== action.payload.index
    );
  }
  return newTodoItems;
}

export const TodoItemsContextProvider = ({ children }) => {
  const [todos, dispatchtodos] = useReducer(todoItemsReducer, []);
  const addtodo = (itemName, itemDueDate) => {
    const newItemAction = {
      type: "NEW_ITEM",
      payload: {
        itemName,
        itemDueDate,
      },
    };
    dispatchtodos(newItemAction);
  };

  const deletetodo = (index) => {
    console.log(index);
    const deleteItemAction = {
      type: "DELETE_ITEM",
      payload: {
        index: index,
      },
    };
    dispatchtodos(deleteItemAction);
  };

  return (
    <TodoItemsContext.Provider value={{ todos, addtodo, deletetodo }}>
      {children}
    </TodoItemsContext.Provider>
  );
};
