import style from "./Dispaly.module.css";
function Dispaly({ text }) {
  return (
    <input className={style.display} type="text" value={text} readOnly></input>
  );
}

export default Dispaly;
