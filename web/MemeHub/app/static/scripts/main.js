const current = {
  img: document.querySelector("#current img"),
  title: document.querySelector("#current .img-title")
}
const imgDivs = document.querySelectorAll(".img-container");

imgDivs.forEach(div => div.getElementsByTagName("img")[0].addEventListener("click", imgClick));
sessionStorage.setItem("current", {
  img: current.img.src,
  title: current.title.innerHTML
})

function imgClick(e) {
  const img = e.target
  const title = img.parentNode.getElementsByClassName("img-title")[0]

  // Change current image to src of clicked image
  current.img.src = img.src;
  current.title.innerHTML = title.innerHTML

  current.title.classList.remove("img-title-error");

  sessionStorage.setItem("current", {
    img: current.img.src,
    title: current.title.innerHTML
  })
}
