import { useDispatch } from "react-redux";
import { useRef } from "react";

function Controls() {
  const dispatch = useDispatch();
  const inputElement = useRef();
  function handleIncrement() {
    dispatch({ type: "INCREMENT" });
  }
  function handleDecrement() {
    dispatch({ type: "DECREMENT" });
  }

  function handleAdd() {
    dispatch({
      type: "ADD",
      payload: {
        num: Number(inputElement.current.value),
      },
    });
    inputElement.current.value = "";
  }

  function handleSubtract() {
    dispatch({
      type: "SUBTRACT",
      payload: {
        num: Number(inputElement.current.value),
      },
    });
    inputElement.current.value = "";
  }

  function handlePrivacyToggle() {
    dispatch({ type: "PRIVACY_TOGGLE" });
  }
  return (
    <>
      <div className="d-grid gap-2 d-sm-flex justify-content-sm-center">
        <button
          type="button"
          className="btn btn-primary "
          onClick={handleIncrement}
        >
          +1
        </button>
        <button
          type="button"
          className="btn btn-success"
          onClick={handleDecrement}
        >
          -1
        </button>
        <button
          type="button"
          className="btn btn-warning"
          onClick={handlePrivacyToggle}
        >
          Privacy Toogle
        </button>
      </div>

      <div className="d-grid gap-2 d-sm-flex justify-content-sm-center control-row">
        <input
          type="text"
          ref={inputElement}
          className="number-input"
          placeholder="Enter number"
        />

        <button type="button" className="btn btn-info" onClick={handleAdd}>
          Add
        </button>

        <button
          type="button"
          className="btn btn-danger"
          onClick={handleSubtract}
        >
          Subtract
        </button>
      </div>
    </>
  );
}

export default Controls;
