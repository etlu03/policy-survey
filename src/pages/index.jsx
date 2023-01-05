import { useEffect, useState } from 'react';

function index() {
  const [render, setRender] = useState(true)
  useEffect(() => setRender(false), [])

  return !render ? <p> I was rendered by the client </p> : null 
}

export default index;