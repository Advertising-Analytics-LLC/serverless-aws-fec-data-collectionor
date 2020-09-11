module.exports.myDashboardBody = (serverless) => {
    const fsPromises = require('fs').promises
    return fsPromises.readFile('cloudwatch.json', 'utf-8')
};
