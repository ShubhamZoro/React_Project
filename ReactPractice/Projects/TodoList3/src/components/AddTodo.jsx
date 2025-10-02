import { IoIosAddCircle } from "react-icons/io";
function AddTodo({ addtodo, fillname, filldate, name, date }) {
  return (
    <div className="container text-center">
      <div className="row kg-row">
        <div className="col-6">
          <input
            type="text"
            placeholder="Enter Todo Here"
            value={name}
            onChange={fillname}
          ></input>
        </div>
        <div className="col-4">
          <input type="date" value={date} onChange={filldate}></input>
        </div>
        <div className="col-2">
          <button
            type="button"
            className="btn btn-outline-success"
            onClick={addtodo}
          >
            <IoIosAddCircle />
          </button>
        </div>
      </div>
    </div>
  );
}

export default AddTodo;
