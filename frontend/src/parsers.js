import Papa from 'papaparse';

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

    console.log(mappedVals)

    this.mappedVals = mappedVals.slice(this.skipRows)
    return this
  }
}

export class FDParser {
  constructor() {
    this.parser = new CSVParser(
      ['id', 'position', 'name', 'salary', 'game', 'injury'],
      [0, 1, 3, 7, 8, 11],
      1
    )
  }

  parse(content) {
    return this.parser.parse(content)
  }
}

//generic configurable csv parser
// configured FD parser by sport
// validation!