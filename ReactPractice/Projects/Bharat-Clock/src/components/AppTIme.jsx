function AppTime() {
  let time = new Date();
  return (
    <p>
      The current time is {time.toLocaleDateString()}-
      {time.toLocaleTimeString()}
    </p>
  );
}

export default AppTime;
