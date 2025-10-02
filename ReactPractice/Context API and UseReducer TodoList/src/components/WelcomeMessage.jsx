import { useContext } from "react";
import { TodoItemsContext } from "../store/todo-items-store";
const WelcomeMessage = () => {
  const { todos } = useContext(TodoItemsContext);
  return todos.length === 0 && <p>Enjoy Your Day</p>;
};

export default WelcomeMessage;
