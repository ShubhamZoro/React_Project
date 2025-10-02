const ErrorMessage = (props) => {
  let foodItems = props.fooditems;
  return <>{foodItems.length === 0 ? <h3>I am still hungry.</h3> : null}</>;
};

export default ErrorMessage;
