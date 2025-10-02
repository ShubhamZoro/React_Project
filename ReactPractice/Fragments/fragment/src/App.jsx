import "./App.css";
import "bootstrap/dist/css/bootstrap.min.css";
import FoodItems from "./components/FoodItems";
import ErrorMessage from "./components/ErrorMessages";
import Container from "./components/container";
import FoodInput from "./components/FoodInput";
import { useState } from "react";
function App() {
  const [FoodItem, setFoodItem] = useState([
    "Dal",
    "Green Vegetables",
    "Fruits",
    "Milk",
    "Roti",
    "Rice",
  ]);
  let texttoshow = "Food Item Enter by User";
  function handleKeyDown(event) {
    if (event.key === "Enter") {
      setFoodItem((FoodItem) => [...FoodItem, event.target.value]);
    }
  }
  return (
    <>
      <Container>
        <h1>Healthy Food</h1>
        <FoodInput handleKeyDown={handleKeyDown}></FoodInput>
        <ErrorMessage fooditems={FoodItem}></ErrorMessage>
        <FoodItems fooditems={FoodItem}></FoodItems>
      </Container>

      <Container>
        <p>Above is the list of Healthy food that are goods for your health.</p>
      </Container>
    </>
  );
}

export default App;
