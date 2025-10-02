import TodoItem from "./TodoItem";
import Styles from "./TodoItems.module.css";
const TodoItems = ({ todoitems }) => {
  if (!todoitems) {
    return <p>Loading todos</p>;
  }
  return (
    <div className={Styles.itemsContainer}>
      {todoitems.map((item, index) => (
        <TodoItem
          todoName={item.name}
          todoDate={item.date}
          key={index}
        ></TodoItem>
      ))}
    </div>
  );
};

export default TodoItems;
