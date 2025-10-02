import style from "./ButtonContainer.module.css";
import Buttons from "./Buttons";
function ButtonContainer() {
  return (
    <div className={style.buttonsContainer}>
      <Buttons></Buttons>
    </div>
  );
}

export default ButtonContainer;
