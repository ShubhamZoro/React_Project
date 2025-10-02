import { useContext } from "react";
import { TodoItemsContext } from "../store/todo-items-store";
import TodoItem from "./TodoItem";
import Styles from "./TodoItems.module.css";
const TodoItems = () => {
  const { todos } = useContext(TodoItemsContext);
  if (!todos) {
    return <p>Loading todos</p>;
  }
  console.log(todos);
  return (
    <div className={Styles.itemsContainer}>
      {todos.map((item, index) => (
        <TodoItem
          todoName={item.name}
          todoDate={item.date}
          index={index}
          key={index}
        ></TodoItem>
      ))}
    </div>
  );
};

export default TodoItems;
