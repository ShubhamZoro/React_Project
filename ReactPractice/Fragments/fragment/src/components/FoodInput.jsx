import styles from "./FoodInput.module.css";
function FoodInput({ handleKeyDown }) {
  return (
    <input
      className={styles.foodInfo}
      placeholder="Enter Food Here"
      type="text"
      onKeyDown={handleKeyDown}
    ></input>
  );
}

export default FoodInput;
