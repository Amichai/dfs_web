export const getDateString = () => {
  const date = new Date()
  const year = date.getFullYear()
  const month = `${date.getMonth() + 1}`.padStart(2, '0')
  const day = `${date.getDate()}`.padStart(2, '0')

  return `${year}-${month}-${day}`
}

export const teamToStartTime = (startTimes) => {
  return Object.entries(startTimes).reduce((acc, kv) => {
    const startTime = kv[0].includes('.5') 
      ? kv[0].split('.')[0] + ":30pm ET"
      : kv[0] + ":00pm ET"
    kv[1].forEach((team) => acc[team] = startTime)
    return acc
  }, {})
}