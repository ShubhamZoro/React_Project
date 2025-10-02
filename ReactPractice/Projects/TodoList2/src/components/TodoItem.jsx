function TodoItem({ todoName, todoDate }) {
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
          <button type="button" className="btn btn-danger kg-button">
            delete
          </button>
        </div>
      </div>
    </div>
  );
}

export default TodoItem;
