import styles from "./Item.module.css";
const Item = ({ FoodItems, bought, handleBuyButton, Index }) => {
  return (
    <li
      className={`${styles["kg-item"]} list-group-item ${bought && "active"}`}
      key={Index}
    >
      <span className={styles["kg-span"]}>{FoodItems}</span>
      <button
        className={`${styles.button} btn btn-info`}
        onClick={handleBuyButton}
      >
        Buy
      </button>
    </li>
  );
};

export default Item;
