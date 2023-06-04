const { Configuration, OpenAIApi } = require("openai");
const express = require('express')

const bodyParser = require("body-parser")
const cors = require("cors")


const configuration = new Configuration({
    organization: "org-IiDETrymjMY47q3ahq5I5f2r",
    apiKey: "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",
});
const openai = new OpenAIApi(configuration);
// const response = await openai.listEngines();


// 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

const app = express()

app.use(bodyParser.json())
app.use(cors())
// app.use(express.json())
// app.use(express.urlencoded({ extended: true }))
const port = 3080


app.post('/',async (req,res) => {

    const { message } = req.body;

    console.log(message);

    const response = await openai.createCompletion({
        model: "text-davinci-003",
        prompt: `${message}`,
        max_tokens: 1000,
        temperature: 0.5,
    });
    // console.log(response.data.choices[0].text);
    res.json({
        // data : response.data
        message : response.data.choices[0].text,
    })
});

app.listen(port, () => {
    console.log(`example app listening at http://localhost:${port}`)
});