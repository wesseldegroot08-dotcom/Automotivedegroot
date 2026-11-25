// Klein beetje JavaScript: slepen op het planbord. Zonder JavaScript werkt alles via de formulieren.
(function () {
  var tijdlijn = document.querySelector('.tijdlijn');
  if (!tijdlijn) return;
  var begin = parseInt(tijdlijn.dataset.begin, 10), eind = parseInt(tijdlijn.dataset.eind, 10);
  var totaal = (eind - begin) * 60;
  var gesleept = null;
  document.querySelectorAll('[data-rit-id][draggable="true"]').forEach(function (el) {
    el.addEventListener('dragstart', function (e) {
      gesleept = el.dataset.ritId;
      e.dataTransfer.setData('text/plain', gesleept);
      e.dataTransfer.effectAllowed = 'move';
    });
  });
  tijdlijn.querySelectorAll('.tl-baan[data-rij-id]').forEach(function (baan) {
    baan.addEventListener('dragover', function (e) { e.preventDefault(); baan.classList.add('sleep-over'); });
    baan.addEventListener('dragleave', function () { baan.classList.remove('sleep-over'); });
    baan.addEventListener('drop', function (e) {
      e.preventDefault();
      baan.classList.remove('sleep-over');
      var id = e.dataTransfer.getData('text/plain') || gesleept;
      if (!id) return;
      var r = baan.getBoundingClientRect();
      var minuten = Math.max(0, Math.round((e.clientX - r.left) / r.width * totaal));
      var f = document.getElementById('sleep-formulier');
      f.action = '/planbord/rit/' + id + '/verplaats';
      f.elements.rij_id.value = baan.dataset.rijId;
      f.elements.minuten.value = minuten;
      f.submit();
    });
  });
})();
