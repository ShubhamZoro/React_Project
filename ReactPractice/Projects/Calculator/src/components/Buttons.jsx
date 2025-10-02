import style from "./Buttons.module.css";

function Buttons() {
  const buttonNames = [
    "C",
    "1",
    "2",
    "+",
    "3",
    "4",
    "-",
    "5",
    "6",
    "*",
    "7",
    "8",
    "/",
    "=",
    "9",
    "0",
    "1",
  ];
  return (
    <>
      {buttonNames.map((item, index) => (
        <button className={style.button} key={index}>
          {item}
        </button>
      ))}
    </>
  );
}

export default Buttons;
