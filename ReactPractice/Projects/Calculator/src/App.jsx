import style from "./App.module.css";
import Dispaly from "./components/Display.jsx";
import ButtonContainer from "./components/ButtonContainer.jsx";
function App() {
  return (
    <div className={style.calculator}>
      <Dispaly></Dispaly>
      <ButtonContainer></ButtonContainer>
    </div>
  );
}

export default App;
