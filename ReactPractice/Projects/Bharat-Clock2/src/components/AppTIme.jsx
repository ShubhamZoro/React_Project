import { useState } from "react";
import { useEffect } from "react";

function AppTime() {
  const [time, settime] = useState(new Date());
  useEffect(() => {
    console.log("Interval has been setup");
    const intervalId = setInterval(() => {
      settime(new Date());
    }, 1000);

    return () => {
      clearInterval(intervalId);
      console.log("cancelled");
    };
  }, []);

  return (
    <p>
      The current time is {time.toLocaleDateString()}-
      {time.toLocaleTimeString()}
    </p>
  );
}

export default AppTime;
