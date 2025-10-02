import {createStore} from "redux"
const INITIAL_VALUE={
  counter:0,
  privacy:false
}
function counterReducer(store=INITIAL_VALUE,action){
  let newStore=store.counter
  if(action.type==="INCREMENT"){
    newStore=newStore+1
  }
  else if(action.type==="DECREMENT"){
    newStore-=1
  }
  else if(action.type==="ADD"){
    newStore+=action.payload.num;
  }
  else if(action.type==='SUBTRACT'){
    newStore-=action.payload.num;
  }
  else if(action.type==="PRIVACY_TOGGLE"){
    return {...store,privacy:!store.privacy}
  }
  return {...store,counter:newStore}
}

const counterStore=createStore(counterReducer)


export default counterStore