import TodoItem from "./TodoItem";
import Styles from "./TodoItems.module.css";
const TodoItems = ({ todoitems, deletetodo }) => {
  if (!todoitems) {
    return <p>Loading todos</p>;
  }
  return (
    <div className={Styles.itemsContainer}>
      {todoitems.map((item, index) => (
        <TodoItem
          todoName={item.name}
          todoDate={item.date}
          deletetodo={deletetodo}
          index={index}
          key={index}
        ></TodoItem>
      ))}
    </div>
  );
};

export default TodoItems;
