import { useEffect, useState } from 'react';

/*
if (typeof window === 'undefined') {
  return true
} else {
  return false
}
*/

function index() {
  const [render, setRender] = useState(true)
  useEffect(() => setRender(false), [])

  return <div> {!render ? <p> I was rendered by the client </p> : null} </div> 
}

export default index;