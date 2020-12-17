const filePicker = document.getElementById("file-picker");
const fileChosen = document.getElementById("file-chosen");

filePicker.addEventListener("change", function() {
  fileChosen.textContent = this.files[0].name
})
