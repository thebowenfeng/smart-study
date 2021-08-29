import React, { Component } from "react";
import {BrowserRouter as Router, Switch, Route} from "react-router-dom";
import axios from 'axios';
import Cookies from 'js-cookie';

import stopWatch from './components/stopWatch';
import Navigator from './components/navBar';
import lineGraph from './components/lineGraph';
import Register from './components/register';
import Logout from './components/Logout';

const URL = "https://smart-study-webapp.herokuapp.com"


export default class App extends Component {
  state = {
    redirect : false
  }
  componentDidMount() {
    let Authcode = Cookies.get("id_token");
    if (Authcode === undefined) {
      console.log("token undefined");
      var url_string = window.location.href;
      if (url_string.startsWith(URL + "/status") || url_string.startsWith(URL + "/register")) {
        const queryParams = new URLSearchParams(window.location.search);
        var auth = queryParams.get('auth_code');
        var json = JSON.stringify({"ClientID": "react", "ClientSecret": "my secret", "AuthCode": auth});
        axios.post(' https://auth-smartstudy.herokuapp.com/get_access_token', json,{
          headers: {
            "Content-Type": "application/json"
          }
        } )
            .then(res => {
              var access_token = res.data["access_token"];
              var refresh_token = res.data["refresh_token"];
              var id_token = res.data["id_token"];

              Cookies.set('access_token', access_token, { path: '/'});
              Cookies.set('refresh_token', refresh_token, { path: '/'});
              Cookies.set('id_token', id_token, { path: '/'});
              window.location.replace(URL)
            })
      }
      else {
        window.location.replace(URL + "/register?callback=" + URL + "/status");
      }
    }
  }
  render() {

    return (
        <Router>
          <Navigator />
          <Switch>
            <Route path="/" exact component={stopWatch} />
            <Route path="/status" component={lineGraph} />
            <Route path="/register" component={Register} />
            <Route path="/logout" component={Logout} />
          </Switch>
        </Router>
    );
  }
}