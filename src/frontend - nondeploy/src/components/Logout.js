import React, {Component} from 'react';
import Cookies from 'js-cookie';

function Logout() {
    if (window.location.href = "https://smart-study-webapp.herokuapp.com/logout") {
        Cookies.remove("auth_code")
        Cookies.remove("refresh_code")
        Cookies.remove("id_token")
        window.location.replace('https://smart-study-webapp.herokuapp.com/register?callback=https://smart-study-webapp.herokuapp.com/')
    }
}

export default Logout;