
export class CSVParser {
  constructor(columns, indices) {
    this.columns = columns;
    this.indices = indices;
  }

  parse(content) {
    console.log("parse content123 213 123")

    const lines = content.split('\n')
    console.log(lines[0])

    const slate = lines.map((line) => {
      const parts = line.split(',')
    })
  }
}


//generic configurable csv parser
// configured FD parser by sport
// validation!