const chatSocket = new WebSocket('ws://'+window.location.host+'/ws/connect_system/');

chatSocket.onmessage = function(e){
    console.log("connection established");
}

chatSocket.onclose=function(e){
    console.error('Chat socket closed unexpectedly');
}

