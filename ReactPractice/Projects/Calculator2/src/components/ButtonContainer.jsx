import style from "./ButtonContainer.module.css";
import Buttons from "./Buttons";
function ButtonContainer({ put }) {
  return (
    <div className={style.buttonsContainer}>
      <Buttons put={put}></Buttons>
    </div>
  );
}

export default ButtonContainer;
