import AppName from "./components/AppHeading";
import AppDescription from "./components/AppDescription";
import AppTime from "./components/AppTIme";
import "bootstrap/dist/css/bootstrap.min.css";
import "./App.css";
function App() {
  return (
    <center>
      <AppName></AppName>
      <AppDescription></AppDescription>
      <AppTime></AppTime>
    </center>
  );
}

export default App;
