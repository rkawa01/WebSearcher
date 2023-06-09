const express = require('express')
const path = require('path');
const app = express();
const { spawn } = require('child_process');
// const helmet = require("helmet");
const cors = require('cors')
const bodyParser = require('body-parser')

const PORT = process.env.PORT || 3000;
const PYTHON = process.env.PYTHON || 'python3.11';

// Define middleware
app.use(cors());
app.use(express.json());
const urlencodedParser = bodyParser.urlencoded({ extended: false })
app.use(express.static(path.join(__dirname, 'public')));
app.post('/search', urlencodedParser, function (req, res)  {
    
        // Get body
        const top = req.body?.top ? req.body.top : 10;
        console.log(req.body)
        const query = req.body?.query ? req.body.query : "math";
        console.log(query)
        console.log(top)
        // Run search.py and return results
        const pyProg = spawn(PYTHON, ['./search.py', query, top]);

        let receivedData = ""
        let errorData = "";

        pyProg.stdout.on('data', (data) => {
            try {
                receivedData += data.toString();
            } catch (error) {
                res.status(500).send({ error })
            }
        });
        pyProg.stderr.on('data', (data) => {
            try {
                errorData += data.toString();
            } catch (error) {
                res.status(500).send({ error })
            }
        });
        pyProg.on('close', (code) => {
            if (code || errorData) {
                return res.status(500).send({ error: errorData })
            }
            res.send(JSON.parse(receivedData))
        });
});

app.get('*', async (req, res) => {
    res.sendFile(path.join(__dirname, './index.html'))
})

app.listen(PORT, () => {
    console.log(`Server running on port ${PORT}`);
});