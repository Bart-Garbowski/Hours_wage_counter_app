function deleteNote(noteId) {
  fetch("/delete-note", {
    method: "POST",
    body: JSON.stringify({ noteId: noteId }),
  }).then((_res) => {
    window.location.href = "/";
  });
}



function callvalue(){
  var basehours= document.getElementById("basehours").checked;
  var overtimes= document.getElementById("overtimes").checked;
  var holiday= document.getElementById("holiday").checked;
  var sick= document.getElementById("sick").checked;
  var startHours= document.getElementById("startHours").value;
  var hoursWorked= document.getElementById("hoursWorked").value;
  var currentDate= $("#currentDate").text();
  var delete_events= document.getElementById("delete_events").checked;
  console.log(delete_events)
  fetch("/saveday", {
    method: "POST",
    body: JSON.stringify({ currentDate: currentDate, startHours: startHours, hoursWorked: hoursWorked, basehours: basehours, overtimes: overtimes, holiday: holiday, sick: sick, delete_events: delete_events }),
  }).then((_res) => {
    window.location.href = "/info";
  });
}

