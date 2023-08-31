import Papa from 'papaparse';
import { writeData, queryData, searchData } from './apiHelper';

export class CSVParser {
  constructor(columns, indices, skipRows) {
    this.columns = columns;
    this.indices = indices;
    this.skipRows = skipRows;
  }

  parse(content) {
    const result = Papa.parse(content)
    const mappedVals = result.data.map((row) => {
      const vals = this.indices.map((index) => {
        return row[index]
      })

      return vals
    })

    this.mappedVals = mappedVals.slice(this.skipRows)
    return this
  }

  areRowsEqual(row1, row2) {
    let toReturn = true
    this.columns.forEach((column) => {
      if(row1[column] !== row2[column]) {
        toReturn = false
      }
    })

    return toReturn
  }

  async upload(slateId, date, tableName) {
    const existingRows = await queryData(tableName, 'slateId', slateId)
    const existingRowsParsed = existingRows.reduce((acc, val) => {
      acc[val.playerId] = val
      return acc
    }, {})

    for(var i = 0; i < this.mappedVals.length; i++) {
      const row = this.mappedVals[i]
      const toWrite = this.columns.reduce((acc, val, index) => {
        acc[val] = row[index]
        return acc
      }, {})

      toWrite.slateId = slateId
      toWrite.slateDay = date

      const existingRow = existingRowsParsed[toWrite.playerId]
      const isRowNew = !existingRow || !this.areRowsEqual(existingRow, toWrite)
      if(!existingRow || isRowNew) {
        console.log("WRITING ROW", toWrite)
        await writeData(tableName, toWrite)
      }
    }
  }
}

export class FDParser {
  constructor() {
    this.parser = new CSVParser(
      ['playerId', 'position', 'name', 'salary', 'game', 'team', 'injury'],
      [0, 1, 3, 7, 8, 9, 11],
      1
    )

    this.tableName = 'FDSlatePlayers'
  }

  parse(content) {
    return this.parser.parse(content)
  }

  async upload(slateId, date, sport) {
    await this.parser.upload(slateId, date, `${this.tableName}_${sport}`)
  }
}

export class DKParser {
  constructor() {
    this.parser = new CSVParser(
      ['position', 'name', 'playerId', 'salary', 'game', 'team'],
      [0, 2, 3, 5, 6, 7],
      1
    )

    this.tableName = 'DKSlatePlayers'
  }

  parse(content) {
    return this.parser.parse(content)
  }

  async upload(slateId, date, sport) {
    await this.parser.upload(slateId, date, `${this.tableName}_${sport}`)
  }
}

//generic configurable csv parser
// configured FD parser by sport
// validation!