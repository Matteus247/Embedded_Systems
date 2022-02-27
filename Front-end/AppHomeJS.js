
//Setup websocket
const sio = io.connect('http://localhost:5000');

//Setup local storage for each signal
localStorage.setItem("airTime", JSON.stringify([]))
localStorage.setItem("landingTime", JSON.stringify([]))
localStorage.setItem("totalRot", JSON.stringify([]))
localStorage.setItem("jumpMid", JSON.stringify([]))
localStorage.setItem("toeHeavy", JSON.stringify([]))

var performanceDivWidth = document.getElementsByClassName('performance-box')[0].offsetWidth;

const startDateInp = document.getElementById('start-date');
const endDateInp = document.getElementById('end-date');
const chartTypeMenu = document.getElementById('selectSession');
var chartType = "airTime";

var dbDate = {
  startDate: startDateInp.value,
  endDate: endDateInp.value
}

//Used to map the selected chart type from front-end menu to the local storage signals
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


//When receiving one jump that needs to be added to the local storage
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
  
  //Clear previous chart and draw the new one
  document.getElementById('jump-graph').innerHTML = "";
  drawChart();
});


//Listen to which chart the user wants
chartTypeMenu.addEventListener('blur', () => setTimeout(() => {  
  chartType = CATEGORIESchart[document.querySelector('.select input[type=radio]:checked + label').innerHTML.trim()];
  console.log(JSON.parse(localStorage.getItem(chartType)));

  //Clear previous chart and draw the new one
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
  
  //Clear previous chart and draw the new one
  document.getElementById('jump-graph').innerHTML = "";
  drawChart();
});

//When the date changes, request info from database
startDateInp.addEventListener('change', (event) => {
  dbDate.startDate = startDateInp.value;
  dbDate.endDate = endDateInp.value;
  sio.emit('dbQuery', dbDate);
});
endDateInp.addEventListener('change', (event) => {
  dbDate.startDate = startDateInp.value;
  dbDate.endDate = endDateInp.value;
  sio.emit('dbQuery', dbDate);
});

var intervalId = window.setInterval(function(){
  sio.emit('getData', "any");
}, 5000);

google.charts.load('current', {'packages':['line']});
google.charts.setOnLoadCallback(drawChart);
var chart;


function drawChart() {
  if(chart!=undefined){
    chart.clearChart();
  }
  data = new google.visualization.DataTable();
  data.addColumn('number', 'Jump');
  //Name the second axis according to the type of analysis
  data.addColumn('number', Object.keys(CATEGORIESchart).find(key => CATEGORIESchart[key] === chartType));

  //Add the selected data from the local storage
  data.addRows(JSON.parse(localStorage.getItem(chartType)));

  var options = {
    chart: {
      title: 'Sensors output vs time'
    },
    width: performanceDivWidth*0.9,
    height: 350
  };

  chart = new google.charts.Line(document.getElementById('jump-graph'));
  chart.draw(data, google.charts.Line.convertOptions(options));
}
