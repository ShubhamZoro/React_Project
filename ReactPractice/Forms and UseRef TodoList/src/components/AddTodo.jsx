import { IoIosAddCircle } from "react-icons/io";

function AddTodo({ addtodo, name, date }) {
  return (
    <div className="container text-center">
      <form className="row kg-row" onSubmit={addtodo}>
        <div className="col-6">
          <input type="text" ref={name} placeholder="Enter Todo Here"></input>
        </div>
        <div className="col-4">
          <input type="date" ref={date}></input>
        </div>
        <div className="col-2">
          <button className="btn btn-outline-success">
            <IoIosAddCircle />
          </button>
        </div>
      </form>
    </div>
  );
}

export default AddTodo;
