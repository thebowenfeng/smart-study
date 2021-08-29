import React, { Component } from "react";
import { Link } from "react-router-dom";
import './navBar-style.css'
class navBar extends Component {
    render() {
        return (
            <nav>
                <input type="checkbox" id="check"></input>
                <label for="check" class="checkbtn">
                    <svg
                        xmlns="http://www.w3.org/2000/svg"
                        width="36"
                        height="36"
                        fill="#5cb0a4"
                        class="bi bi-list"
                        viewBox="0 0 16 16"
                    >
                        <path
                            fill-rule="evenodd"
                            d="M2.5 12a.5.5 0 0 1 .5-.5h10a.5.5 0 0 1 0 1H3a.5.5 0 0 1-.5-.5zm0-4a.5.5 0 0 1 .5-.5h10a.5.5 0 0 1 0 1H3a.5.5 0 0 1-.5-.5zm0-4a.5.5 0 0 1 .5-.5h10a.5.5 0 0 1 0 1H3a.5.5 0 0 1-.5-.5z"
                        />
                    </svg>
                </label>

                <label class="logo">
                    <img
                        class="logo-image"
                        src="https://cdn.discordapp.com/attachments/862233859672375338/878473468906192946/smart_study.png"
                        width="90px"
                    ></img>
                    <span className="text-muted">Smart</span>
                    <strong className="bold">Study</strong>
                </label>

                <div className="app-title"></div>

                <ul class="nav-links d-sm-flex justify-content-end">
                    <li className="nav-item">
                        <Link to="/">Home</Link>
                    </li>

                    <li className="nav-item">
                        <Link to="/status">Status</Link>
                    </li>

                    <li className="nav-item">
                        <Link to="/logout">Logout</Link>
                    </li>

                </ul>
            </nav>
        );
    }
}

export default navBar;