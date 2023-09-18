import axios from 'axios';

const URL_BASE = 'http://127.0.0.1:5000'

export const writeData = async (table, data) => {
  const augmentedData = {
    ...data,
    time: new Date().toISOString(),
  }

  const result = await axios.post(`${URL_BASE}/write`, { table, data: augmentedData })
  const json = result.json
  return json
}

export const queryData = async (table, key, value) => {
  const result = await axios.post(`${URL_BASE}/query`, { 
    table,
    key, 
    value 
  })
  console.log(result.data)
  return result.data
}

export const searchData = async (table, key, query) => {
  const result = await axios.get(`${URL_BASE}/search?table=${table}&key=${key}&query=${query}`, { 
    table, 
    key, 
    query
  })

  console.log(result.data)
  return result.data
}

export const runScraper = async (sport, scraper) => {
  const result = await axios.post(`${URL_BASE}/runscraper?sport=${sport}&scraper=${scraper}`)
  console.log(result.data)
  return result.data
}

export const getScrapedLines = async (scraper) => {
  // const result = await axios.get(`${URL_BASE}/getscrapedlines?scraper=${scraper}`)
  const result = await axios.get(`${URL_BASE}/getscrapedlineswithhistory?scraper=${scraper}`)
  console.log(result.data)
  return result.data
}

export const runOptimizer = async (sport, site, type, slateId) => {
  const result = await axios.post(`${URL_BASE}/optimize`,
  {
    sport,
    site,
    type,
    slateId
  })
  console.log(result.data)
  return result.data
}