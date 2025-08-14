function filterName() {
  let input = document.getElementById('search').value.toLowerCase();
  let items = document.getElementsByClassName('carousel-item');
  Array.from(items).forEach((item) => {
    let name = item.getElementsByTagName('h3')[0].innerText.toLowerCase();
    item.style.display = name.includes(input) ? '' : 'none';
  });
}

function filterCategory() {
  let cat = document.getElementById('category').value;
  let items = document.getElementsByClassName('carousel-item');
  Array.from(items).forEach((item) => {
    let itemCat = item.getElementsByTagName('p')[0].innerText;
    item.style.display = !cat || itemCat === cat ? '' : 'none';
  });
}
