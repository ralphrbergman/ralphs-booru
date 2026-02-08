const anchors = document.getElementById('navbar-anchors');
const menuToggler = document.getElementById('menu-toggler');

menuToggler.addEventListener('click', function() {
    const State = anchors.style.display == '' ? 'none' : '';

    anchors.style.display = State;
});
