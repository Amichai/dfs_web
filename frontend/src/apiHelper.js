import { v4 as uuidv4 } from 'uuid'

export const getTitles = async (description) => {
  var myHeaders = new Headers()
  myHeaders.append('Content-Type', 'application/json')

  var raw = JSON.stringify({
    description
  })

  var requestOptions = {
    method: 'POST',
    headers: myHeaders,
    body: raw,
    redirect: 'follow'
  }

  const response = await fetch(
    'https://i27f13a1be.execute-api.us-east-1.amazonaws.com/dev/titles',
    requestOptions
  )
  const result = await response.json()

  return result
}

export const getEpigraphs = async (description, title) => {
  var myHeaders = new Headers()
  myHeaders.append('Content-Type', 'application/json')

  var raw = JSON.stringify({
    titleAndDescription: {
      title,
      description
    }
  })

  var requestOptions = {
    method: 'POST',
    headers: myHeaders,
    body: raw,
    redirect: 'follow'
  }

  const response = await fetch(
    'https://i27f13a1be.execute-api.us-east-1.amazonaws.com/dev/titles',
    requestOptions
  )
  const result = await response.json()

  return result
}

export const uploadBook = async (description, title, epigraph) => {
  const id = uuidv4()
  let data = {
    uuid: id,
    description: encodeURIComponent(description),
    title: encodeURIComponent(title),
    epigraph: encodeURIComponent(epigraph)
  }

  fetch('https://i27f13a1be.execute-api.us-east-1.amazonaws.com/dev/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    // body: JSON.stringify(data),
    body: JSON.stringify(data)
  })
    .then((response) => response.json())
    .then((data) => console.log('Success:', data))
    .catch((error) => console.error('Error:', error))

  return id
}
