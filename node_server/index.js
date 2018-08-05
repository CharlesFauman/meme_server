const express = require('express');
const path = require('path');
const fs = require('file-system');



const app = express();

/*
const server = require('https').createServer({ 
    key: fs.readFileSync('privatekey.pem'),
    cert: fs.readFileSync('certificate.pem') 
 },app);
 */
 const server = require('http').Server(app);


 const io = require('socket.io')(server);

 const request = require('request')
 require('request-to-curl');



 let rooms = 0;

 app.use(express.static('.'));

 app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'game.html'));
});

 io.on('connection', (socket) => {
    var socket_id = socket.id;
    var client_ip = socket.request.connection.remoteAdress;

    socket.on('request_predictions', (data) => {

        var formData = {
            input : data.text
        }

        request.post({url:'http://localhost:5000/predict', formData: formData}, function(err, httpResponse, body) {
            if (err) {
                //
            }else if(JSON.parse(body).hasOwnProperty('predictions')){
                socket.emit('receive_predictions', { predictions : JSON.parse(body).predictions })
            }
        });
        
    });



});

//server.listen(80);
server.listen(80);