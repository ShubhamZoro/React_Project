import { IoIosAddCircle } from "react-icons/io";
import { useContext } from "react";
import { TodoItemsContext } from "../store/todo-items-store";
function AddTodo({ name, date }) {
  const { addtodo } = useContext(TodoItemsContext);

  return (
    <div className="container text-center">
      <div className="row kg-row">
        <div className="col-6">
          <input type="text" ref={name} placeholder="Enter Todo Here"></input>
        </div>
        <div className="col-4">
          <input type="date" ref={date}></input>
        </div>
        <div className="col-2">
          <button
            className="btn btn-outline-success"
            onClick={() => addtodo(name.current.value, date.current.value)}
          >
            <IoIosAddCircle />
          </button>
        </div>
      </div>
    </div>
  );
}

export default AddTodo;
