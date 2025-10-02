import { MdDelete } from "react-icons/md";
import { TodoItemsContext } from "../store/todo-items-store";
import { useContext } from "react";
function TodoItem({ todoName, todoDate, index }) {
  const { deletetodo } = useContext(TodoItemsContext);
  return (
    <div className="container">
      <div className="row kg-row">
        <div className="col-6">
          <p>{todoName}</p>
        </div>
        <div className="col-4">
          <p>{todoDate}</p>
        </div>
        <div className="col-2 ">
          <button
            type="button"
            className="btn btn-danger kg-button"
            onClick={() => deletetodo(index)}
          >
            <MdDelete />
          </button>
        </div>
      </div>
    </div>
  );
}

export default TodoItem;
