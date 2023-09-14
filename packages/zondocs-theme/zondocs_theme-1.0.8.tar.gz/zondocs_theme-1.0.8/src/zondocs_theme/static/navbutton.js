( () => {
    const button = document.querySelector( '#navbutton' );
    const sidebar = document.querySelector( '#sidebar' );
    const mediaQueryList = window.matchMedia( '(min-width: 51.01em)' );
    button.addEventListener( 'click', () => {
        let expanded = button.getAttribute( 'aria-expanded' ) === 'true' || false;
        button.setAttribute( 'aria-expanded', !expanded );
        sidebar.classList.toggle( 'opened' );
    });
    mediaQueryList.addListener( ( mql ) => {
        if ( mql.matches ) {
            sidebar.classList.add( 'opened' );
            button.setAttribute( 'aria-expanded', true );
        } else {
            sidebar.classList.remove( 'opened' );
            button.setAttribute( 'aria-expanded', false );
        }
    });
})();
