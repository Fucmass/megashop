// Get the elements
const menuIcon = document.querySelector('.menu-icon');
const navLinks = document.querySelector('#nav-links');

// Add click event listener to toggle the menu
menuIcon.addEventListener('click', () => {
    menuIcon.classList.toggle('active');
    navLinks.classList.toggle('active');
});
