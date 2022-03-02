//Setup websocket
const sio = io.connect('http://localhost:5000');

//Setup local storage for each signal
localStorage.setItem("airTime", JSON.stringify([]))
localStorage.setItem("stiffness", JSON.stringify([]))
localStorage.setItem("totalRot", JSON.stringify([]))
localStorage.setItem("peakRotSpeed", JSON.stringify([]))
localStorage.setItem("toeHeavy", JSON.stringify([]))

//Get width of the parent element of the chart so chart width is responsive
var performanceDivWidth = document.getElementsByClassName('performance-box')[0].offsetWidth;

//Get html elements
const startDateInp = document.getElementById('start-date');
const endDateInp = document.getElementById('end-date');
const chartTypeMenu = document.getElementById('selectSession');
var chartType = "airTime";

//Dictionary of the start and end date the user wants
var dbDate = {
  startDate: startDateInp.value,
  endDate: endDateInp.value
}

//Used to map the selected chart type from front-end menu to the local storage signals
const CATEGORIESchart = {
  'Air Time': 'airTime',
  'Stiffness': 'stiffness',
  'Total Rotation': 'totalRot',
  'Peak Rotational Speed': 'peakRotSpeed',
  'Toe Heavy': 'toeHeavy'
};

//Test signal 
//  var testAirTime = [[1, 10],[2, 12]];
//  localStorage.setItem("airTime", JSON.stringify(testAirTime))
//  var testLandTime = [[1, 3],[2, 1]];
//  localStorage.setItem("stiffness", JSON.stringify(testLandTime))

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
  //Save current local storage in variables
  var storedSignals1 = JSON.parse(localStorage.getItem("airTime"))
  var storedSignals2 = JSON.parse(localStorage.getItem("stiffness"))
  var storedSignals3 = JSON.parse(localStorage.getItem("totalRot"))
  var storedSignals4 = JSON.parse(localStorage.getItem("peakRotSpeed"))
  var storedSignals5 = JSON.parse(localStorage.getItem("toeHeavy"))

  //Push the latest data from back end server into the variables
  storedSignals1.push([storedSignals1.length, data.air_time])
  storedSignals2.push([storedSignals1.length, data.landing_time])
  storedSignals3.push([storedSignals1.length, data.total_rotation])
  storedSignals4.push([storedSignals1.length, data.jump_midpoint])
  //Make the toe heavy boolean into 1 or 0
  var pushToe = data.toe_heavy ? 1:0;
  storedSignals5.push([storedSignals1.length, pushToe])

  //Set the local storage with the new data
  localStorage.setItem("airTime", JSON.stringify(storedSignals1))
  localStorage.setItem("stiffness", JSON.stringify(storedSignals2))
  localStorage.setItem("totalRot", JSON.stringify(storedSignals3))
  localStorage.setItem("peakRotSpeed", JSON.stringify(storedSignals4))
  localStorage.setItem("toeHeavy", JSON.stringify(storedSignals5))
  
  //Clear previous chart and draw the new one
  document.getElementById('jump-graph').innerHTML = "";
  drawChart();
});


//Listen to which chart the user wants
chartTypeMenu.addEventListener('blur', () => setTimeout(() => {  
  //update the chart type
  chartType = CATEGORIESchart[document.querySelector('.select input[type=radio]:checked + label').innerHTML.trim()];

  //Clear previous chart and draw the new one
  document.getElementById('jump-graph').innerHTML = "";
  drawChart();
}, 100));

//Process data from database
sio.on('databaseReturn', function(data){
  console.log(data);
  //Clear local storage before writing to it
  localStorage.clear();

  //Fill the local storage with info from database
  //Database returns a dictionary
  localStorage.setItem("airTime", JSON.stringify(data.air_time_list))
  localStorage.setItem("stiffness", JSON.stringify(data.landing_time_list))
  localStorage.setItem("totalRot", JSON.stringify(data.total_rotation_list))
  localStorage.setItem("peakRotSpeed", JSON.stringify(data.peak_rotation_list))

  //Make the toe heavy booleans into 0 and 1 so they can be used in the chart
  data.toe_heavy_list[1].forEach(function(element){return element ? 1:0});
  localStorage.setItem("toeHeavy", JSON.stringify(data.toe_heavy_list))
  
  //Clear previous chart and draw the new one
  document.getElementById('jump-graph').innerHTML = "";
  drawChart();
});

//When either date changes, request info from database
startDateInp.addEventListener('change', (event) => {
  //Update the dates and send them to back end server
  dbDate.startDate = startDateInp.value;
  dbDate.endDate = endDateInp.value;
  sio.emit('dbQuery', dbDate);
});
endDateInp.addEventListener('change', (event) => {
  //Update the dates and send them to back end server
  dbDate.startDate = startDateInp.value;
  dbDate.endDate = endDateInp.value;
  sio.emit('dbQuery', dbDate);
});

var intervalId = window.setInterval(function(){
  sio.emit('getData', "any");
}, 5000);


//Using Google Charts
google.charts.load('current', {'packages':['line']});
google.charts.setOnLoadCallback(drawChart);
var chart;

function drawChart() {
  if(chart!=undefined){
    //Clearing the chart before drawing a new one
    chart.clearChart();
  }
  data = new google.visualization.DataTable();
  data.addColumn('number', 'Jump');
  //Name the second axis according to the type of analysis
  data.addColumn('number', Object.keys(CATEGORIESchart).find(key => CATEGORIESchart[key] === chartType));

  //Add the selected data from the local storage
  data.addRows(JSON.parse(localStorage.getItem(chartType)));


  //Styling of the chart
  var options = {
    hAxis: {titleTextStyle: {fontSize: 15}},
    vAxis: {title: Object.keys(CATEGORIESchart).find(key => CATEGORIESchart[key] === chartType), titleTextStyle: {fontSize: 15}},
    width: performanceDivWidth*0.9,
    height: 350

  };

  //Draw the chart
  chart = new google.charts.Line(document.getElementById('jump-graph'));
  chart.draw(data, google.charts.Line.convertOptions(options));
}
