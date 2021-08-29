import React from "react";
import axios from "axios";
import Cookies from 'js-cookie';
import "./register-style.css";

const URL = "https://smart-study-webapp.herokuapp.com"

const register = () => {
    async function doRegister() {
        const usernameF = document.getElementById("username").value;
        const emailF = document.getElementById("email").value;
        const passwordF = document.getElementById("password").value;


        const response = await fetch("https://resource-smartstudy.herokuapp.com/register", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                Username: usernameF,
                Password: passwordF,
                Email: emailF
            })
        });

        if (response.status !== 200) {
            const rt = await response.text();
            alert("An error occurred during registration: " + rt);
            return;
        }
        const data = await response.json();
        const access_token = data.access_token;
        const refresh_token = data.refresh_token;
        const id_token = data.id_token;

        Cookies.set('access_token', access_token, { path: '/'});
        Cookies.set('refresh_token', refresh_token, { path: '/'});
        Cookies.set('id_token', id_token, { path: '/'});
        window.location.replace(URL + "/");
    }



    return (
        <div className="body">
            <div className="container align-items-center">
                <div className="register justify-content-center">
                    <h3 className="title" >Register</h3>
                    <div className="content">
                        <div className="form">
                            <div className="form-group">
                                <label htmlFor="username">Username</label>
                                <input type="text" id="username" placeholder="Username" />
                            </div>
                            <div className="form-group">
                                <label htmlFor="email">Email</label>
                                <input type="email" id="email" placeholder="Email" />
                            </div>
                            <div className="form-group">
                                <label htmlFor="password">Password</label>
                                <input type="password" id="password" placeholder="Password" />
                            </div>
                        </div>
                    </div>
                    <div className="footer">
                        <input value="Register"
                            id="registerButton"
                            onClick={doRegister}
                            type="submit"
                            className="btn-grad" />
                        <a href="https://auth-smartstudy.herokuapp.com/login?callback=https://smart-study-webapp.herokuapp.com/status">Login</a>
                    </div>

                </div>
            </div>
        </div>
    );
};

export default register;