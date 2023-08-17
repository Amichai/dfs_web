import axios from 'axios';

export const writeData = async (table, data) => {
  const augmentedData = {
    ...data,
    time: new Date().toISOString(),
  }

  const result = await axios.post('http://127.0.0.1:5000/write', { table, data: augmentedData })
  const json = result.json
  console.log(json)
  return json
}

export const queryData = async (table, key, value) => {
  const result = await axios.post('http://127.0.0.1:5000/query', { 
    table,
    key, 
    value 
  })
  console.log(result.data)
  return result.data
}

export const searchData = async (table, key, query) => {
  const result = await axios.get(`http://127.0.0.1:5000/search?table=${table}&key=${key}&query=${query}`, { 
    table, 
    key, 
    query
  })

  console.log(result.data)
  return result.data
}