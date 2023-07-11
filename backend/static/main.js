// var socket = new WebSocket('ws://backend-lkpvidlwkq-as.a.run.app/get_gmji_data/20090118_064750/')

// socket.onmessage = function(e){
//     var data = JSON.parse(e.data);
//     console.log(data);

//     document.querySelector('#api').innerText = data[99]['E_data'];
// }

// socket.onclose = console.log('connection closed')

var socket = new WebSocket('ws://localhost:8000/get_gmji_data/20100208_112154/')

socket.onmessage = function(e){
    var data = JSON.parse(e.data);
    console.log(data);

    document.querySelector('#api').innerText = data[0];
}

socket.onclose = console.log('connection closed')


// var socket1 = new WebSocket('ws://localhost:8000/get_jagi_data/20120915_163224/')

// socket1.onmessage = function(e){
//     var data = JSON.parse(e.data);
//     console.log(data);

//     document.querySelector('#api1').innerText = data[0];
// }

// socket1.onclose = console.log('connection closed')

// var socket2 = new WebSocket('ws://localhost:8000/get_pwji_data/20120915_163224/')

// socket2.onmessage = function(e){
//     var data = JSON.parse(e.data);
//     console.log(data);

//     document.querySelector('#api2').innerText = data[0];
// }

// socket2.onclose = console.log('connection closed')

// var socket3 = new WebSocket('ws://localhost:8000/test_firebase/')

// socket3.onmessage = function(e){
//     var data = JSON.parse(e.data);
//     console.log(data);

//     document.querySelector('#api3').innerText = data;
// }

// socket3.onclose = console.log('connection closed')