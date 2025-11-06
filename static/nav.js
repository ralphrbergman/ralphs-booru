const Anchors = document.getElementById('navbar-anchors');
const MenuToggler = document.getElementById('menu-toggler');

MenuToggler.addEventListener('click', function() {
    const State = Anchors.style.display == '' ? 'none' : '';

    Anchors.style.display = State;
});
