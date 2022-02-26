

const sio = io.connect('http://localhost:5000');
localStorage.setItem("airTime", JSON.stringify([]))
localStorage.setItem("landingTime", JSON.stringify([]))
localStorage.setItem("totalRot", JSON.stringify([]))
localStorage.setItem("jumpMid", JSON.stringify([]))
localStorage.setItem("toeHeavy", JSON.stringify([]))

// var testAirTime = [[1, 10],[2, 12]];
// localStorage.setItem("airTime", JSON.stringify(testAirTime))
// console.log(localStorage.getItem("airTime"))

sio.on('connect',function() {
    console.log('Client has connected to the server!');
});

sio.on('msg',function(data) {
    console.log('Received a message from the server!', data);
    updateValues(data);
});

sio.on('disconnect',function() {
    console.log('The client has disconnected!');
});

sio.on('getData',function() {
    console.log('Got data from the server!');
});

sio.on('setData',function(data) {
  console.log('Received a message from the server!', data);
  var storedSignals1 = JSON.parse(localStorage.getItem("airTime"))
  var storedSignals2 = JSON.parse(localStorage.getItem("landingTime"))
  var storedSignals3 = JSON.parse(localStorage.getItem("totalRot"))
  var storedSignals4 = JSON.parse(localStorage.getItem("jumpMid"))
  var storedSignals5 = JSON.parse(localStorage.getItem("toeHeavy"))
  storedSignals1.push([storedSignals1.length(), data.air_time])
  storedSignals2.push(data.ladning_time)
  storedSignals3.push(data.total_rotation)
  storedSignals4.push(data.jump_midpoint)
  storedSignals5.push(data.isToeHeavy)
  localStorage.setItem("airTime", JSON.stringify(storedSignals1))
  localStorage.setItem("landingTime", JSON.stringify(storedSignals2))
  localStorage.setItem("totalRot", JSON.stringify(storedSignals3))
  localStorage.setItem("jumpMid", JSON.stringify(storedSignals4))
  localStorage.setItem("toeHeavy", JSON.stringify(storedSignals5))
  
  drawChart()
});

var intervalId = window.setInterval(function(){
  sio.emit('getData', "any");
}, 5000);

function updateValues(data){
  document.getElementById("airTime").innerHTML = "Air Time: " + dictTest.air_time + "s";
  document.getElementById("landingTime").innerHTML = "Landing Time: " + dictTest.landing_time + "s";
  document.getElementById("totalRot").innerHTML = "Rotation: " + dictTest.total_rotation + "rad";
  document.getElementById("jumpMid").innerHTML = "Jump Midpoint: " + dictTest.jump_midpoint + "s";
  document.getElementById("toeHeavy").innerHTML = "Toe heavy jump: " + dictTest.isToeHeavy;
}

// var dictTest = {air_time: 0.6649265289306641, landing_time: 1.8953299522399902, total_rotation: 2.3961387153069174, jump_midpoint: 11.173666666666668, isToeHeavy: false}
// document.getElementById("airTime").innerHTML = "Air Time: " + dictTest.air_time + "s";
// document.getElementById("landingTime").innerHTML = "Landing Time: " + dictTest.landing_time + "s";
// document.getElementById("totalRot").innerHTML = "Rotation: " + dictTest.total_rotation + "rad";
// document.getElementById("jumpMid").innerHTML = "Jump Midpoint: " + dictTest.jump_midpoint + "s";
// document.getElementById("toeHeavy").innerHTML = "Toe heavy jump: " + dictTest.isToeHeavy;

//Transforming input data



google.charts.load('current', {'packages':['line']});
google.charts.setOnLoadCallback(drawChart);

function drawChart() {

  var data = new google.visualization.DataTable();
  data.addColumn('number', 'Jump');
  data.addColumn('number', 'Air time');
  // data.addColumn('number', 'Spin');

  // var signalArr = localStorage.getItem("airTime");
  // var inputChart = "";
  // for(var i=1; i<=signalArr.length; i++){
  //   chartArray+="["+i+", "+signalArr[i]+"]"
  //   if(i!=signalArr.length)chartArray+=",";
  // }
//  localStorage.getItem("airTime")
  data.addRows(JSON.parse(localStorage.getItem("airTime")));

  // data.addRows([
  // [1,  37.8],
  // [2,  30.9],
  // [3,  25.4],
  // [4,  11.7],
  // [5,  11.9],
  // [6,   8.8],
  // [14,  4.2]
  // ]);

  var options = {
    chart: {
      title: 'Sensors output vs time'
    },
    width: 650,
    height: 350
    // series: {
    //   // Gives each series an axis name that matches the Y-axis below.
    //   0: {axis: 'Force'},
    //   1: {axis: 'Spin'}
    // },
    // axes: {
    //   // Adds labels to each axis; they don't have to match the axis names.
    //   y: {
    //     Force: {label: 'Force (N)'},
    //     Spin: {label: 'Spin (radians'}
    //   }
    // }
  };

  var chart = new google.charts.Line(document.getElementById('jump-graph'));

  chart.draw(data, google.charts.Line.convertOptions(options));
}



// const mySocket = new WebSocket('ws://localhost:8082');

// // Connection opened
// mySocket.addEventListener('open', function (event) {
//     mySocket.send('Opened server!');
// });

// // Listen for messages
// mySocket.addEventListener('message', function (event) {
//     console.log('Message from server: ', event.data);
// });

// var options = {
//   fontName: "'Rubik', sans-serif",
//   backgroundColor: "#FAFCFE",
//   chartAre: {top: 100},
//   tooltip: {textStyle: {color: '#000000'}, showColorCode: false},
//   legend: {position:'bottom'},
//   fontSize: 18,
//   width: 650,
//   height: 350
// };
