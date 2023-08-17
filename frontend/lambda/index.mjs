import { DynamoDBDocument } from "@aws-sdk/lib-dynamodb";
import { DynamoDB } from "@aws-sdk/client-dynamodb";
//import AWS from '/var/runtime/node_modules/aws-sdk/lib/aws.js'

const ddb = DynamoDBDocument.from(new DynamoDB({ region: 'us-east-1' }));


const updateRow = async (summary, row) => {
    const description = row.description.S
    const title = row.title.S
    const uuid = row.uuid.S
    const epigraph = row.epigraph.S
    console.log('-----')
    console.log(row)
    console.log(uuid)
    console.log(epigraph)
    console.log("update row", title)
  
   const params = {
        TableName: 'AIGhostWriter',
        Item: {
            uuid,
            title,
            description,
            epigraph,
            summary
        }
    };

    // Call DynamoDB to add the item to the table
    try {
        const data = await ddb.put(params);
        console.log("Item successfully stored:", data);
    } catch (err) {
      console.log("Error: ", err);
        console.error("Error: ", err);
    }
}

const getOutline = async (title, description) => {
  const chapterCount = Math.floor(Math.random() * 5) + 3;

  const openAIResponse = await fetch('https://api.openai.com/v1/completions', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': 'Bearer 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'
    },

    
    body: JSON.stringify({
      'model': 'text-davinci-003',
      "prompt": `The following is an extremely detailed summary of all ${chapterCount} chapters from the book "${title}". Each chapter is given with its title followed by an extremely detailed description of that chapter's contents. "${title}" has been described as follows:\n\n${description}\n\nBook summary:`,
      'temperature': 1,
      'max_tokens': 1005,
      'top_p': 1,
      'frequency_penalty': 0,
      'presence_penalty': 0
    })
  });

  return openAIResponse
}

export const handler = async(event) => {
  // TODO implement
  
  const inserts = event.Records.filter((record) => record.eventName === 'INSERT')
  for(var i = 0; i < inserts.length; i += 1) {
      const insert = inserts[i];

      console.log(insert.dynamodb)
      
      const newImage = insert.dynamodb.NewImage
      
      const description = newImage.description.S
      const title = newImage.title.S
      
      const openAIResponse = await getOutline(title, description)
      const asJson = await openAIResponse.json()
      console.log(asJson)
      const outline = asJson['choices'][0]['text']
      
      console.log(outline)
      await updateRow(outline, newImage)
  }
  
  
  const response = {
      statusCode: 200,
      body: JSON.stringify('Hello from Lambda!'),
  };
  return response;
};
