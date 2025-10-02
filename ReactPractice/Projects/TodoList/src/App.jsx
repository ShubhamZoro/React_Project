import AppName from "./components/AppName";
import AddTodo from "./components/AddTodo";
import TodoItem1 from "./components/TodoItem1";
import TodoItem2 from "./components/TodoItem2";
import "./App.css";

function App() {
  return (
    <center className="todo-container">
      <AppName></AppName>
      <AddTodo></AddTodo>
      <div className="items-container">
        <TodoItem1></TodoItem1>
        <TodoItem2></TodoItem2>
        <TodoItem1></TodoItem1>
      </div>
    </center>
  );
}

// import { useState } from "react";

// function App() {
//   const [todoList, settodoList] = useState([]);
//   const [todo, settodo] = useState("");
//   const [date, setdate] = useState(new Date());

//   function fillstate() {
//     settodoList((todoList) => [...todoList, { text: todo, date: date }]);
//     console.log(todoList);
//   }

//   function text(event) {
//     settodo(event.target.value);
//     console.log(event.target.value);
//   }

//   function date_set(event) {
//     setdate(event.target.value);
//     console.log(event.target.value);
//   }

//   return (
//     <center className="todo-container">
//       <h1>Todo App</h1>
//       <div className="container text-center">
//         <div className="row">
//           <div className="col-6">
//             <input
//               type="text"
//               placeholder="Enter Todo Here"
//               value={todo}
//               onChange={text}
//             ></input>
//           </div>
//           <div className="col-4">
//             <input type="date" value={date} onChange={date_set}></input>
//           </div>
//           <div className="col-2">
//             <button
//               type="button"
//               className="btn btn-outline-success"
//               onClick={fillstate}
//             >
//               Add
//             </button>
//           </div>
//         </div>

//         {todoList.map((item, index) => (
//           <div className="row">
//             <div className="col-6">
//               <p key={index}>{item.text}</p>
//             </div>
//             <div className="col-4">
//             <p key={index}>{item.date}</p>
//             </div>
//             <div className="col-2">
//               <button type="button" className="btn btn-outline-success" key={index}>
//                 delete
//               </button>
//             </div>
//           </div>
//         ))}
//  </div>
//     </center>
//   );
// }

export default App;
