
//Setup websocket
const sio = io.connect('http://localhost:5000');

//Setup local storage for each signal
localStorage.setItem("airTime", JSON.stringify([]))
localStorage.setItem("landingTime", JSON.stringify([]))
localStorage.setItem("totalRot", JSON.stringify([]))
localStorage.setItem("jumpMid", JSON.stringify([]))
localStorage.setItem("toeHeavy", JSON.stringify([]))


const startDateInp = document.getElementById('start-date');
const endDateInp = document.getElementById('end-date');
const chartTypeMenu = document.getElementById('selectSession');
var chartType = "airTime";

const CATEGORIESchart = {
  'Air Time': 'airTime',
  'Landing Time': 'landingTime',
  'Rotation': 'totalRot',
  'Peak Rotation': 'jumpMid',
  'Toe Heavy': 'toeHeavy'
};

//Test signal 
 var testAirTime = [[1, 10],[2, 12]];
 localStorage.setItem("airTime", JSON.stringify(testAirTime))
 var testLandTime = [[1, 3],[2, 1]];
 localStorage.setItem("landingTime", JSON.stringify(testLandTime))
// console.log(localStorage.getItem("airTime"))

//Websocket events
sio.on('connect',function() {
    console.log('Client has connected to the server!');
});

sio.on('msg',function(data) {
    console.log('Received a message from the server!', data);
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


//Listen to which chart the user wants
chartTypeMenu.addEventListener('blur', () => setTimeout(() => {  
  var chartType = CATEGORIESchart[document.querySelector('.select input[type=radio]:checked + label').innerHTML.trim()];
  console.log(JSON.parse(localStorage.getItem(chartType)));
  document.getElementById('jump-graph').innerHTML = "";
  drawChart();
}, 100));

//Process data from database
sio.on('databaseReturn', function(data){
  localStorage.clear();
  localStorage.setItem("airTime", JSON.stringify(data.ladning_time))
  localStorage.setItem("landingTime", JSON.stringify(storedSignals2))
  localStorage.setItem("totalRot", JSON.stringify(storedSignals3))
  localStorage.setItem("jumpMid", JSON.stringify(storedSignals4))
  localStorage.setItem("toeHeavy", JSON.stringify(storedSignals5))
  document.getElementById('jump-graph').innerHTML = "";
  drawChart();
});

//When the date changes, request info from database
startDateInp.addEventListener('change', (event) => {
  var startDateVal = startDateInp.value;
  var endDateVal = endDateInp.value;
  sio.send("["+startDateVal+","+endDateVal+"]");
});

endDateInp.addEventListener('change', (event) => {
  var startDateVal = startDateInp.value;
  var endDateVal = endDateInp.value;
  sio.send("["+startDateVal+","+endDateVal+"]");
});

var intervalId = window.setInterval(function(){
  sio.emit('getData', "any");
}, 5000);


// var dictTest = {air_time: 0.6649265289306641, landing_time: 1.8953299522399902, total_rotation: 2.3961387153069174, jump_midpoint: 11.173666666666668, isToeHeavy: false}
// document.getElementById("airTime").innerHTML = "Air Time: " + dictTest.air_time + "s";
// document.getElementById("landingTime").innerHTML = "Landing Time: " + dictTest.landing_time + "s";
// document.getElementById("totalRot").innerHTML = "Rotation: " + dictTest.total_rotation + "rad";
// document.getElementById("jumpMid").innerHTML = "Jump Midpoint: " + dictTest.jump_midpoint + "s";
// document.getElementById("toeHeavy").innerHTML = "Toe heavy jump: " + dictTest.isToeHeavy;

//Transforming input data



google.charts.load('current', {'packages':['line']});
google.charts.setOnLoadCallback(drawChart);
var chart, data;


function drawChart() {
  if(chart!=undefined){
    chart.clearChart();
    data =[];
    chart.data = [];
    console.log(chart);
  }
  data = new google.visualization.DataTable();
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
  data.addRows(JSON.parse(localStorage.getItem(chartType)));

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

  chart = new google.charts.Line(document.getElementById('jump-graph'));

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
