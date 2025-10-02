import { useState } from "react";
import Item from "./Items";
function FoodItems(props) {
  let foodItems = props.fooditems;
  let [active, setactive] = useState([]);
  const onBuyButton = (item, index) => {
    setactive((active) => [...active, index]);
    console.log(`${item} item being bought`);
  };
  return (
    <ul className="list-group ">
      {foodItems.map((item, index) => (
        <Item
          FoodItems={item}
          Index={index}
          bought={active.includes(index)}
          handleBuyButton={() => onBuyButton(item, index)}
        ></Item>
      ))}
    </ul>
  );
}

export default FoodItems;
