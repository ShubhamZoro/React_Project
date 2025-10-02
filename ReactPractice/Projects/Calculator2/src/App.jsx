import style from "./App.module.css";
import Dispaly from "./components/Display.jsx";
import ButtonContainer from "./components/ButtonContainer.jsx";
import { useState } from "react";
function App() {
  let [text, settext] = useState("");
  function put(item) {
    let result = text + item;

    if (item === "=") {
      try {
        // remove the "=" sign before evaluating
        const expression = text;
        result = Function("return " + expression)();
      } catch (e) {
        result = "Error";
      }
    }
    if (item === "C") {
      settext("");
      return;
    }

    settext(result.toString());
  }
  return (
    <div className={style.calculator}>
      <Dispaly text={text}></Dispaly>
      <ButtonContainer put={put}></ButtonContainer>
    </div>
  );
}

export default App;
